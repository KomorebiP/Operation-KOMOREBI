# Reproduce v0.10.0

## Pins and source boundary

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Lake 5.0.0-src+6a10ac8.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

All dependency pins are in lake-manifest.json. The distribution excludes compiler binaries, dependency caches and build products. The retained portable Linux kit supplies the exact dependency cache.

Runtime restoration from the seven retained offline parts verified the concatenated tar.zst SHA-256:

    66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34

The restored runtime's report and output are in provenance/runtime_restore_v0.10.0.json and .log. The predecessor source archive is retained as provenance/predecessor_v0.9.0.zip.

## Attach and verify

From the extracted project directory:

```bash
KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
export PATH="$KIT/toolchain/bin:$PATH"
bash "$KIT/run.sh" attach "$PWD"
PYTHON=/usr/bin/python3
"$PYTHON" scripts/verify_staged.py start
for batch in $(seq 1 35); do
    "$PYTHON" scripts/verify_staged.py next --count 3 || exit 1
done
"$PYTHON" scripts/verify_staged.py finish
"$PYTHON" scripts/make_manifest.py
"$PYTHON" scripts/validate_manifest.py verification/computation_manifest.json --root .
"$PYTHON" scripts/package_release.py
```

Use a plain Python interpreter with the standard library. In this host, the virtual-environment Python had an unrelated spreadsheet startup hook consuming memory; the completed run used /usr/bin/python3.

Each next call is synchronous. In a host with shorter enclosing tool limits, invoke batches separately or keep the actual subprocess handle and observe its exit before proceeding. Do not call start between successful batches. The plan can resume only with exactly matching pinned inputs. Extra next calls after the last planned command do not repeat compiler work.

## Audit coverage

The plan has 103 compiler commands: version checks, topological builds of all 48 mathematical modules, the full root build, separate warnings-as-errors elaboration of each module and the root, the exhaustive 502-name axiom audit, and two deliberately failing controls.

The finalizer requires all command outcomes, log hashes, before/after input hashes, source scanning, named-theorem audit coverage and standard axiom allowlist. It also compares all 40 predecessor mathematical modules byte-for-byte.

Start clears the project's .lake/build products and all active verdict files. The pinned dependency cache is reused. The active theorem inventory includes supporting and syntax-interpretation lemmas, not only independent central results.

## Evidence and interruptions

The final completed session is identified by verification/process_record.json and RESULTS.json. The process record describes completion of a staged session, not one uninterrupted compiler subprocess. The command plan and every accepted compiler exit are recorded.

An earlier startup-interrupted run is retained under verification_history/v0.10.0_interrupted_startup. A later outer timeout is recorded in development_v0.10.0/verification_outer_timeout.json. No incomplete compiler command was credited; resumption repeated the unrecorded command from the stored boundary. The final next batch's actual zero exit was observed.

## Resource and trust boundary

Per-compiler-command timeout: 120 seconds.
Observed cgroup limit: 4 GiB memory and CPU quota of four cores.
Project targets are serial. No extra process memory, CPU-time or affinity cap is imposed.
Unused spreadsheet startup helpers were stopped before completion of the Lean-only audit.

Compiler/kernel, ambient Lean axioms, pinned dependencies/cache and platform remain trusted. Checksums and manifest validation verify provenance and record integrity, not an independent proof of Lean soundness.

The packager requires a completed PASS and manifest, writes all source/evidence hashes, creates the ZIP, extracts it separately, checks the exact file set and checksums, and validates the extracted evidence manifest.
