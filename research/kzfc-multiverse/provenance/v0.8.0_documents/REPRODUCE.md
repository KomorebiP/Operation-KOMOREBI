# Reproduce v0.8.0

## Pinned environment

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Lake 5.0.0-src+6a10ac8.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
All dependency pins are in lake-manifest.json. Do not update them while claiming to reproduce this checkpoint.

The archive excludes compiler binaries, dependency caches and project build products. The retained portable Linux kit contains the required dependencies. It was restored from Lean_Offline_01.zip through Lean_Offline_07.zip in this run. The verified concatenated tar.zst hash is

    66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34

The restore script uses fixed /mnt/data paths. Inspect it before use. It has no --help interface, and requires /mnt/data/lean_runtime and /mnt/data/kzfc_work to exist. Do not restore again when the exact runtime is already present.

## Attach and run

From the extracted project directory:

```bash
KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KIT/toolchain/bin:$PATH"
bash "$KIT/run.sh" attach "$PWD"
python3 scripts/verify_staged.py start
# In v0.8.0, 73 compiler commands fit into batches of at most three.
for batch in $(seq 1 25); do
    python3 scripts/verify_staged.py next --count 3 || exit 1
done
python3 scripts/verify_staged.py finish
python3 scripts/make_manifest.py
python3 scripts/validate_manifest.py verification/computation_manifest.json --root .
```

Calls may be made as separate synchronous host invocations. Do not call start between batches. status reports progress. start deletes active verdicts and project build products and pins proof inputs, predecessor source files, contract and relevant verification/evidence scripts. next checks unchanged hashes and records each actual compiler exit and log. finish requires the complete plan and all integrity checks before publishing a verdict.

The 59 commands include Lean/Lake versions, topologically ordered project builds, the complete root, separate warnings-as-errors elaboration of every mathematical module, the all-theorem axiom audit, and deliberately invalid false-proof and placeholder controls. Supporting checks verify all 378 theorem names, the standard axiom allowlist, a prohibited-source-construct scan, unchanged input hashes and all 26 predecessor mathematical modules.

Each compiler subprocess has a 120-second timeout. Host limits can be shorter. The observed environment has 4 GiB cgroup memory and a CPU quota equivalent to four cores. No additional process memory limit, CPU-time limit, affinity or global thread cap is imposed. Project build targets are scheduled serially. The dependency cache is trusted and not rebuilt.

A completed run requires RESULTS.json status PASS, every expected compiler outcome, matching log hashes, and process_record.json exit_status 0. The process record describes a staged session, not one uninterrupted subprocess. No historical PASS elsewhere establishes current completion.

Two v0.8 audit batches of five compiler commands hit the enclosing host limit after four completed records in each batch. The staged plan resumed at its next unrecorded command using batches of three. Completed compiler commands remain hash-pinned; no interrupted command is counted as a success.

## Packaging and provenance

After a completed run and regenerated manifest:

```bash
python3 scripts/package_release.py
```

The packager verifies the manifest, writes per-file SHA-256 hashes, creates a source-only archive, extracts it to a separate directory, checks the exact file set and every checksum, and validates the extracted manifest. The separate ARCHIVE_CHECK.json reports integrity, not a second independent mathematical proof.

The shipped SHA256SUMS.txt pins the shipped run. A rerun changes logs and is not expected to match the original output hashes. Regenerate and validate evidence rather than treating those old hashes as a fresh verdict.
