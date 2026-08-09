# Features & Workflows

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10

## Features

- **Auto-transcribe voice notes** — drop any audio into `VoiceNotes/` and a `.md` note appears in `Transcriptions/`, audio moves to `Completed/`. *(added: 2026-08-10)*
- **Bilingual support** — Whisper `large-v3` auto-detects Arabic and English per note. *(added: 2026-08-10)*
- **Supported formats** — `.mp3 .m4a .ogg .opus .wav .flac .aac .webm`. *(added: 2026-08-10)*
- **Startup catch-up** — audio already in the folder is processed on service start, not just new drops. *(added: 2026-08-10)*
- **Manual mode** — `--once` flag processes existing files without running the watcher. *(added: 2026-08-10)*

---

## Workflows

**Voice note → Obsidian note**
1. User drops/records audio into `/mnt/knowledge/Obsidian/Personal/VoiceNotes/`
2. watchdog fires `on_created`/`on_moved` → `WatchHandler._schedule`
3. `Transcriber.process` waits for stable file size (2 × 2s)
4. Lazy-loads `large-v3` (if not resident) → transcribes with VAD + auto language
5. `write_note` writes `Transcriptions/YYYY-MM-DD HHMM - stem.md` with frontmatter
6. Audio moved to `VoiceNotes/Completed/`
