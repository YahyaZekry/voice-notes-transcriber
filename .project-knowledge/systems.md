# Systems

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10

| System | Status | Details |
|--------|--------|---------|
| Transcription engine | Live | faster-whisper `large-v3`, CPU + int8, lazy model load (~19s cold from cache; ~3.8 GB resident while loaded). `vad_filter=True`, auto language detect. |
| File watching | Live | watchdog `Observer`, `recursive=False`, scans existing files at startup then watches `on_created`/`on_moved`. Size-stability check (2 checks / 2s apart) avoids mid-write files. |
| Service / boot | Live | systemd --user `voice-transcriber.service`, `Restart=on-failure`, `WantedBy=default.target` (starts at login). Idles at ~20 MB; model unloaded until first note. |
| Model download | Live | HuggingFace hub, unauthenticated (~3 GB cache at `~/.cache/huggingface/`). |
