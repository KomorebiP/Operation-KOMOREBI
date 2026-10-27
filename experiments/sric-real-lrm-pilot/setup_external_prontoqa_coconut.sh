#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)/external_runtime}"
COMMIT="32f413d8d55239d9bc54bb6b6ec37b0630891ed4"
mkdir -p "$ROOT"
python -m venv "$ROOT/.venv"
PY="$ROOT/.venv/bin/python"
HF="$ROOT/.venv/bin/hf"
"$PY" -m pip install --upgrade pip setuptools wheel
"$PY" -m pip install -r "$(dirname "$0")/requirements-real.txt"
"$PY" -m pip install -e "$(dirname "$0")"
if [[ ! -d "$ROOT/are-lrms-easily-interpretable/.git" ]]; then
  git clone https://github.com/connordilgren/are-lrms-easily-interpretable.git "$ROOT/are-lrms-easily-interpretable"
fi
git -C "$ROOT/are-lrms-easily-interpretable" checkout --detach "$COMMIT"
"$HF" download connordilgren/gpt2-prontoqa-multimode-coconut checkpoint_37 --local-dir "$ROOT/checkpoints/gpt2_prontoqa_multimode"
"$HF" download openai-community/gpt2 --local-dir "$ROOT/models/gpt2"
cat > "$ROOT/runtime_paths.json" <<JSON
{
  "python": "$PY",
  "external_repo": "$ROOT/are-lrms-easily-interpretable",
  "external_commit": "$COMMIT",
  "checkpoint": "$ROOT/checkpoints/gpt2_prontoqa_multimode/checkpoint_37",
  "base_model": "$ROOT/models/gpt2",
  "data": "$ROOT/are-lrms-easily-interpretable/data/prontoqa_test.json"
}
JSON
echo "SRIC_REAL_LRM_EXTERNAL_SETUP=PASS"
