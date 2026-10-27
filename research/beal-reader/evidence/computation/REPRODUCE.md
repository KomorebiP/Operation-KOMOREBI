# Reproduce the finite Beal evidence

Run commands from the top of the extracted Beal source package. Use Python 3.10 or newer. The current Block 80 scientific replay uses the standard library. Earlier point count scripts use optional NumPy for exact integer acceleration. The independent new audit also needs SymPy.

The authoring environment used Python 3.12.14, NumPy 2.3.5 and SymPy 1.14.0. No scientific test uses floating point arithmetic. Bounds, field bases, character normalizations and precision windows are those of the original releases.

## Current scientific replay

This PowerShell compatible command rebuilds the finite fixture and all four Block 80 scientific JSONs in a private temporary copy. It compares the complete results with the bundled original outputs. It leaves the original inputs untouched.

```text
python -B evidence/computation/portable_science80.py --output local_replay80
```

The separate exact audit checks field basis conversion, the seven conductor self units, stored matrices, supplied target classification, origin invariance and the three symbolic identities.

```text
python -B evidence/computation/independent80_audit.py --output local_independent80
```

The outputs are synthetic linear tests. Neither command supplies an arithmetic global primitive or authenticates its affine target.

## Earlier scientific algorithms

The exact original scientific code and copied inputs are under `inputs/block67` through `inputs/block80`. The reviewed command plans are under `plans`. They contain complete canonical JSON hashes, not expected success flags. The source snapshot byte hashes are in `EXACT_SOURCE_PINS.json`.

An individual direct replay works on Windows, macOS and Linux:

```text
python -B evidence/computation/portable_historical.py --block 70 --output local_replay70
```

Choose a new output name for a repeat. Each program uses private temporary work and removes all declared scientific outputs before regenerating them. Raw large count tables are temporary. Their full JSON hashes and byte sizes are retained in the report. Only two environment fields of the Block 68 backend comparison are omitted, exactly as in its original verifier.

On Linux, the bounded launcher also records a version 2 manifest with input hashes before and after, actual argv, outputs, timestamps, runtime, exit status and effective resource limits:

```text
python -B evidence/computation/run_portable_replays.py --blocks 67 68 69 70 71 72 73 74 75 76 77 78 79 --suffix local_check --workers 1
```

This launcher requests POSIX address space and CPU limits plus Linux CPU affinity. The authoring run was on Linux. The direct commands above are the portable alternative on hosts without those controls. They retain their per command wall time cap but do not assert Linux memory or affinity enforcement.

The original scripts require more time with their standard library count fallback. A timeout is inconclusive. It does not exclude a candidate and does not confirm a finite assertion. Avoid widening a mathematical range merely because an earlier run passed.

## Original archive observations

The `block67-run` through `block80-run` records describe fresh runs of original unchanged archive verifiers. Block 80's run also executed the immediate Block 79 default verifier. That option is not a full earlier chain replay.

These archive mode manifests pin the original Block 80 archive with SHA256 `cd5ed533e11d5d7202afc38293bf47d8134f94b758738d3931a317e808cddc0e`. The complete nested original archive contains third party papers and is excluded from this source distribution. Consequently, repeating archive integrity mode requires supplying that exact original archive. These observed records are preserved and must not be rewritten to claim that the bundled scientific snapshots were their original execution inputs.

The portable scientific records pin only bundled inputs. They can be checked from this source distribution without the excluded archive. They do not reassert its integrity or rerun its archived negative controls.

## Recorded wrapper failure

Block 67's unchanged verifier completed with its documented status `PASS` and exit code zero. It regenerated and compared all eight scientific results and rejected nine deliberate corruptions. The archive wrapper incorrectly required the label `PASS_DECLARED_CHECKS` and therefore exited with a failure after that successful scientific run.

The failed wrapper manifest and traceback remain in `block67-run`. The separately bounded `block67-status-review` verifies the successful subprocess, the eight output hashes, the rejection controls and the unchanged failure record. It does not turn the failed wrapper into a successful wrapper. The separately observed portable scientific replay uses the exact source programs directly.

The original Block 69 archive mode attempt reached its aggregate 840 second wall cap without a final scientific report. That record is resource inconclusive and remains failed. Its status must not be inferred from any later portable run. Details are in `COMPUTATION_FAILURES.md`.

All portable scientific replays for Blocks 67 through 80 completed at their unchanged bounds. Portable69 compared all 17 complete scientific JSONs in475.410396 seconds; portable70 completed in203.785775 seconds. Their manifests retain the actual resource limits and full comparison records.

## Legacy metadata and independent final-guide comparison

The correct Block 71 ring unit count is 2352=49²−7²=49×48. The original primary's hardcoded2304 metadata is preserved and identified as wrong. Its actual loop and separate original result agree on 2352. To reproduce the correction:

```text
python -B evidence/computation/audit_unit_domain71.py --output local_unit71
```

The independent final-guide and reader-data check reads the frozen source pins, complete fresh mathematical results and the metadata correction. It does not import or execute the figure generator:

```text
python -B evidence/computation/audit_reader_data_v2.py --output local_reader_qa
```

It checks the published source data and hashes. It does not newly enumerate the source q11 curves, prove the conditional external theorems or authenticate an arithmetic target. The earlier failed QA used a wrong residue norm in its own h test; that script, contract and failed manifest remain separately preserved. The accepted version uses the all-inert base-field residue norm q².

## What these checks establish

They establish exact finite statements for the declared families and comparison conventions. They verify the current operator, its kernel and cokernel dimensions, and the supplied target evaluator.

The actual arithmetic target is not present. No first stage branch is excluded. The actual upper stage, integral Frey realization, unrestricted conductors and depths, other signature branches and general Beal require separate mathematical arguments.
