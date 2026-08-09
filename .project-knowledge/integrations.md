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

## HuggingFace Hub (one-time model download)

- Downloads `Systran/faster-whisper-large-v3` to `~/.cache/huggingface/` (~3 GB), unauthenticated (slower rate limits — download took ~2h at ~250 KB/s)
- Model is cached; no network needed after first download
