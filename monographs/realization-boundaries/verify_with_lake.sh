#!/usr/bin/env bash
# Run the unchanged strict verifier against a conventional pinned Lean/Lake checkout.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
cd -- "$repo_root"
if ! command -v lean >/dev/null 2>&1; then
  echo 'Lean was not found on PATH. Install the pinned toolchain described in docs/BUILDING.md.' >&2
  exit 2
fi
if [[ ! -d "$repo_root/.lake/packages/mathlib" ]]; then
  echo 'Pinned dependencies are missing. Run lake exe cache get from the repository root first.' >&2
  exit 2
fi
lean_prefix="$(lean --print-prefix)"
if [[ ! -x "$lean_prefix/bin/lake" || ! -x "$lean_prefix/bin/leanchecker" ]]; then
  echo 'The selected Lean installation must include lake and leanchecker.' >&2
  exit 2
fi
runtime_view="$(mktemp -d /tmp/realization-boundaries-runtime.XXXXXXXX)"
trap 'rm -rf -- "$runtime_view"' EXIT
mkdir -p -- "$runtime_view/workspace/.lake"
ln -s -- "$lean_prefix" "$runtime_view/toolchain"
ln -s -- "$repo_root/.lake/packages" "$runtime_view/workspace/.lake/packages"
python3 "$repo_root/scripts/verify.py" --kit "$runtime_view" "$@"
