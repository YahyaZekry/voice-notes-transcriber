# Roadmap

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10
> Forward-looking only. Check this before starting any task — know what's in flight.

## Current Goal

In production. Validate accuracy with real Arabic + English voice notes (the espeak test clips were robotic; real speech is the true test). Reuse the transcription engine for future AI projects in `/mnt/airfryer/Projects/AI/`.

---

## Known Bugs

- None known. (Testing artifact only: `--once` with an empty folder exits silently without loading the model — not a bug, by design.)

---

## Active TODOs

- [ ] Run real voice-note validation (drop an actual Arabic recording and an English one; confirm language detection + transcript quality). *(added: 2026-08-10)*
- [x] Commit pending changes (notifications + video + diarization) — done in `b56a73d`. *(added: 2026-08-10, done: 2026-08-10)*
- [ ] Validate diarization on a genuine multi-person recording (auto mode; the screen recording was one person voicing two characters). *(added: 2026-08-10)*
- [ ] Decide if the model should stay resident between notes (instant transcription, ~3.8 GB RAM) vs idle ~20 MB (restart service to unload). *(added: 2026-08-10)*

---

## Planned Features

- [ ] Optional Arabic diacritization/harakat post-processing of Arabic transcripts. *(added: 2026-08-10)*
- [ ] Optional timestamped segments in the note (e.g. minutes marks). *(added: 2026-08-10)*
