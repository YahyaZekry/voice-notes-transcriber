# Systems

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10

| System | Status | Details |
|--------|--------|---------|
| Transcription engine | Live | faster-whisper `large-v3`, CPU + int8, lazy model load (~19s cold from cache; ~3.8 GB resident while loaded). `vad_filter=True`, auto language detect, `word_timestamps=True` (needed for speaker-word assignment). |
| Speaker diarization | Live | pyannote `speaker-diarization-3.1` (gated models, needs `HF_TOKEN`). Audio decoded to 16 kHz mono via PyAV (bypasses broken torchcodec) and fed as a waveform dict. Auto speaker count with a probe fallback: if auto returns 1 speaker on ≥10s of speech, re-run with `num_speakers=2` and accept only when the minority voice ≥10% of speech AND ≥4s (catches dominance-collapse; avoids splitting monologues). Labels added only when >1 distinct voice. Falls back to plain transcript on any failure. |
| File watching | Live | watchdog `Observer`, `recursive=False`, scans existing files at startup then watches `on_created`/`on_moved`. Only direct children of the root are processed (subdir events like `Completed/` are ignored). Stability gate: file must be idle (mtime age ≥ 5s) AND size unchanged across polls, up to 10 min (protects against mid-write files, e.g. an active screen recording). |
| Notifications | Live | `notify()` helper → `notify-send` (fallback `kdialog --passivepopup`), never raises. Fires on: found voice note, skipped (still writing), transcription failed, could not write note, and transcription complete (with duration + language). Toggle with `TRANSCRIBER_NOTIFY=0`. |
| Service / boot | Live | systemd --user `voice-transcriber.service`, `Restart=on-failure`, `WantedBy=default.target` (starts at login). Idles at ~20 MB; model unloaded until first note. |
| Model download | Live | HuggingFace hub, unauthenticated (~3 GB cache at `~/.cache/huggingface/`). |
