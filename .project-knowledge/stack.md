# Stack

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-11

## Tech Stack

| Category | Details |
|----------|---------|
| Language | Python 3.12.13 (pinned via uv; system Python is 3.14 — too new for faster-whisper) |
| Runtime | local venv at `.venv/` |
| Framework | none (standalone script) |
| Transcription | `faster-whisper` — Whisper `large-v3` (multilingual), `device=cuda`, `compute_type=float16` (since 2026-08-11; was CPU/int8) |
| File watching | `watchdog` 6.0.0 |
| Audio decode | system `ffmpeg` (n9.0) via faster-whisper (also decodes audio track of video files) |
| Speaker diarization | `pyannote.audio` (speaker-diarization-3.1) + torch CUDA; audio fed as waveform via PyAV (torchcodec is broken on this system and bypassed); pipeline moved back to CPU after each note to free VRAM |
| GPU / CUDA | NVIDIA GeForce RTX 3050 (8 GB), driver 610.57, CUDA UMD 13.3; torch `2.13.0+cu129` (CUDA 12.9 build); ctranslate2 4.8.1 built from source with CUDA 13.3 |
| Notifications | `notify-send` (libnotify / org.freedesktop.Notifications), `kdialog` fallback |
| Process mgmt | systemd --user unit `voice-transcriber.service` |
| Package mgmt | `uv` (user-level at `~/.local/bin/uv`) — **but use `python -m pip` for CUDA/nvidia wheels** (uv's HTTP client times out on `pypi.nvidia.com`; pip & curl work) |
| Version control | git (repo initialized `c6a5ea6`, branch `main`) |

---

## Dev Commands

| Command | What It Does |
|---------|-------------|
| `systemctl --user status voice-transcriber.service` | Check service status |
| `systemctl --user restart voice-transcriber.service` | Restart watcher |
| `systemctl --user stop voice-transcriber.service` | Stop watcher |
| `.venv/bin/python transcriber.py` | Run in watch mode (foreground) |
| `.venv/bin/python transcriber.py --once` | Process files already in the folder, then exit |
| `TRANSCRIBER_MODEL=small .venv/bin/python transcriber.py --once` | Override model (default `large-v3`) |
| `uv pip install --python .venv/bin/python faster-whisper watchdog` | Reinstall deps in a fresh venv |
| `uv venv --python 3.12 .venv` | Recreate the venv (path-bound) |
| `python -m pip install torch==2.13.0+cu129 --index-url https://download.pytorch.org/whl/cu129` | Install CUDA torch (pip, not uv — see note above) |
| `python -m pip install dist/ctranslate2-*.whl` | Install a locally-built ctranslate2 wheel |
| `systemctl --user cat voice-transcriber.service` | Show the unit incl. `LD_LIBRARY_PATH` for GPU libs |

---

## Environment Variables

| Variable | Used In | What It Enables |
|----------|---------|----------------|
| `TRANSCRIBER_WATCH_DIR` | `transcriber.py` config | Watch folder (default `~/VoiceNotes`; this deployment pins `/mnt/knowledge/Obsidian/Personal/VoiceNotes` in the systemd unit) |
| `TRANSCRIBER_MODEL` | `transcriber.py` config | Overrides `MODEL_NAME` (default `large-v3`) |
| `TRANSCRIBER_NOTIFY` | `transcriber.py` config | `0` disables desktop notifications (default enabled) |
| `TRANSCRIBER_DIARIZE` | `transcriber.py` config | `0` disables speaker diarization (default enabled) |
| `TRANSCRIBER_SPEAKERS` | `transcriber.py` config | Force speaker count (e.g. `2`) when pyannote undercounts; empty = auto |
| `HF_TOKEN` | service `EnvironmentFile` | `~/.config/voice-transcriber/hf.env` (`0600`); needed to download gated pyannote models |
| `PATH` | systemd unit | `/usr/bin:/bin:~/.local/bin` (ffmpeg + uv) |
| `LD_LIBRARY_PATH` | systemd unit (Environment) | `<repo>/.ct2-cuda/lib:<repo>/.cuda13/lib64` — CUDA ctranslate2 + CUDA 13.3 runtime libs (cudart13, cublas13, cudnn9, curand10) |
