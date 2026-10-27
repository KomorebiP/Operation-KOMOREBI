# Runtime and reproduction boundary

Recorded compiler: Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
All nine dependency revisions are recorded in the successful receipt and pinned manifest.

The five user-provided `Lean_Compact_01.zip` through `Lean_Compact_05.zip` files were recovered from the Library. Their byte fragments were concatenated and the resulting XZ archive was fully extracted. The operation records 166,035 archive members. Actual hashes are in `evidence/runtime_restoration.json`. The combined archive SHA-256 is `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.

The verifier matches the actually imported upstream object parts and selected compiler/shared-library binaries against the runtime's existing file inventory. It records the inventory's own SHA-256 and every checked artifact. This is consistency with a preserved distribution, not a new cryptographic origin attestation or a source rebuild of Lean and Mathlib.

The runtime is not included in this small research ZIP. The primary tested route is Linux x86_64 with the restored runtime and its package cache. No Windows execution, new package downloads, GPU work, or hosted repository changes are claimed.

Lean compilations use one thread, warnings as errors, an internal 3,072 MiB memory limit and a 45-second per-command wall allowance. This is not a separately enforced operating-system memory cap. Local same-kernel module replays are serial and reuse the same imported dependency objects.

Block 02 recovered and revalidated the same five-part runtime in this session. The new receipt is `evidence/runtime_restoration_block02.json`. The preceding receipt remains historical. Current cold builds, API, axiom and replay gates are in `evidence/final02` and `evidence/fresh02`.

Block 03 recovered the same five-part archive and recorded the actual concatenation and extraction in `evidence/runtime_restoration_block03.json`. Its combined SHA-256 again equals the preceding expected value. The current local production gates are `final03` and `fresh03`. Per-command timeouts now kill the command's process group. The outer supervisor's whole-gate wall limit is 900 seconds, with no change to the 45-second per-command limit or proof acceptance policy.

Block04 recovered and revalidated the same five parts. Its receipt is `evidence/runtime_restoration_block04.json`; current proof gates are `final04` and `fresh04`. No runtime bytes are included. The command and outer limits are unchanged from Block03.

Block05 found the saved parts already mounted but the runtime not extracted. A materialization attempt returned file-exists warnings, after which the existing parts were used. The supplied assembler reverified chunks and archive hash and extracted the same runtime. Current artifact validation is recorded in `evidence/runtime_restoration_block05.json`; current proof gates are `final05` and `fresh05`. No runtime or font binaries are included.

Block06 found the compact parts mounted after a file-exists materialization response. The inspected supplied assembler checked every chunk and the full archive, then extracted the same pinned runtime. Its recorded archive hash and restoration log are in evidence/runtime_restoration_block06.json. Runtime and standalone font binaries are not distributed.

## Block 13 runtime reuse

Block 13 reused an already extracted copy of the same runtime. All nine actual git revisions and the chosen compiler/shared-library artifacts matched the preserved distribution. No runtime extraction, upstream source rebuild, or change to shared runtime files was needed. The recovery record is `evidence/runtime13/recovery.json`.

This host requires the distribution's `compat/app_path.so` adapter for executable-path discovery. The adapter is supplied through `LD_PRELOAD` and its hash is checked against the distribution inventory alongside the compiler. A typical command on this host is:

```bash
LD_PRELOAD=/absolute/runtime/compat/app_path.so python3 scripts/verify.py --runtime /absolute/runtime --out evidence/my_replay
```

The old 3,072 MiB Lean limit failed when loading the measure-theoretic conditional-expectation library. The same smoke compiled and replayed at 4,096 MiB. Block 13 therefore uses `-M4096` for Lean compilation, retains warnings as errors and the 45-second command timeout, and records that it is an internal limit rather than a separately enforced operating-system cap. The successful smoke does not itself verify the new theorem. Only the completed block gates do that.
