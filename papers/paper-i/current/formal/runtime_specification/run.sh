#!/usr/bin/env bash
set -euo pipefail
kit_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo 'This offline bundle requires Linux x86_64 (including x86_64 WSL2).' >&2
  exit 2
fi
export PATH="$kit_root/toolchain/bin:$PATH"
unset LEAN_PATH LEAN_SRC_PATH LEAN_SYSROOT LAKE_HOME
adapter_dir=''
cleanup() { [[ -z "$adapter_dir" ]] || rm -rf -- "$adapter_dir"; }
trap cleanup EXIT
# Probe the unmodified runtime. Enable the path adapter only for the known
# executable-discovery failure. Do not mask other startup errors.
if version_output="$(lean --version 2>&1)"; then
  :
elif [[ "$version_output" == *'failed to locate application'* ]]; then
  # LD_PRELOAD cannot represent a filename containing spaces. A private,
  # short temporary path lets the whole kit itself live in a spaced path.
  adapter_dir="$(mktemp -d /tmp/komorebi-lean.XXXXXXXX)"
  cp -- "$kit_root/compat/app_path.so" "$adapter_dir/app_path.so"
  export LD_PRELOAD="$adapter_dir/app_path.so${LD_PRELOAD:+:$LD_PRELOAD}"
  lean --version >/dev/null
else
  printf '%s\n' "$version_output" >&2
  exit 2
fi
command_name="${1:-verify}"
[[ $# == 0 ]] || shift
case "$command_name" in
  lean|lake|leanc|leanchecker) "$command_name" "$@" ;;
  check)
    [[ $# == 1 ]] || { echo 'Usage: bash run.sh check FILE.lean' >&2; exit 2; }
    proof_file="$(realpath -- "$1")"
    cd -- "$kit_root/workspace"
    lake env lean -DwarningAsError=true "$proof_file"
    ;;
  verify) python3 "$kit_root/scripts/verify.py" "$@" ;;
  attach) python3 "$kit_root/scripts/attach.py" "$@" ;;
  shell)
    echo 'Portable Lean active in this shell. Type exit to leave.'
    cd -- "$kit_root/workspace"
    bash --noprofile --norc -i
    ;;
  *) echo 'Commands: verify, check FILE, lean ARGS, lake ARGS, attach PROJECT, shell' >&2; exit 2 ;;
esac
