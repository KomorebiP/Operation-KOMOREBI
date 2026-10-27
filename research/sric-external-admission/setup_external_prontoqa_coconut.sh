#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)/external_runtime}"
DEVICE_MODE="${DEVICE_MODE:-cuda}"
TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu124}"
DISABLE_XET="${DISABLE_XET:-0}"
LOCAL_FILES_ONLY="${LOCAL_FILES_ONLY:-0}"
COMMIT="32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
REPO_URL="https://github.com/connordilgren/are-lrms-easily-interpretable.git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

resolve_python() {
  if [[ -n "${PYTHON_EXE:-}" ]]; then
    candidates=("$PYTHON_EXE")
  else
    candidates=(python3.12 python3.11 python3.10 python)
  fi
  for candidate in "${candidates[@]}"; do
    command -v "$candidate" >/dev/null 2>&1 || continue
    version="$($candidate -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
    case "$version" in
      3.10|3.11|3.12) printf '%s\n' "$candidate"; return 0 ;;
    esac
  done
  echo "No compatible Python found. Install Python 3.10-3.12 or set PYTHON_EXE." >&2
  return 1
}

mkdir -p "$ROOT"
ROOT="$(cd "$ROOT" && pwd)"
VENV="$ROOT/.venv"
EXTERNAL_REPO="$ROOT/are-lrms-easily-interpretable"

if [[ ! -x "$VENV/bin/python" ]]; then
  BASE_PY="$(resolve_python)"
  "$BASE_PY" -m venv "$VENV"
fi
PY="$VENV/bin/python"
version="$($PY -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
case "$version" in
  3.10|3.11|3.12) ;;
  *) echo "Pinned runtime requires Python 3.10-3.12; found $version" >&2; exit 2 ;;
esac

"$PY" -m pip install --upgrade pip setuptools wheel
if [[ "$DEVICE_MODE" == "cpu" ]]; then
  "$PY" -m pip install torch==2.5.1
else
  "$PY" -m pip install torch==2.5.1 --index-url "$TORCH_INDEX_URL"
fi
"$PY" -m pip install -r "$SCRIPT_DIR/requirements-real-no-torch.txt"
"$PY" -m pip install -e "$SCRIPT_DIR"
"$PY" -m pip check

if [[ ! -d "$EXTERNAL_REPO/.git" ]]; then
  if [[ "$LOCAL_FILES_ONLY" == "1" ]]; then
    echo "LOCAL_FILES_ONLY=1, but the pinned external repository is absent: $EXTERNAL_REPO" >&2
    exit 3
  fi
  git clone "$REPO_URL" "$EXTERNAL_REPO"
fi
if [[ -n "$(git -C "$EXTERNAL_REPO" status --porcelain)" ]]; then
  echo "External repository is dirty: $EXTERNAL_REPO" >&2
  exit 3
fi
if [[ "$LOCAL_FILES_ONLY" == "1" ]]; then
  git -C "$EXTERNAL_REPO" cat-file -e "$COMMIT^{commit}" || {
    echo "LOCAL_FILES_ONLY=1, but the pinned commit is absent from the local repository." >&2
    exit 4
  }
else
  git -C "$EXTERNAL_REPO" fetch origin "$COMMIT"
fi
git -C "$EXTERNAL_REPO" checkout --detach "$COMMIT"
[[ "$(git -C "$EXTERNAL_REPO" rev-parse HEAD)" == "$COMMIT" ]] || {
  echo "External commit verification failed" >&2; exit 4;
}

DOWNLOAD_ARGS=(
  "$SCRIPT_DIR/download_external_assets.py"
  --runtime-root "$ROOT"
  --external-repo "$EXTERNAL_REPO"
  --source-lock "$SCRIPT_DIR/external_source_lock.json"
)
[[ "$LOCAL_FILES_ONLY" == "1" ]] && DOWNLOAD_ARGS+=(--local-files-only)
[[ "$DISABLE_XET" == "1" ]] && DOWNLOAD_ARGS+=(--disable-xet)

set +e
"$PY" "${DOWNLOAD_ARGS[@]}"
status=$?
set -e
if [[ $status -ne 0 && "$DISABLE_XET" != "1" && "$LOCAL_FILES_ONLY" != "1" ]]; then
  echo "Default Hugging Face/Xet transfer failed; retrying through standard HTTP/LFS." >&2
  "$PY" "${DOWNLOAD_ARGS[@]}" --disable-xet
elif [[ $status -ne 0 ]]; then
  echo "Exact external-asset download failed. This is an infrastructure failure, not a model result." >&2
  exit "$status"
fi

PATHS_FILE="$ROOT/runtime_paths.json"
[[ -f "$PATHS_FILE" ]] || { echo "Missing asset receipt: $PATHS_FILE" >&2; exit 5; }
CHECKPOINT="$($PY -c 'import json,sys; print(json.load(open(sys.argv[1]))["checkpoint"])' "$PATHS_FILE")"
DATA="$($PY -c 'import json,sys; print(json.load(open(sys.argv[1]))["data"])' "$PATHS_FILE")"

"$PY" "$SCRIPT_DIR/capture_environment.py" --output "$ROOT/environment.json"
"$PY" -m sric_real_lrm verify-source --external-repo "$EXTERNAL_REPO" --dataset-key prontoqa_test
"$PY" -m sric_real_lrm preflight --external-repo "$EXTERNAL_REPO" --checkpoint "$CHECKPOINT" --data "$DATA"

echo "SRIC_BLOCK24_EXTERNAL_SETUP=PASS"
echo "runtime_paths=$PATHS_FILE"
echo "python=$PY"
echo "external_repo=$EXTERNAL_REPO"
echo "checkpoint=$CHECKPOINT"
echo "data=$DATA"
