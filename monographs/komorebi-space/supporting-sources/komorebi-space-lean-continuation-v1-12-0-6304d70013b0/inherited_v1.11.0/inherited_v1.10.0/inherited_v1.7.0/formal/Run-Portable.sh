#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ne 2 ]]; then
  echo "Usage: bash formal/Run-Portable.sh /path/to/portable-runtime NEW_REPLAY_LABEL" >&2
  exit 2
fi
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$here/scripts/verify.py" --runtime "$1" --label "$2"
