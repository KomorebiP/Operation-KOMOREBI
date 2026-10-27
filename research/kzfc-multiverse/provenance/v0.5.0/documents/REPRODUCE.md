# Reproduce v0.5.0

## Environment

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Lake 5.0.0-src+6a10ac8.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Use the dependency revisions in lake-manifest.json. Do not update to a different Mathlib revision while claiming to reproduce this record.

The final archive does not include the compiler, compiled dependencies or project build cache. The retained portable Linux runtime contains the pinned toolchain and dependencies. During this run it was restored from the seven Lean_Offline_01.zip through Lean_Offline_07.zip parts. The concatenated tar.zst checksum was:

    66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34

The restore script `scripts/restore_runtime.py --help` documents its arguments. Do not rerun a multi-gigabyte restore when the matching runtime is already present.

## Attach and verify

From the extracted project directory, with a matching portable runtime:

```bash
KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KIT/toolchain/bin:$PATH"
bash "$KIT/run.sh" attach "$PWD"
python3 scripts/run_recorded.py --clean --sequential-build
```

`--clean` removes only this project's .lake/build cache. `--sequential-build` builds the project mathematical modules in topological order, one target at a time, then builds the complete root. It does not impose a general OS-wide thread cap. Every compiler subprocess has a 240-second wall timeout by default. No extra per-process memory, CPU-time or affinity cap is imposed. The recorded environment had a 4 GiB cgroup memory limit and CPU quota equivalent to four cores.

The verifier separately checks all mathematical source files with warnings as errors, enumerates and audits all named theorem declarations, checks the allowed axioms, scans active source for prohibited constructs, verifies unchanged proof-input hashes, and compares the 12 predecessor mathematical modules byte-for-byte. Invalid false-proof and placeholder controls must be rejected for the expected diagnostics.

Success requires both `verification/RESULTS.json` status PASS and `verification/process_record.json` exit_status 0. The verifier clears stale verdicts at startup. An interrupted run is not a fresh verification, even if older historical PASS files remain elsewhere.

## Validate evidence

```bash
python3 scripts/validate_manifest.py verification/computation_manifest.json --root .
sha256sum -c SHA256SUMS.txt
```

The original manifest pins the original run, including times and log hashes. Rerunning verification changes outputs. After a successful rerun, regenerate the evidence manifest with:

```bash
python3 scripts/make_manifest.py
python3 scripts/validate_manifest.py verification/computation_manifest.json --root .
```

Fresh output hashes do not supersede the release checksum list until a new release is intentionally produced. The manifest producer rejects a non-PASS run, a nonzero observed process exit, or changed proof inputs. Manifest validation confirms record integrity, not a new mathematical theorem.

## History

This release's active verdict is unversioned `verification/RESULTS.json`. The v0.4.0 verdict and documents are explicitly historical. The incomplete parallel attempt for this release is under `verification/interrupted_parallel_clean`; the final serial run is complete. The distribution preserves failed elaboration logs as development evidence, without treating them as active theorem source.
