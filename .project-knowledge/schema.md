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
speakers: 2                          # optional — only when diarization found >1 voice
---
```

Body: `# YYYY-MM-DD HHMM - <stem>` heading, blank line, transcript text.
When `speakers > 1`, the body is grouped by voice into turns:

```
**Speaker 1:** first utterance

**Speaker 2:** reply
```

## Behavior Notes

- Empty transcript (no speech after VAD) still writes a note with empty body.
- Language is auto-detected per note (`language=None` in `transcribe()`); expected `ar` / `en` for this user, but any Whisper lang can appear (e.g. `la` for gibberish test audio).
- Speaker labels appear **only when diarization detects >1 distinct voice**. One voice — even two characters voiced by the same person — stays a plain transcript. Diarization separates by vocal identity, not persona.
