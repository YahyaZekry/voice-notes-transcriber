# Voice Notes Transcriber

Local, private Whisper transcription for Obsidian voice notes.

Watches `VoiceNotes/`, transcribes new recordings **on this machine** (no cloud) with Whisper `large-v3` — Arabic + English auto-detected — labels speakers with pyannote diarization, writes a Markdown note with YAML frontmatter into `VoiceNotes/Transcriptions/`, then moves the audio to `VoiceNotes/Completed/`. Desktop toast on found / failed / complete.

Runs on the NVIDIA GPU (CUDA, float16).

## What it does

- Watches `/mnt/knowledge/Obsidian/Personal/VoiceNotes/` for new audio/video files
- Lazy-loads the model (loads on the first note, not at startup)
- Auto-detects language (Arabic / English / others), VAD filter, word-level timestamps
- Speaker diarization when >1 distinct voice (labels `**Speaker 1:**`/`**Speaker 2:**` turns)
- Writes a note like `2026-08-11 1638 - 03 ...md` into `Transcriptions/`
- Moves the source file to `Completed/`
- systemd user service with auto-restart and login start

## Requirements

- Python 3.12 (the system Python 3.14 is too new for faster-whisper — use `uv`)
- NVIDIA GPU with a working driver (tested: RTX 3050, 8 GB)
- `ffmpeg` on PATH (audio decode, incl. the audio track of video files)

## Setup

### 1. Create the venv

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python faster-whisper watchdog
```

For CUDA support you also need the GPU torch build and a CUDA-enabled ctranslate2.
Install the torch wheel with **pip** (not uv — uv's HTTP client times out on
`pypi.nvidia.com`):

```bash
.venv/bin/python -m pip install torch==2.13.0+cu129 --index-url https://download.pytorch.org/whl/cu129
```

ctranslate2 ships only CPU wheels on PyPI, so build the CUDA version from source
(see `docs/` / git history of this repo for the CUDA 13.3 + gcc-16 recipe used here).

> Runtime note: the service unit sets `LD_LIBRARY_PATH` to the local CUDA build
> dirs — `.ct2-cuda/lib` and `.cuda13/lib64` (gitignored, machine-specific).

### 2. Download the models

```bash
./download_models.sh
```

This fetches the Whisper model (public) plus the four gated pyannote models into
`~/.cache/huggingface/` so the service runs offline afterwards. Already-cached
repos are skipped.

Use a smaller model with `./download_models.sh --model small` (also works via
`TRANSCRIBER_MODEL` at runtime).

### 3. HuggingFace token (for diarization only)

The pyannote models are **gated**:

1. Create a token at https://huggingface.co/settings/tokens (read scope is enough)
2. Log in and accept the license on each of:
   - `pyannote/speaker-diarization-3.1`
   - `pyannote/segmentation-3.0`
   - `pyannote/speaker-diarization-community-1`
   - `pyannote/wespeaker-voxceleb-resnet34-LM`
3. Save it:

```bash
install -m 600 /dev/null ~/.config/voice-transcriber/hf.env
echo 'HF_TOKEN=hf_...' >> ~/.config/voice-transcriber/hf.env
```

Diarization is optional — the transcriber still works without the token (plain
transcript, no speaker labels).

### 4. Install the service

```bash
systemctl --user daemon-reload
systemctl --user enable --now voice-transcriber.service
```

## Usage

Drop a recording (`.ogg .m4a .mp3 .wav .flac .aac .opus .mp4 .mkv ...`) into the
watch folder. The note appears in `Transcriptions/` and the file moves to
`Completed/`.

Manual runs:

```bash
.venv/bin/python transcriber.py            # watch mode (foreground)
.venv/bin/python transcriber.py --once     # process files already in the folder, exit
```

## Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `TRANSCRIBER_MODEL` | `large-v3` | faster-whisper model |
| `TRANSCRIBER_NOTIFY` | `1` | `0` disables desktop notifications |
| `TRANSCRIBER_DIARIZE` | `1` | `0` disables speaker diarization |
| `TRANSCRIBER_SPEAKERS` | empty | force speaker count (e.g. `2`); empty = auto |

Set them in the systemd unit (`Environment=...`) or as `EnvironmentFile` lines.

## Output format

```markdown
---
type: voice-note
created: 2026-08-11T16:38:19
source: 03 ....ogg
duration: 15:10
language: ar
speakers: 3
---

# 2026-08-11 1638 - 03 ...

**Speaker 1:** ...
**Speaker 2:** ...
```

## Troubleshooting

- **CUDA out of memory** — whisper float16 needs ~3.2 GB; pyannote adds ~1.5 GB.
  The service frees pyannote to CPU after each note so the next whisper run has
  headroom. If your GPU is smaller, lower the desktop VRAM use or disable
  diarization (`TRANSCRIBER_DIARIZE=0`).
- **`torchcodec` import warning / error** — known-broken on this system; the
  service bypasses it by decoding audio to a 16 kHz waveform via PyAV. Safe to
  ignore.
- **`pypi.nvidia.com` timeout with uv** — use `python -m pip` for CUDA/nvidia
  wheels (uv's HTTP client times out there; pip and curl work).
- **Whisper model still downloads at runtime** — run `./download_models.sh` first.
- **gcc too new for nvcc** — CUDA 13.3 nvcc accepts gcc 16 with
  `-allow-unsupported-compiler` (used in the ctranslate2 build); CUDA 12.9 cannot.

## Notes / known limitations

- Rapid-fire Q&A (0.3–1s interjections) under a dominant voice collapses into one
  speaker — a verified pyannote model limit; long utterances label correctly.
- Files renamed while mid-transcription break that run (note keeps the old name;
  restart the service to re-process).
- `speed`, `--help` and other extras live in the git history / `.project-knowledge/`.

---

<details>
<summary>🧠 AI Context</summary>

This project uses the [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) skill to maintain a `.project-knowledge/` folder — a living, AI-readable map of the codebase. Every AI session loads only the files relevant to the current task instead of scanning from scratch.

Built by [Yahya Zekry](https://github.com/YahyaZekry/claude-code-skills).

</details>
