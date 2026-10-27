# Host compatibility and compiler identity

The official Lean 4.34.0-rc2 Linux release was downloaded without modification. Its compiler reports revision 6a10ac8c22beadecabdbb0919c2b50214762f91d. Mathlib is checked out at aeb72f1e9981b6d35b426b16dca7759be3e7ba06 with the pinned dependency manifest.

The unmodified executable initially exited with `error: failed to locate application`. The pinned runtime source (src/runtime/io.cpp, lean_io_app_path) constructs `/proc/<getpid()>/exe`. In this host's process namespace that numbered path does not exist, while `/proc/self/exe` resolves. A direct Python probe reproduced the difference. `LEAN_SYSROOT` alone did not fix it. A diagnostic strace attempt was rejected by the host's ptrace restriction; no tracing permission was changed or retried.

The small source in scripts/proc_self_exe_compat.c redirects exactly that own-process executable readlink to `/proc/self/exe`. All other readlink calls go to the original libc function. scripts/lean_env.sh applies the shim and selects the pinned compiler. No Lean executable, shared library, proof kernel, theorem source, or compiled dependency was patched. The shim is additional host compatibility code and remains part of this run's recorded execution environment, not a mathematical axiom.

Both `lean --version` and `lean --print-prefix` succeed under the wrapper. Subsequent proof checks use this wrapper and record the exact source and command. An ordinary matching host does not need the compatibility shim.

An earlier remote setup was launched before direct local source access was confirmed. Its slow follow-up status calls were abandoned and it was not used for any accepted proof compilation. Its last observed state is retained in ENVIRONMENT_ATTEMPTS.json.
