# Features & Workflows

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10

## Features

- **Auto-transcribe voice notes** — drop any audio or video into `VoiceNotes/` and a `.md` note appears in `Transcriptions/`, the file moves to `Completed/`. *(added: 2026-08-10)*
- **Bilingual support** — Whisper `large-v3` auto-detects Arabic and English per note. *(added: 2026-08-10)*
- **Speaker diarization** — when >1 distinct voice is detected, notes label turns as `**Speaker 1:**` / `**Speaker 2:**` (voice-identity based; auto speaker count, `TRANSCRIBER_SPEAKERS=N` to force). *(added: 2026-08-10)*
- **Supported formats** — audio: `.mp3 .m4a .ogg .opus .wav .flac .aac`; video (audio track transcribed): `.webm .mp4 .mkv .mov .avi .m4v .ts .3gp`. *(added: 2026-08-10)*
- **Desktop notifications** — toast on found, skipped, failed, and complete (with duration + language); toggle `TRANSCRIBER_NOTIFY=0`. *(added: 2026-08-10)*
- **Startup catch-up** — audio already in the folder is processed on service start, not just new drops. *(added: 2026-08-10)*
- **Manual mode** — `--once` flag processes existing files without running the watcher. *(added: 2026-08-10)*

---

## Workflows

**Voice note / video → Obsidian note**
1. User drops/records audio or video into `/mnt/knowledge/Obsidian/Personal/VoiceNotes/`
2. watchdog fires `on_created`/`on_moved` → `WatchHandler._schedule` (direct children only)
3. `Transcriber.process` waits for the file to be stable (mtime age ≥ 5s, size unchanged)
4. Lazy-loads `large-v3` (if not resident) → transcribes with VAD + auto language + word timestamps
5. Runs pyannote diarization (auto speaker count) if enabled; if >1 voice, words are grouped into `**Speaker N:**` turns
6. `write_note` writes `Transcriptions/YYYY-MM-DD HHMM - stem.md` with frontmatter
7. File moved to `VoiceNotes/Completed/`; success/failure toast fired along the way
