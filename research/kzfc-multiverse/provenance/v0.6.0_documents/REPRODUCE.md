# Reproduce v0.6.0

## Environment

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Lake 5.0.0-src+6a10ac8.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Use the dependency revisions in lake-manifest.json. Do not update to a different Mathlib revision while claiming to reproduce this record.

The final archive does not include the compiler, compiled dependencies or project build cache. The retained portable Linux runtime contains the pinned toolchain and dependencies. During this run it was restored from the seven Lean_Offline_01.zip through Lean_Offline_07.zip parts. The concatenated tar.zst checksum was:

    66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34

The inherited restore script `scripts/restore_runtime.py` uses fixed /mnt/data paths; inspect and adapt them before running it. Create /mnt/data/lean_runtime and /mnt/data/kzfc_work first. It does not implement a --help interface. Do not rerun a multi-gigabyte restore when the matching runtime is already present.

## Attach and verify

From the extracted project directory, with a matching portable runtime:

```bash
KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KIT/toolchain/bin:$PATH"
bash "$KIT/run.sh" attach "$PWD"
python3 scripts/verify_staged.py start
# This release has 47 compiler commands, processed in ten batches.
for batch in $(seq 1 10); do
    python3 scripts/verify_staged.py next --count 5 || exit 1
done
python3 scripts/verify_staged.py finish
```

`start` clears active verdicts and only this project's .lake/build cache. It pins every proof input and records a complete command plan. Each `next` executes the next unrecorded commands, checks unchanged input hashes, and records the compiler's actual exit status and log hash. `finish` requires the entire plan to have passed and performs the final audits before issuing PASS. `status` reports progress without starting another verification. The batches can be issued as separate synchronous host calls without restarting the session.

For this release the plan contains 47 compiler commands. A future changed plan may require a different number of batches. Never use `start` between batches. A run interrupted inside a command has no final verdict; that unrecorded command must be rerun by `next`.

Targets build in topological order, one at a time, followed by the complete root. Each compiler command has a 120-second subprocess wall timeout. An enclosing host can impose a shorter limit. No additional process memory, CPU-time, affinity, or general thread cap is imposed. The recorded container has a 4 GiB memory limit and CPU quota equivalent to four cores. The inherited monolithic verifier and recording wrapper remain available but were not the source of this release's completed verdict.
The verifier separately checks all mathematical source files with warnings as errors, enumerates and audits all named theorem declarations, checks the allowed axioms, scans active source for prohibited constructs, verifies unchanged proof-input hashes, and compares the 17 predecessor mathematical modules byte-for-byte. Invalid false-proof and placeholder controls must be rejected for the expected diagnostics.

Success requires `verification/RESULTS.json` status PASS, all 47 actual compiler-command exits matching their expectations, and `verification/process_record.json` exit_status 0 for final staged-session completion. The process record explicitly describes a staged session, not one uninterrupted compiler subprocess. The verifier clears stale verdicts at startup. An interrupted run is not a fresh verification, even if older historical PASS files remain elsewhere.

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

Fresh output hashes do not supersede the release checksum list until a new release is intentionally produced. The manifest producer rejects a non-PASS run, a nonzero recorded completion status, or changed proof inputs. Manifest validation confirms record integrity, not a new mathematical theorem.

## History

This release's active verdict is unversioned `verification/RESULTS.json`. The v0.5.0 verdict and documents are explicitly historical. Two incomplete serial attempts are under `verification/interrupted_serial_clean` and `verification/interrupted_serial_clean_02`. The final clean staged session is complete and has a distinct session ID. Its runtime_seconds includes pauses between batches; compiler_seconds records the sum of compiler-command runtimes. The distribution preserves failed elaboration logs as development evidence, without treating them as active theorem source.

## Memory note for this release

An unused artifact renderer consuming about 1.4 GiB was stopped during development. Another monolithic attempt was still interrupted afterwards, so memory pressure is not established as the sole cause. The completed verification uses serial targets in short, hash-pinned batches. Do not treat an interrupted verifier as a final result.
