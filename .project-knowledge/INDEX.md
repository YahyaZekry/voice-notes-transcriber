# Voice Notes Transcriber — Knowledge Index

> Last updated: 2026-08-10
> Status: Active (deployed & running)
> Stack: Python 3.12 + faster-whisper (Whisper large-v3, CPU/int8) + pyannote diarization + watchdog + notify-send
> Current goal: In production. Diarization live (labels notes when >1 real voice); validate with real Arabic/English notes and a genuine multi-person recording.

## What This Project Does
Watches `/mnt/knowledge/Obsidian/Personal/VoiceNotes/`, transcribes new voice notes and videos **locally** (no cloud) with Whisper `large-v3` (Arabic + English auto-detected), labels speakers when >1 distinct voice is present, writes a Markdown note with YAML frontmatter to `VoiceNotes/Transcriptions/`, then moves the file to `VoiceNotes/Completed/` — with desktop toasts on found/failed/complete.

---

## Files in This Folder

| File | Contents | Load when... |
|------|----------|--------------|
| `stack.md` | Tech stack, run/service commands, env vars | Setting up, changing the model, checking how to run |
| `structure.md` | File tree, entry points, key files | Navigating the codebase, adding files |
| `schema.md` | Output note frontmatter contract | Changing the generated note format |
| `systems.md` | Transcription engine, file watching, service | Touching any subsystem |
| `features.md` | User-facing features and workflow | Understanding what's built |
| `integrations.md` | Obsidian vault paths, systemd, HF models + token | Path changes, service changes, model downloads |
| `roadmap.md` | Known bugs, TODOs, current goal | Starting any task |
| `history.md` | Fixes, decisions | Debugging, reviewing past decisions |
| `sessions.md` | Session-by-session log | Reviewing work history |

---

## Context Loading Guide

| Task | Load these files |
|------|-----------------|
| Change model / device / paths | `stack.md` + `integrations.md` |
| Change output note format | `schema.md` |
| Touch service / boot behavior | `integrations.md` + `systems.md` |
| Add a feature (e.g. diacritization) | `roadmap.md` + `features.md` |
| General orientation (new session) | This file → then pick by task |
| Full audit | All files |

---

*Maintained with [project-knowledge](https://github.com/YahyaZekry/claude-code-skills) · by [Yahya Zekry](https://github.com/YahyaZekry)*
