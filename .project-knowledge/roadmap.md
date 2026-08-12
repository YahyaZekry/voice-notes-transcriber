# Roadmap

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-11
> Forward-looking only. Check this before starting any task — know what's in flight.

## Current Goal

In production on **GPU** (CUDA/float16) since 2026-08-11. Validated on a real batch: 4 Arabic voice notes (Joker/Jung analysis, Devouring Mother, Camus/Absurd, Meursault) transcribed with diarization (2–3 speakers) — 3+5+15+18 min files, all done. Watch mode live; nothing urgent in flight.

---

## Known Bugs

- None known. (Testing artifact only: `--once` with an empty folder exits silently without loading the model — not a bug, by design.)
- Behavioral caveat (not a bug): a file renamed in place while mid-transcription breaks that run — the note is written under the old name and the renamed file is not re-scheduled; restart the service to pick it up. Observed 2026-08-11 when the user cleaned newline filenames (phone recorder artifact) out of the watch folder mid-batch.

---

## Active TODOs

- [x] Run real voice-note validation (drop an actual Arabic recording and an English one; confirm language detection + transcript quality). *(added: 2026-08-10, done: 2026-08-11 — 4 real Arabic notes processed on GPU)*
- [x] Validate diarization on a genuine multi-person recording (auto mode; the screen recording was one person voicing two characters). *(added: 2026-08-10, done: 2026-08-10)*
- [x] Decide if the model should stay resident between notes (instant transcription, ~3.8 GB RAM) vs idle ~20 MB (restart service to unload). *(added: 2026-08-10, done: 2026-08-10 — keep resident; transcriptions are slow on CPU)*
- [x] GPU migration: torch 2.13.0+cu129 via pip, ctranslate2 4.8.1 CUDA built from source (CUDA 13.3 + gcc-16 workaround), service rewired. *(added: 2026-08-11, done: 2026-08-11)*
- [ ] Consider re-scheduling files renamed mid-processing (a clean fix for the caveat above) — needs a `rename` → requeue path in the watcher. *(added: 2026-08-11)*
- [ ] If diarization quality on fast turn-taking becomes a recurring pain, evaluate an alternative engine (e.g. NVIDIA NeMo). Deliberately parked — pyannote limit verified 2026-08-10. *(added: 2026-08-10)*

---

## Planned Features

- [ ] Optional Arabic diacritization/harakat post-processing of Arabic transcripts. *(added: 2026-08-10)*
- [ ] Optional timestamped segments in the note (e.g. minutes marks). *(added: 2026-08-10)*
