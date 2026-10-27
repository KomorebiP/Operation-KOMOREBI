# Runtime recovery for WR15

The original portable runtime was recovered on 2026-10-13 from the seven existing `Lean_Offline_01.zip` through `Lean_Offline_07.zip` files. ZIP payload CRC, each part size and SHA-256, combined size, and combined SHA-256 all passed before extraction. The verified combined archive hash is `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.

The active root is `/workspace/scratch/5d9f7f8127b0/runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2`. The pre-existing pruned directory contained no files and was preserved under the `.pruned_skeleton` suffix before extraction. This local path is not a portable promise.

Lean reports version `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. The Lean executable SHA-256 is `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`. The bundled, unchanged adapter at `compat/app_path.so` has SHA-256 `fdcc7edf41b2c301abd13ec01041d44eee52148cbf05f2332bc39b23c5862853`; both hashes match the accepted v1.11.0 archive's inherited recovery evidence.

All nine dependency Git revisions match the original runtime manifest and all nine dependency worktrees are clean. Mathlib is pinned at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Eight dependencies expose `lib/lean` caches, comprising 115,098 files; the pinned Cli repository has no such cache. This count excludes the toolchain cache scopes used by the project verifier.

Direct Lean invocation uses `toolchain/bin/lean` with `LD_PRELOAD` set to the bundled `compat/app_path.so`. `LEAN_PATH` joins the eight available `workspace/.lake/packages/*/.lake/build/lib/lean` directories. Both Lean and Lake start; the targeted inner-product and nonsingular-matrix smoke compiles with warnings treated as errors.

`runtime_recovery.json` records actual invocations, outputs, pins, paths, and hashes. `runtime_library_sources.json` preserves the resolved original file identities. `runtime_assembly.log` records the successful seven-part archive checks. `recover_check.py`, `RecoverySmoke.lean`, and `runtime_smoke.log` reproduce the bounded smoke. Recovery does not change production sources, project ledgers, compiler binaries, adapter binaries, or dependency caches, and does not constitute a project replay or declaration audit.
