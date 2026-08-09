# History

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10
> Past-only. Append-only — never delete entries.

## Removed

- ~~Old home `~/voice-notes-transcriber/`~~ — project moved to `/mnt/airfryer/Projects/AI/voice-notes-transcriber/`; venv recreated (venvs are path-bound) *(removed: 2026-08-10)*

---

## Fixed

- Watch mode ignored files already present when the service started → added `scan_existing()` before starting the observer *(fixed: 2026-08-10)*
- venv broke after the directory move → recreated with `uv venv --python 3.12` + reinstall *(fixed: 2026-08-10)*

---

## Decisions

- **Model choice: `large-v3` local over Groq** — user's rule: if the remote option runs the same model, prefer local. Both are Whisper `large-v3`; local via faster-whisper. `large-v3` (multilingual) chosen over English-only `distil-large-v3` for Arabic. *(2026-08-10)*
- **CPU only** — faster-whisper/CTranslate2 has no ROCm/Vulkan path for the AMD GPU; `int8` on CPU (8 cores) is the practical setup. *(2026-08-10)*
- **Python 3.12 via uv** — system Python 3.14 too new for faster-whisper; pinned 3.12.13 in a venv managed by `uv`. *(2026-08-10)*
- **Watch mode + systemd --user** — auto-start at login, no sudo needed; lazy model load keeps idle RAM at ~20 MB. *(2026-08-10)*
- **Lazy model load** — model loads on first note, not at service start, to avoid pinning ~3.8 GB RAM permanently. *(2026-08-10)*
