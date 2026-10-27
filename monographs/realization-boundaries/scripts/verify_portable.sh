#!/usr/bin/env bash
set -euo pipefail
: "${KOMOREBI_LEAN_KIT:?Set KOMOREBI_LEAN_KIT to the restored portable kit}"
kit_root="$(cd -- "$KOMOREBI_LEAN_KIT" && pwd -P)"
export PATH="$kit_root/toolchain/bin:$PATH"
unset LEAN_PATH LEAN_SRC_PATH LEAN_SYSROOT LAKE_HOME
if version_output="$("$kit_root/toolchain/bin/lean" --version 2>&1)"; then
  :
elif [[ "$version_output" == *'failed to locate application'* ]]; then
  adapter_dir="$(mktemp -d /tmp/boundaries-lean.XXXXXXXX)"
  trap 'rm -rf -- "$adapter_dir"' EXIT
  cp -- "$kit_root/compat/app_path.so" "$adapter_dir/app_path.so"
  export LD_PRELOAD="$adapter_dir/app_path.so${LD_PRELOAD:+:$LD_PRELOAD}"
else
  printf '%s\n' "$version_output" >&2
  exit 2
fi
python3 "$(dirname -- "$0")/verify.py" --kit "$kit_root" "$@"
