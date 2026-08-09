# Project Structure

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10

## File Tree

```
/mnt/airfryer/Projects/AI/voice-notes-transcriber/
├── .gitignore            # ignores .venv/, __pycache__
├── transcriber.py        # the entire app (config + logic, ~190 lines)
├── .venv/                # Python 3.12.13 venv (faster-whisper, watchdog)
└── .project-knowledge/   # this folder
```

## Key Files

| File | Purpose |
|------|---------|
| `transcriber.py` | Single-file app: config constants at top, `Transcriber` class (model load, stability check, transcribe, write note, move to Completed), `WatchHandler`, `scan_existing`, `main()` |
| `~/.config/systemd/user/voice-transcriber.service` | Systemd --user unit running the watcher; auto-starts at login |
