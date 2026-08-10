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
import subprocess
import sys
import time
from bisect import bisect_right
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

VOICE_DIR = Path("/mnt/knowledge/Obsidian/Personal/VoiceNotes")
COMPLETED_DIR = VOICE_DIR / "Completed"
OUTPUT_DIR = VOICE_DIR / "Transcriptions"
EXTENSIONS = {
    ".mp3", ".m4a", ".ogg", ".opus", ".wav", ".flac", ".aac",
    ".webm", ".mp4", ".mkv", ".mov", ".avi", ".m4v", ".ts", ".3gp",
}
MODEL_NAME = os.environ.get("TRANSCRIBER_MODEL", "large-v3")
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
SCAN_INTERVAL = 5.0
MIN_AGE = 5.0
STABILITY_DELAY = 2.0
MAX_WAIT = 600.0
NOTIFY_ENABLED = os.environ.get("TRANSCRIBER_NOTIFY", "1") != "0"
DIARIZE = os.environ.get("TRANSCRIBER_DIARIZE", "1") != "0"
SPEAKERS = os.environ.get("TRANSCRIBER_SPEAKERS", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

log = logging.getLogger("voice-transcriber")


def notify(title: str, message: str) -> None:
    if not NOTIFY_ENABLED:
        return
    try:
        if shutil.which("notify-send"):
            subprocess.run(
                ["notify-send", "-a", "Voice Transcriber", title, message],
                check=False,
            )
        elif shutil.which("kdialog"):
            subprocess.run(
                ["kdialog", "--title", "Voice Transcriber", "--passivepopup", message, "8"],
                check=False,
            )
    except Exception:
        log.debug("Notification failed", exc_info=True)


def is_audio(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in EXTENSIONS


class Transcriber:
    def __init__(self):
        self.model = None
        self.diarization = None

    def _get_model(self):
        if self.model is None:
            log.info("Loading Whisper model %s (first run downloads it)...", MODEL_NAME)
            from faster_whisper import WhisperModel

            self.model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)
            log.info("Model ready.")
        return self.model

    def _get_diarization(self):
        if self.diarization is None:
            log.info("Loading speaker-diarization pipeline...")
            from pyannote.audio import Pipeline

            self.diarization = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=HF_TOKEN or None,
            )
            log.info("Diarization ready.")
        return self.diarization

    def _stable(self, path: Path) -> bool:
        deadline = time.time() + MAX_WAIT
        prev = -1
        while time.time() < deadline:
            if not path.exists():
                return False
            st = path.stat()
            too_young = time.time() - st.st_mtime < MIN_AGE
            if too_young or st.st_size != prev:
                prev = st.st_size
                time.sleep(STABILITY_DELAY)
                continue
            return True
        return False

    def transcribe(self, path: Path) -> tuple[str, str, float, int]:
        model = self._get_model()
        segments, info = model.transcribe(
            str(path),
            language=None,  # auto-detect ar / en per note
            task="transcribe",
            vad_filter=True,
            word_timestamps=True,
        )
        seg_list = list(segments)
        text = "".join(seg.text for seg in seg_list).strip()
        speakers = 0
        if DIARIZE and text:
            num_speakers = int(SPEAKERS) if SPEAKERS.isdigit() else None
            try:
                turns = self._diarize(path, num_speakers=num_speakers)
                distinct = {t[2] for t in turns}
                if len(distinct) > 1:
                    labeled, speakers = self._diarize_text(seg_list, turns)
                    if speakers:
                        text = labeled
            except Exception:
                log.exception("Diarization failed — using plain transcript")
        return text, info.language, info.duration, speakers

    def _diarize(
        self, path: Path, num_speakers: int | None = None
    ) -> list[tuple[float, float, str]]:
        pipeline = self._get_diarization()
        waveform = self._load_waveform(path)
        kwargs = {"num_speakers": num_speakers} if num_speakers else {}
        output = pipeline(
            {"waveform": waveform.unsqueeze(0), "sample_rate": 16000},
            **kwargs,
        )
        diarization = getattr(output, "speaker_diarization", output)
        return [
            (turn.start, turn.end, speaker)
            for turn, _, speaker in diarization.itertracks(yield_label=True)
        ]

    def _load_waveform(self, path: Path):
        import numpy as np
        import torch

        import av

        container = av.open(str(path))
        stream = next(s for s in container.streams if s.type == "audio")
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=16000)
        frames = []
        for frame in container.decode(stream):
            for resampled in resampler.resample(frame):
                frames.append(resampled.to_ndarray())
        for resampled in resampler.resample(None):
            frames.append(resampled.to_ndarray())
        audio = (
            np.concatenate(frames, axis=1).ravel() if frames else np.zeros(0, np.float32)
        )
        return torch.from_numpy(audio).float()

    def _diarize_text(
        self, segments, turns: list[tuple[float, float, str]]
    ) -> tuple[str, int]:
        turns = sorted(turns, key=lambda t: t[0])
        starts = [t[0] for t in turns]
        word_items = [
            (w.start, w.end, w.word)
            for s in segments
            for w in s.words
        ]
        grouped: dict[int, list[str]] = {}
        for ws, _, wt in word_items:
            i = bisect_right(starts, ws) - 1
            if 0 <= i < len(turns):
                grouped.setdefault(i, []).append(wt)

        speaker_name: dict[str, str] = {}
        lines: list[str] = []
        buffer: list[str] = []
        prev_label: str | None = None
        for i, t in enumerate(turns):
            spk = t[2]
            if spk not in speaker_name:
                speaker_name[spk] = f"Speaker {len(speaker_name) + 1}"
            label = speaker_name[spk]
            chunk = "".join(grouped.get(i, [])).strip()
            if not chunk:
                continue
            if label == prev_label:
                buffer.append(chunk)
            else:
                if buffer:
                    lines.append(f"**{prev_label}:** {' '.join(buffer)}")
                buffer = [chunk]
            prev_label = label
        if buffer:
            lines.append(f"**{prev_label}:** {' '.join(buffer)}")

        text = "\n\n".join(lines)
        if text and len(speaker_name) > 1:
            return text, len(speaker_name)
        return text, 0

    def write_note(self, path: Path, text: str, language: str, duration: float, speakers: int = 0) -> Path:
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
            + (f"speakers: {speakers}\n" if speakers else "")
            + "---\n\n"
            "# " + title + "\n\n" + text.rstrip() + "\n"
        )
        note.write_text(content, encoding="utf-8")
        return note

    def process(self, path: Path) -> bool:
        if not is_audio(path):
            return False
        log.info("Processing %s ...", path.name)
        notify("Found voice note", path.name)
        if not self._stable(path):
            log.warning("Skipping %s (kept changing)", path.name)
            notify("Skipped", f"{path.name} was still being written")
            return False
        try:
            text, language, duration, speakers = self.transcribe(path)
        except Exception:
            log.exception("Transcription failed for %s", path.name)
            notify("Transcription failed", path.name)
            return False
        if not text:
            log.warning("No speech detected in %s — moving on without a note", path.name)
        try:
            note = self.write_note(path, text, language, duration, speakers)
        except Exception:
            log.exception("Could not write note for %s", path.name)
            notify("Could not write note", path.name)
            return False
        COMPLETED_DIR.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(path), COMPLETED_DIR / path.name)
        except Exception:
            log.exception("Could not move %s to Completed/", path.name)
        mins, secs = int(duration // 60), int(duration % 60)
        log.info(
            "Wrote %s (lang=%s, %ds%s)",
            note.name,
            language,
            int(duration),
            f", {speakers} speakers" if speakers else "",
        )
        notify(
            "Transcription complete",
            f"{path.name} → {note.name} ({mins}:{secs:02d}, {language}"
            + (f", {speakers} speakers)" if speakers else ")"),
        )
        return True


class WatchHandler(FileSystemEventHandler):
    def __init__(self, transcriber: Transcriber):
        self.transcriber = transcriber
        self.scheduled = set()

    def _schedule(self, path: Path):
        if not is_audio(path):
            return
        if path.parent != VOICE_DIR:
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
