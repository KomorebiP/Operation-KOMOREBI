#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 3 ]]; then
  echo 'Usage: run.sh /absolute/formal-root /absolute/pinned-runtime /absolute/new-output [--base-fresh /absolute/fresh54] [--boundary /absolute/ReleaseBoundary.lean]' >&2
  exit 2
fi
AUDIT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_ROOT="$(realpath "$1")"
KIT="$(realpath "$2")"
OUTPUT_DIR="$(realpath -m "$3")"
shift 3
exec bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 "$AUDIT_DIR/verify_release.py" --root "$SOURCE_ROOT" --kit "$KIT" --out "$OUTPUT_DIR" "$@"
