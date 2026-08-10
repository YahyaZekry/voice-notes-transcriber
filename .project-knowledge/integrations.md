# External Integrations & Data Contracts

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10

## Obsidian Vault (read/write)

- Watches: `/mnt/knowledge/Obsidian/Personal/VoiceNotes/` (audio in, any extension in `EXTENSIONS`)
- Writes: `/mnt/knowledge/Obsidian/Personal/VoiceNotes/Transcriptions/<title>.md` — see `schema.md`
- Moves to: `/mnt/knowledge/Obsidian/Personal/VoiceNotes/Completed/`
- Vault root: `/mnt/knowledge/Obsidian/Personal/`

## systemd --user (runs the watcher)

- Unit: `~/.config/systemd/user/voice-transcriber.service`
- ExecStart: `.venv/bin/python transcriber.py` (absolute paths to this project dir)
- `After/Wants=network-online.target` (model download may need network); auto-starts at login via `default.target.wants`

## KDE desktop notifications (outbound)

- `notify-send` (org.freedesktop.Notifications DBus) works from the systemd --user context; `kdialog --passivepopup` is the fallback.
- Caveat: KDE's screen recorder (Meta+Shift+R) saves to the currently-focused folder — a recording dropped into `VoiceNotes/` WILL be treated as a video voice note. The stability gate (min age 5s) prevents reading it mid-recording.

## HuggingFace Hub (model downloads)

- Whisper `large-v3`: `~/.cache/huggingface/` (~3 GB), unauthenticated.
- pyannote diarization models (`pyannote/speaker-diarization-3.1`, `pyannote/segmentation-3.0`, `pyannote/speaker-diarization-community-1`) are **gated** — need `HF_TOKEN` from `~/.config/voice-transcriber/hf.env` (0600, loaded into the service via `EnvironmentFile`). Licenses must be accepted on HF first (Company/Website fields are informational).
- Model is cached; no network needed after first download.
