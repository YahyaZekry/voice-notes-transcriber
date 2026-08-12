#!/usr/bin/env bash
# download_models.sh — pre-download every model the transcriber needs.
#
# Downloads into the default HuggingFace cache (~/.cache/huggingface/) so the
# service runs fully offline once it has the files. Already-cached repos are
# skipped automatically.
#
# Usage:
#   ./download_models.sh                    # all models (pyannote ones need HF_TOKEN)
#   ./download_models.sh --model tiny       # use a smaller whisper model instead
#   HF_TOKEN=hf_xxx ./download_models.sh    # pass the token inline
#
# The script also reads HF_TOKEN from ~/.config/voice-transcriber/hf.env if set.
set -euo pipefail

cd "$(dirname "$0")"

VENV_PYTHON="${VENV_PYTHON:-$PWD/.venv/bin/python}"
WHISPER_MODEL="${TRANSCRIBER_MODEL:-large-v3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      WHISPER_MODEL="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "venv python not found at $VENV_PYTHON — run 'uv venv --python 3.12 .venv' and install deps first." >&2
  exit 1
fi

# HF_TOKEN: env var wins, otherwise the service env file.
if [[ -z "${HF_TOKEN:-}" && -f "$HOME/.config/voice-transcriber/hf.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$HOME/.config/voice-transcriber/hf.env"
  set +a
fi

echo "==> Using whisper model: $WHISPER_MODEL"
echo "==> HF_TOKEN set: $([[ -n "${HF_TOKEN:-}" ]] && echo yes || echo no)"

# Map the shorthand (large-v3, small, ...) to the faster-whisper repo id.
case "$WHISPER_MODEL" in
  large-v3)   WHISPER_REPO="Systran/faster-whisper-large-v3" ;;
  large-v2)   WHISPER_REPO="Systran/faster-whisper-large-v2" ;;
  large)      WHISPER_REPO="Systran/faster-whisper-large-v2" ;;
  small)      WHISPER_REPO="Systran/faster-whisper-small" ;;
  tiny)       WHISPER_REPO="Systran/faster-whisper-tiny" ;;
  base)       WHISPER_REPO="Systran/faster-whisper-base" ;;
  */*)        WHISPER_REPO="$WHISPER_MODEL" ;;  # already a full repo id
  *)          WHISPER_REPO="Systran/faster-whisper-${WHISPER_MODEL}" ;;
esac

PY="$VENV_PYTHON"

# Public whisper model — no token needed.
echo
echo "==> [1/5] $WHISPER_REPO (public)"
"$PY" - "$WHISPER_REPO" <<'EOF'
import sys
from huggingface_hub import snapshot_download
snapshot_download(sys.argv[1])
print("    done")
EOF

# Gated pyannote models — need HF_TOKEN and accepted licenses on HF.
gated() {
  local repo="$1"
  echo
  echo "==> [gated] $repo"
  if [[ -z "${HF_TOKEN:-}" ]]; then
    echo "    SKIPPED: no HF_TOKEN set. Export HF_TOKEN=hf_... or add it to" >&2
    echo "    ~/.config/voice-transcriber/hf.env (see README 'HuggingFace token')." >&2
    return 1
  fi
  "$PY" - "$repo" "$HF_TOKEN" <<'EOF'
import sys
from huggingface_hub import snapshot_download
snapshot_download(sys.argv[1], token=sys.argv[2])
print("    done")
EOF
}

failures=0
gated "pyannote/speaker-diarization-3.1"           || failures=$((failures+1))
gated "pyannote/segmentation-3.0"                  || failures=$((failures+1))
gated "pyannote/speaker-diarization-community-1"   || failures=$((failures+1))
gated "pyannote/wespeaker-voxceleb-resnet34-LM"    || failures=$((failures+1))

echo
if [[ $failures -gt 0 ]]; then
  echo "!! $failures gated model(s) skipped. The pyannote ones require:" >&2
  echo "   https://huggingface.co/pyannote/speaker-diarization-3.1" >&2
  echo "   https://huggingface.co/pyannote/segmentation-3.0" >&2
  echo "   https://huggingface.co/pyannote/speaker-diarization-community-1" >&2
  echo "   https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM" >&2
  echo "   -> log in, accept the access/license, then re-run this script." >&2
else
  echo "All models downloaded. The service can now run offline." >&2
fi
