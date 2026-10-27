# Reproduction v0.4.0

## Pinned environment

Lean: `leanprover/lean4:v4.34.0-rc2`

Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

All dependency revisions are fixed in lake-manifest.json. Compiler, cached dependencies and build products are not in this source ZIP.

## Existing portable runtime

From the extracted project root, set KIT to the restored Komorebi_Portable_Lean_4.34.0-rc2 directory and run:

```bash
bash "$KIT/run.sh" attach "$PWD"
export PATH="$KIT/toolchain/bin:$PATH"
python3 scripts/verify.py --clean
```

The attachment checks pinned dependency revisions and creates project-local dependency symlinks. The proof sources are not changed. The verifier's clean flag deletes only this project's .lake/build, not the dependency cache. It returns zero only on a complete PASS.

## Restoring the archived offline runtime

The inherited `scripts/restore_runtime.py` is an environment-specific restoration utility, not a general installer. It expects Lean_Offline_01.zip through Lean_Offline_07.zip in /mnt/data/lean_restore, requires zstd and tar, and writes under /mnt/data/lean_runtime and /mnt/data/kzfc_work. Create both destination directories before running it. It streams the ZIP members through zstd/tar and checks the concatenated archive SHA-256 against:

```
66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34
```

Do not use untrusted replacement archive parts. The parts and large runtime are not included in this project ZIP. The actual completed restoration report is verification/runtime_restore.json.

## Independently installed toolchain

With the exact pinned Lean toolchain and dependencies installed:

```bash
lake build Komorebi
python3 scripts/verify.py --clean
```

The verifier has a 240-second limit per compiler command. Increase it explicitly with `--timeout` for a slower host, and retain that changed command and limit in the new result record. No individual theorem is restricted to a finite test range by this execution limit.

## Expected checks

A clean build, 13 source-file rereads with warnings as errors, all 97 named theorem axiom outputs, exact inventory coverage, the standard axiom allowlist, source scan, before/after proof-input hashes, and equality of eight predecessor mathematical modules. The two negative controls must fail with the intended diagnostics, rather than merely failing for an unrelated reason. The final verdict is verification/RESULTS.json.

## Manifest and archive integrity

The final computation_manifest.json pins the actual proof execution inputs and declared outputs. The bundled manifest validator checks these against the extracted project root:

```bash
python3 scripts/validate_manifest.py verification/computation_manifest.json --root .
sha256sum -c SHA256SUMS.txt
```

A manifest PASS checks the evidence record and hashes, not an additional mathematical theorem. A reproduction changes output timestamps and may change durations. It is expected to require fresh output hashes and a new manifest, rather than silently passing the original execution record's hashes.

Historical reports are kept under explicitly versioned directories. Only the unversioned verification/RESULTS.json is this release's active final verdict. The two interrupted synchronous drivers are preserved under verification/interrupted_driver and verification/interrupted_recorded_driver. For an additional top-level exit record, use `python3 scripts/run_recorded.py --clean`. The verifier clears stale verdicts when a new run begins.
