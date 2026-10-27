#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
MODE="release"
MODE_REQUESTED=""
WRITE_PDF=0
ARCHIVE=""
LEAN_PACKAGES_CACHE=""

while (($#)); do
  case "$1" in
    --release)
      if [[ -n "$MODE_REQUESTED" && "$MODE_REQUESTED" != "release" ]]; then
        printf 'ERROR: --release and --development are mutually exclusive.\n' >&2
        exit 2
      fi
      MODE="release"
      MODE_REQUESTED="release"
      ;;
    --development)
      if [[ -n "$MODE_REQUESTED" && "$MODE_REQUESTED" != "development" ]]; then
        printf 'ERROR: --release and --development are mutually exclusive.\n' >&2
        exit 2
      fi
      MODE="development"
      MODE_REQUESTED="development"
      ;;
    --write-pdf)
      WRITE_PDF=1
      ;;
    --archive)
      if (($# < 2)); then
        printf 'ERROR: --archive requires a ZIP path.\n' >&2
        exit 2
      fi
      if [[ -n "$ARCHIVE" ]]; then
        printf 'ERROR: --archive may be supplied only once.\n' >&2
        exit 2
      fi
      ARCHIVE="$2"
      shift
      ;;
    --lean-packages-cache)
      if (($# < 2)); then
        printf 'ERROR: --lean-packages-cache requires a directory path.\n' >&2
        exit 2
      fi
      if [[ -n "$LEAN_PACKAGES_CACHE" ]]; then
        printf 'ERROR: --lean-packages-cache may be supplied only once.\n' >&2
        exit 2
      fi
      LEAN_PACKAGES_CACHE="$2"
      shift
      ;;
    -h|--help)
      printf 'Usage: %s [--release|--development] [--write-pdf] [--archive ZIP] [--lean-packages-cache DIR]\n' "$0"
      printf '\n'
      printf '  --release      Require every release gate, including Lean and checksums.\n'
      printf '  --development  Permit explicitly reported skips for unfinished release artifacts.\n'
      printf '  --write-pdf    Install the deterministic clean rebuild as paper/paper4.pdf.\n'
      printf '  --archive ZIP  Verify the final ZIP entry set, hashes, types, and paths.\n'
      printf '  --lean-packages-cache DIR\n'
      printf '                 Reuse a validated external Lake packages directory.\n'
      exit 0
      ;;
    *)
      printf 'ERROR: unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
  shift
done

if ! command -v python3 >/dev/null 2>&1; then
  printf 'ERROR: python3 is required to run the release gate.\n' >&2
  exit 1
fi

ARGS=(--root "$ROOT" --mode "$MODE")
if ((WRITE_PDF)); then
  ARGS+=(--write-pdf)
fi
if [[ -n "$ARCHIVE" ]]; then
  ARGS+=(--archive "$ARCHIVE")
fi
if [[ -n "$LEAN_PACKAGES_CACHE" ]]; then
  ARGS+=(--lean-packages-cache "$LEAN_PACKAGES_CACHE")
fi

export PYTHONDONTWRITEBYTECODE=1
exec python3 "$ROOT/verification/check_release.py" "${ARGS[@]}"
