# Pinned runtime recovery

The exact archived Linux runtime was recovered from the seven existing offline parts on 2026-10-12. All ZIP payload CRC checks, seven part sizes and SHA-256 checks, total size, and combined archive SHA-256 passed before extraction. The combined archive hash is `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.

Lean reports 4.34.0-rc2 at commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Lake starts, all nine dependency Git revisions match the inherited project pins, and the targeted `RecoverySmoke.lean` compiled with warnings treated as errors. These are runtime recovery checks, not a new project replay or declaration audit.

The runtime is at `/workspace/scratch/5d9f7f8127b0/runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2`. The temporary working path is not a portable promise. The archive is intentionally excluded from the continuation deliverable.

Direct Lean startup failed with `failed to locate application`. The recovered kit already includes a documented executable-location adapter that maps only the current process's own numeric `/proc/<pid>/exe` to `/proc/self/exe`. Using its existing `run.sh` succeeds. Scripts invoking the compiler directly in this environment should set `LD_PRELOAD` to the kit's `compat/app_path.so`; neither the compiler nor any proof rules were modified.

Eight dependency `lib/lean` cache directories are present. The ninth pinned repository, Cli, has no such directory. Existing verifiers collect available cache directories. The targeted smoke passed; a genuinely missing imported object will be detected by the subsequent project compilation.

The complete receipt is `recovery.json`, with compiler and adapter hashes. `assembly.log` and `offline_archive_manifest.json` preserve archive checks. No inherited project source was modified during recovery.
