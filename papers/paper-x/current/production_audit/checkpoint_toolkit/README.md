# Paper X: verification tooling and recovery checkpoint

**Version 0.1.0 | 19 October 2026 | Operation Komorebi**

## Status

**Verification tooling: tested. Paper X production closeout: blocked.**

This is not a replacement Paper X edition. It contains no recovered October 16–17 mathematical source tree and no newly certified Paper X production theorem. The previously reported 122-module build and 39 companion tests have not been reproduced or authenticated here.

The new work restores the exact offline Lean runtime, implements and tests an owning-module transitive-axiom auditor, and records a complete set of compiler and evidence-handling controls. The October 11 package was found, but it was not used as the current source or included as a substitute.

## Executed scope

| Check | Result |
|---|---|
| Seven offline archive chunks and combined archive | Matched the supplied SHA-256 pins |
| Lean executable | Exact 4.34.0-rc2 executable pin matched |
| Runtime dependency HEAD comparisons | 9 of 9 matched the recovered manifest |
| Actual compiler fixture cases | 18 passed, in 5 complete disjoint batches |
| Positive audited fixtures | 4 |
| Compiled fixtures rejected by axiom or declaration policy | 9 |
| Invalid proof or placeholder fixtures rejected by the compiler | 5 |
| Python unit and receipt-mutation tests | 64 passed, no failures, errors or skips |
| Paper X production modules checked in this checkpoint | **0** |

There are 41 recorded Lean process invocations across the accepted compiler batches. These include repeated compiler-version probes and auditor builds. They are not 41 distinct mathematical results. Failed and interrupted pilots do not contribute to the accepted case count.

## Contents

`lean/AuditCore.lean` is the auditor source. `scripts/audit_engine.py` runs bounded processes, handles source pins and parses exact audit records. `scripts/run_compiler_controls.py` freshly compiles the isolated fixtures. `scripts/verify_control_evidence.py` rechecks saved fixture receipts and logs without invoking Lean again. `scripts/run_unit_tests.py` executes the Python tests. `scripts/verify_checkpoint.py` checks this checkpoint's manifest and recorded controls.

`evidence/controls/` contains the accepted source-bound compiler runs. `evidence/failed_attempts/` preserves development failures and exact repair diffs. `evidence/runtime/` contains archive and dependency pins, not the runtime binaries. `evidence/RECOVERY_STATUS.json` records the unresolved Paper X source selection. The historical Library inventory was searched locally, but only Paper X candidate metadata is included here. Unrelated Library contents are not redistributed.

## Reproduce the checks

Run from this extracted checkpoint directory, using Python 3.10 or later:

```bash
python -B scripts/verify_checkpoint.py
python -B scripts/run_unit_tests.py --out ../paper-x-tool-tests-new
```

The second command requires a new output directory. The first authenticates recorded evidence. The second executes the Python tests, including mutations of copied evidence.

For a fresh real-compiler control run, use the already extracted **Linux x86-64** portable runtime:

```bash
python -B scripts/run_compiler_controls.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --work ../paper-x-controls-new
```

The default runs all 18 cases. In an execution environment with short outer call limits, use separate new work directories and the disjoint inclusive ranges `--first 1 --last 3`, `4–6`, `7–9`, `10–12`, and `13–18`. A successful subset is not a complete-suite result. Each report records its complete inventory and selected range. The preserved accepted suite uses exactly those five ranges.

No command installs dependencies or downloads files. The runtime is deliberately not bundled. A full Mathlib import, a cold upstream rebuild, native Windows operation and a new Paper X production build were not tested. On Windows, this Linux runtime requires a compatible Linux environment such as WSL.

## Audit policy and limits

Declarations are selected by owning module, not by the spelling of their namespace. The census includes private and generated kernel declarations visible in the imported environment. Explicit targets must exist, have the stated declaration kind, and belong to the stated owner. Lean's `collectAxioms` computes their transitive axiom dependencies under the pinned toolchain. Only `propext`, `Classical.choice` and `Quot.sound` are permitted by this policy.

A custom axiom can compile successfully in Lean. Such a fixture must subsequently be rejected by the audit policy. A timeout, signal termination, launch failure or unrelated error is never accepted as the intended negative control. The parser requires successful process completion and an exact final census event. It rejects duplicate records, inconsistent counts, forbidden axioms and missing target correspondences.

These tests establish the behavior of the delivered verifier on the stated finite control suite. They do not establish that an arbitrary manuscript and Lean statement have the same mathematical meaning. They are not an independent kernel implementation, a formal proof of the Python verifier, a cold rebuild of external dependencies, or a security sandbox for malicious Lean metaprograms. Authenticity still depends on trusted source and runtime pins, actual compiler execution, and appropriate review of the selected source.

## Resume Paper X

Recover and authenticate the following latest artifacts before selecting production sources:

- `Paper_X_Reviewed_With_Lean_Check_2026-10-16.zip`
- `Paper_X_Review_Evidence_2026-10-16.zip`
- `Paper_X_Reviewed_Readers_2026-10-16.zip`, for final reader reconciliation

Then establish the exact source manifest, import closure, statement correspondence and dependency pins. Build fresh project objects in a new directory. The compiler controls here deliberately put no old Paper X objects on `LEAN_PATH`. Generate a request through `audit_engine.audit_source(owners, targets)`, compile `AuditCore.lean`, and run the request on the newly built objects with warnings treated as errors. Resolve the complete owned census and the explicit manuscript targets, rerun the actual Paper X companion tests, then verify the final frozen archive by fresh extraction.

Do not infer an isomorphism between two separately constructed witnesses. Do not infer nonzero occupancy from zero multiplicity. These boundaries have positive and negative fixture controls in this package, but Paper X's actual conditional hypotheses still require their own semantic review.

## Distribution

`MANIFEST.json` covers every file except itself. The separately delivered receipt covers the frozen ZIP and its fresh extraction, avoiding a circular archive digest. Hashes provide integrity against the supplied pins, not independent evidence of the correctness of the mathematics. No font files, external runtime installation, older paper replacement, or new project-wide licensing decision is included.
