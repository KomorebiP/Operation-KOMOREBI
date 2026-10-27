#!/usr/bin/env bash
set -euo pipefail
komorebi_task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
komorebi_runtime="$(dirname -- "$komorebi_task_root")/.lean_runtime"
export PATH="$komorebi_runtime/lean-4.34.0-rc2-linux/bin:$PATH"
export LEAN_SYSROOT="$komorebi_runtime/lean-4.34.0-rc2-linux"
export LD_PRELOAD="$komorebi_runtime/proc_self_exe_compat.so${LD_PRELOAD:+:$LD_PRELOAD}"
exec "$@"
