#!/usr/bin/env python3
"""Watch an Obsidian VoiceNotes folder, transcribe new voice notes locally
with faster-whisper (multilingual — Arabic + English auto-detected), write a
Markdown note into VoiceNotes/Transcriptions/, then move the audio to
VoiceNotes/Completed/.

Usage:
    python transcriber.py            # watch mode (default)
    python transcriber.py --once     # process existing files and exit
"""

import argparse
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

VOICE_DIR = Path("/mnt/knowledge/Obsidian/Personal/VoiceNotes")
COMPLETED_DIR = VOICE_DIR / "Completed"
OUTPUT_DIR = VOICE_DIR / "Transcriptions"
EXTENSIONS = {".mp3", ".m4a", ".ogg", ".opus", ".wav", ".flac", ".aac", ".webm"}
MODEL_NAME = os.environ.get("TRANSCRIBER_MODEL", "large-v3")
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
SCAN_INTERVAL = 5.0
STABILITY_CHECKS = 2
STABILITY_DELAY = 2.0

log = logging.getLogger("voice-transcriber")


def is_audio(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in EXTENSIONS


class Transcriber:
    def __init__(self):
        self.model = None

    def _get_model(self):
        if self.model is None:
            log.info("Loading Whisper model %s (first run downloads it)...", MODEL_NAME)
            from faster_whisper import WhisperModel

            self.model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)
            log.info("Model ready.")
        return self.model

    def _stable(self, path: Path) -> bool:
        prev = -1
        for _ in range(STABILITY_CHECKS):
            if not path.exists():
                return False
            size = path.stat().st_size
            if size == prev:
                return True
            prev = size
            time.sleep(STABILITY_DELAY)
        return True

    def transcribe(self, path: Path) -> tuple[str, str, float]:
        model = self._get_model()
        segments, info = model.transcribe(
            str(path),
            language=None,  # auto-detect ar / en per note
            task="transcribe",
            vad_filter=True,
        )
        text = "".join(seg.text for seg in segments).strip()
        return text, info.language, info.duration

    def write_note(self, path: Path, text: str, language: str, duration: float) -> Path:
        now = datetime.now()
        stamp = now.strftime("%Y-%m-%d %H%M")
        safe_stem = "".join(c for c in path.stem if c not in '/\\:*?"<>|').strip() or "note"
        title = f"{stamp} - {safe_stem}"
        note = OUTPUT_DIR / f"{title}.md"
        mins, secs = int(duration // 60), int(duration % 60)
        content = (
            "---\n"
            "type: voice-note\n"
            f"created: {now.isoformat(timespec='seconds')}\n"
            f"source: {path.name}\n"
            f"duration: {mins}:{secs:02d}\n"
            f"language: {language}\n"
            "---\n\n"
            "# " + title + "\n\n" + text.rstrip() + "\n"
        )
        note.write_text(content, encoding="utf-8")
        return note

    def process(self, path: Path) -> bool:
        if not is_audio(path):
            return False
        log.info("Processing %s ...", path.name)
        if not self._stable(path):
            log.warning("Skipping %s (kept changing)", path.name)
            return False
        try:
            text, language, duration = self.transcribe(path)
        except Exception:
            log.exception("Transcription failed for %s", path.name)
            return False
        if not text:
            log.warning("No speech detected in %s — moving on without a note", path.name)
        try:
            note = self.write_note(path, text, language, duration)
        except Exception:
            log.exception("Could not write note for %s", path.name)
            return False
        COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(path), COMPLETED_DIR / path.name)
        except Exception:
            log.exception("Could not move %s to Completed/", path.name)
        log.info("Wrote %s (lang=%s, %ds)", note.name, language, int(duration))
        return True


class WatchHandler(FileSystemEventHandler):
    def __init__(self, transcriber: Transcriber):
        self.transcriber = transcriber
        self.scheduled = set()

    def _schedule(self, path: Path):
        if not is_audio(path):
            return
        if path in self.scheduled:
            return
        self.scheduled.add(path)
        try:
            self.transcriber.process(path)
        finally:
            self.scheduled.discard(path)

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self._schedule(Path(event.dest_path))


def scan_existing(transcriber: Transcriber):
    for path in sorted(VOICE_DIR.iterdir()):
        if path.is_file():
            transcriber.process(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="process existing files and exit")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    for d in (VOICE_DIR, COMPLETED_DIR, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    transcriber = Transcriber()

    if args.once:
        scan_existing(transcriber)
        return

    log.info("Watching %s for new voice notes...", VOICE_DIR)
    scan_existing(transcriber)
    handler = WatchHandler(transcriber)
    observer = Observer()
    observer.schedule(handler, str(VOICE_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    sys.exit(main())
