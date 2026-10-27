# Reproduce v0.9.0

## Pinned environment

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Lake 5.0.0-src+6a10ac8.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
All dependency pins are in lake-manifest.json. Do not update them while claiming to reproduce this checkpoint.

The source archive excludes compiler binaries, dependency caches and project build products. The retained portable Linux kit supplies the pinned dependencies. This run restored the seven stored Lean_Offline_01.zip through Lean_Offline_07.zip parts and verified the concatenated tar.zst SHA-256:

    66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34

The optional retained restore script uses fixed /mnt/data paths and has no --help interface. Inspect it before use and do not restore again when the exact runtime is already present.

## Attach and check

From the extracted project directory:

```bash
KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KIT/toolchain/bin:$PATH"
bash "$KIT/run.sh" attach "$PWD"
python3 scripts/verify_staged.py start
# There are 87 compiler commands. Each next call is synchronous.
for batch in $(seq 1 29); do
    python3 scripts/verify_staged.py next --count 3 || exit 1
done
python3 scripts/verify_staged.py finish
python3 scripts/make_manifest.py
python3 scripts/validate_manifest.py verification/computation_manifest.json --root .
python3 scripts/package_release.py
```

In hosts with individual tool-call limits, invoke each batch separately. Never call start between batches. `status` reports the current plan position. Extra `next` calls after the last command, before `finish`, do not repeat compiler commands. The recorded argv determine the actual batch sizes used for the shipped run.

The plan contains Lean/Lake version checks, serial topological builds of 40 mathematical modules, the full root build, separate warnings-as-errors checks of all mathematical modules and the root, the complete 439-name axiom audit, and two negative controls. All 33 predecessor mathematical sources are compared byte-for-byte.

`start` removes active verdict files and project build products, not the dependency cache. It pins sources, dependency configuration, contract and relevant verifier/evidence scripts. Each `next` verifies unchanged inputs and records actual compiler exit status and log hash. `finish` requires full command coverage, expected exits, unchanged inputs, exhaustive theorem-audit coverage, the standard axiom allowlist and predecessor preservation.

Each compiler command has a 120-second timeout. Enclosing host limits may be shorter. Observed cgroup memory is 4 GiB and CPU quota equals four cores. No additional memory, CPU-time, affinity or global thread cap is imposed. Project targets are serial, but dependency cache and compiler platform remain trusted.

A completed run requires RESULTS.json PASS and process_record.json exit_status 0, together with every recorded check and log integrity. The process record describes a staged session, not a single uninterrupted compiler subprocess. Historical build logs cannot establish fresh completion.

The packager validates the manifest, writes SHA-256 hashes, creates a source archive, extracts it separately, checks the exact file set and all hashes, and revalidates the extracted manifest. Archive integrity is not an independent second proof of Lean's soundness.
