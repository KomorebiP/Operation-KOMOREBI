#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo 'Usage: bash formal/verify.sh /absolute/pinned-runtime /absolute/new-output' >&2
  exit 2
fi
FORMAL_ROOT="$(cd "$(dirname "$0")" && pwd)"
exec bash "$FORMAL_ROOT/scripts/release_audit/run.sh" "$FORMAL_ROOT/current" "$1" "$2" \
  --boundary "$FORMAL_ROOT/tests/ReleaseBoundary.lean"
