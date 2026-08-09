# Schema

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-10
> Source of truth is `transcriber.py::write_note` — the output note format contract.

## Output Note (Markdown file in `Transcriptions/`)

Filename: `YYYY-MM-DD HHMM - <audio-stem>.md`
(`stamp` = transcription time, not recording time; `<audio-stem>` = original filename without extension, sanitized of `/\:*?"<>|`)

```yaml
---
type: voice-note
created: 2026-08-10T00:54:27        # ISO, transcription time
source: test-arabic.wav              # original audio filename
duration: 0:05                       # M:SS audio duration
language: ar                         # Whisper auto-detected lang code
---
```

Body: `# YYYY-MM-DD HHMM - <stem>` heading, blank line, raw transcript text.

## Behavior Notes

- Empty transcript (no speech after VAD) still writes a note with empty body.
- Language is auto-detected per note (`language=None` in `transcribe()`); expected `ar` / `en` for this user, but any Whisper lang can appear (e.g. `la` for gibberish test audio).
