# External Integrations & Data Contracts

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-11

## Obsidian Vault (read/write)

- Watches: `/mnt/knowledge/Obsidian/Personal/VoiceNotes/` (audio in, any extension in `EXTENSIONS`)
- Writes: `/mnt/knowledge/Obsidian/Personal/VoiceNotes/Transcriptions/<title>.md` — see `schema.md`
- Moves to: `/mnt/knowledge/Obsidian/Personal/VoiceNotes/Completed/`
- Vault root: `/mnt/knowledge/Obsidian/Personal/`

## systemd --user (runs the watcher)

- Unit: `~/.config/systemd/user/voice-transcriber.service`
- ExecStart: `.venv/bin/python transcriber.py` (absolute paths to this project dir)
- `Environment=LD_LIBRARY_PATH=/mnt/airfryer/Projects/AI/voice-notes-transcriber/.ct2-cuda/lib:/mnt/airfryer/Projects/AI/voice-notes-transcriber/.cuda13/lib64` — required for the CUDA ctranslate2 + CUDA 13.3 runtime libs
- `After/Wants=network-online.target` (model download may need network); auto-starts at login via `default.target.wants`

## Local CUDA toolkits (machine-specific, gitignored)

- `<repo>/.cuda13/` — working CUDA 13.3 toolkit assembled from NVIDIA ubuntu2404 debs (`nvcc` 13.3.73 + ptxas + nvvm, headers, cudart13/cublas13/cudnn9/curand10 runtime libs in `lib64/`). Used to build ctranslate2 AND at runtime via `LD_LIBRARY_PATH`.
- `<repo>/.cuda12/` — abandoned CUDA 12.9 toolkit (nvcc 12.9 cannot parse gcc 16 headers).
- `<repo>/.ct2-cuda/` — installed CUDA-enabled ctranslate2 4.8.1 (`libctranslate2.so`), built from source (git clone `v4.8.1` + submodules, `WITH_CUDA=ON WITH_CUDNN=ON`, `CUDA_NVCC_FLAGS=-allow-unsupported-compiler`, `CUDA_ARCH_LIST=8.6`, cmake 3.31 via pip).

## KDE desktop notifications (outbound)

- `notify-send` (org.freedesktop.Notifications DBus) works from the systemd --user context; `kdialog --passivepopup` is the fallback.
- Caveat: KDE's screen recorder (Meta+Shift+R) saves to the currently-focused folder — a recording dropped into `VoiceNotes/` WILL be treated as a video voice note. The stability gate (min age 5s) prevents reading it mid-recording.

## HuggingFace Hub (model downloads)

- All models cached at `~/.cache/huggingface/hub/`: `models--Systran--faster-whisper-large-v3` (+ `-tiny`), `models--pyannote--speaker-diarization-3.1`, `models--pyannote--segmentation-3.0`, `models--pyannote--speaker-diarization-community-1`, `models--pyannote--wespeaker-voxceleb-resnet34-LM`.
- Whisper is public; the four pyannote repos are **gated** — need `HF_TOKEN` from `~/.config/voice-transcriber/hf.env` (0600, loaded via `EnvironmentFile`). Licenses must be accepted on HF first (Company/Website fields are informational).
- `./download_models.sh` pre-downloads everything (idempotent); the service is fully offline after first download.
