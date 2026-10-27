#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$ROOT_DIR/build"
MAIN="Projector_Refinement_Physics_Covariant_Backreaction_Bridge"
PYTHON_BIN="${PYTHON_BIN:-python}"

cd "$ROOT_DIR"
export PYTHONDONTWRITEBYTECODE=1
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1787097600}"

command -v "$PYTHON_BIN" >/dev/null 2>&1 || {
  echo "Python interpreter not found: $PYTHON_BIN" >&2
  exit 127
}
command -v latexmk >/dev/null 2>&1 || {
  echo "latexmk is required to build the manuscript." >&2
  exit 127
}

mkdir -p "$BUILD_DIR"
"$PYTHON_BIN" code/validate_release.py
latexmk \
  -pdf \
  -interaction=nonstopmode \
  -halt-on-error \
  -file-line-error \
  -outdir="$BUILD_DIR" \
  "$MAIN.tex"
"$PYTHON_BIN" code/validate_release.py \
  --pdf "$BUILD_DIR/$MAIN.pdf" \
  --log "$BUILD_DIR/$MAIN.log"
