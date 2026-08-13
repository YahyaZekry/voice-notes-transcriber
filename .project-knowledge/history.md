# History

> Part of voice-notes-transcriber/.project-knowledge/ | Last updated: 2026-08-11
> Past-only. Append-only — never delete entries.

## Removed

- ~~Old home `~/voice-notes-transcriber/`~~ — project moved to `/mnt/airfryer/Projects/AI/voice-notes-transcriber/`; venv recreated (venvs are path-bound) *(removed: 2026-08-10)*

---

## Fixed

- **Speaker 1/Speaker 2 labels on single-speaker recordings** — pyannote force-splits monologues: with `num_speakers=2` it alternates between two arbitrary clusters on one voice (verified: a 31s single-voice clip → probe split → cluster centroid cosine sim **0.962**; a real 2-voice clip → **0.162**). Fix: `_clusters_distinct()` embeds each cluster's audio via the pipeline's wespeaker embedding model (`PretrainedSpeakerEmbedding`) and compares L2-normalized centroid cosine similarity; the probe is accepted only when sim < **0.75**, and auto mode's own 2-speaker results above the threshold are collapsed back to 1. Verified: monologue→1 speaker, balanced 2-voice→2, dominant+≥4s minority→2 (probe path still works). *(fixed: 2026-08-12)*
- Watch mode ignored files already present when the service started → added `scan_existing()` before starting the observer *(fixed: 2026-08-10)*
- venv broke after the directory move → recreated with `uv venv --python 3.12` + reinstall *(fixed: 2026-08-10)*
- Active/large files could be transcribed mid-write (e.g. a screen recording landing in the folder) → stability gate now requires mtime age ≥ 5s AND unchanged size, waiting up to 10 min *(fixed: 2026-08-10)*
- Move-to-`Completed/` could theoretically re-trigger the watcher → `_schedule` now processes only direct children of the root folder *(fixed: 2026-08-10)*
- Broken `torchcodec` audio decoder (lib mismatches, needs CUDA `libnvrtc`) → bypassed entirely: audio decoded to a 16 kHz mono waveform via PyAV and fed to the pyannote pipeline as `{'waveform', 'sample_rate'}` *(fixed: 2026-08-10)*
- pyannote API drift (`Pipeline.from_pretrained(use_auth_token=)` → `token=`; output is now `DiarizeOutput` with `.speaker_diarization`, no longer the bare `Annotation`) → fixed both with a `getattr` compatibility fallback *(fixed: 2026-08-10)*
- pyannote **auto mode undercounts speakers** on recordings where one voice dominates: a real 2-person Arabic video (81/19 speech split) came back as 1 speaker. Fix: when auto returns a single speaker on a clip with ≥10s of speech, probe `num_speakers=2` and accept the split only if the minority voice holds ≥10% of speech time AND ≥4s (guards against over-splitting monologues). Same-person persona recordings still correctly stay 1 speaker. *(fixed: 2026-08-10)*
- pyannote **cannot separate rapid-fire Q&A with short interjections**: on the user's 2-person Arabic quiz video, the student's 0.3–1s answers ("لا", "غير صحيح", "تيمن") were absorbed into the teacher's cluster for the first 60s. Verified as a hard model limit at all three levels — (1) segmentation-3.0's secondary-speaker channel registers only ~3.2s of 78s total speech; (2) even nearest-centroid embedding reassignment fails (0.5s utterances padded through resnet34 are indistinguishable from the dominant speaker); (3) local channel identities flip between chunks so overlap-stitching can't map them. Long utterances of both speakers ARE labeled correctly. Decided to accept this limitation rather than swap diarization engines. *(accepted: 2026-08-10)*
- **CUDA out of memory on the 2nd file of a batch** — whisper float16 (~3.2 GB) + pyannote resident on GPU (~1.5 GB) + desktop pushed past 7.7 GB usable. Fix: after every note, `_release_diarization()` moves the pyannote pipeline back to CPU and calls `torch.cuda.empty_cache()`; `_diarize_turns` re-moves it to CUDA per run. 4-file batch then completed cleanly. *(fixed: 2026-08-11)*
- **File renamed while mid-transcription broke that run** (user cleaned newline filenames out of the watch folder): note written under the old name, renamed file left unprocessed. Worked around by deleting the stale note and restarting the service to re-process. Root-cause fix (requeue on rename) parked in roadmap. *(2026-08-11)*

---

## Decisions

- **Model choice: `large-v3` local over Groq** — user's rule: if the remote option runs the same model, prefer local. Both are Whisper `large-v3`; local via faster-whisper. `large-v3` (multilingual) chosen over English-only `distil-large-v3` for Arabic. *(2026-08-10)*
- **GPU (CUDA) over CPU** — CPU `int8` never finished a 10-min note (CPU-bound, ~4 GB RAM); user approved switching to the RTX 3050. `float16` on CUDA now handles 10–18 min notes in ~3–5 min + diarization. *(2026-08-11)*
- **torch 2.13.0+cu129 via pip, not uv** — uv's HTTP client times out on `pypi.nvidia.com`; pip and curl work fine. All CUDA/nvidia wheels use `python -m pip`. *(2026-08-11)*
- **ctranslate2 built from source with CUDA 13.3** — PyPI ships only CPU wheels for ctranslate2; no CUDA wheels exist anywhere. Built 4.8.1 from the git tag (+submodules) against a locally-assembled CUDA 13.3 toolkit (`.cuda13/` from NVIDIA ubuntu2404 debs, extracted with bsdtar since Arch has no dpkg-deb). CUDA 12.9 nvcc can't parse gcc 16 headers; CUDA 13.3 + `-allow-unsupported-compiler` works. Build: `WITH_CUDA=ON WITH_CUDNN=ON WITH_MKL=OFF OPENMP_RUNTIME=COMP CUDA_ARCH_LIST=8.6`, cmake 3.31 (pip) because cmake 4.x dropped FindCUDA. Runtime libs served via `LD_LIBRARY_PATH` in the systemd unit. *(2026-08-11)*
- **Python 3.12 via uv** — system Python 3.14 too new for faster-whisper; pinned 3.12.13 in a venv managed by `uv`. *(2026-08-10)*
- **Watch mode + systemd --user** — auto-start at login, no sudo needed; lazy model load keeps idle RAM at ~20 MB. *(2026-08-10)*
- **Lazy model load** — model loads on first note, not at service start, to avoid pinning ~3.8 GB RAM permanently. *(2026-08-10)*
- **Notifications via `notify-send`** — native KDE toasts from the service context, `kdialog` passivepopup fallback, non-fatal, `TRANSCRIBER_NOTIFY=0` to disable. *(2026-08-10)*
- **Videos transcribed from their audio track** — faster-whisper's ffmpeg decode reads video files' audio; no extra extraction step. *(2026-08-10)*
- **Speaker diarization via pyannote** — `pyannote/speaker-diarization-3.1` + `pyannote/segmentation-3.0` + `pyannote/speaker-diarization-community-1` (embedding), all gated (HF token at `~/.config/voice-transcriber/hf.env`, `0600`). Labels only appear when >1 distinct voice; same-person characters stay plain (diarization = voice identity, not persona). *(2026-08-10)*
- **Auto speaker count by default** — `num_speakers=None` lets pyannote estimate; `TRANSCRIBER_SPEAKERS=N` forces it for known meetings. `TRANSCRIBER_DIARIZE=0` disables entirely. *(2026-08-10)*
