# AVOC v0.38.0 — verification record

## Status

**PASS within the stated formal and bounded executable scopes.**

## Formal corpus

| Item | Result |
|---|---:|
| Inherited theorem/lemma declarations | 1,920 |
| New theorem/lemma declarations | 124 |
| Complete exact-name inventory | **2,044** |
| Non-audit AVOC modules | 180 |
| Non-audit AVOC Lean lines | 30,271 |
| Local source/executable targets | **205/205 passed** |
| Exact theorem axiom reports | **2,044/2,044 passed** |
| Deliberately invalid Lean files | **111/111 substantively rejected** |
| Inherited non-audit modules | **174/174 byte-identical to v0.37** |
| Positive-source forbidden shortcuts | **Zero hits** |

The axiom union is exactly:

```text
propext
Classical.choice
Quot.sound
```

No `sorry`, proof-tactic `admit`, project-specific axiom, `native_decide`, or unsafe theorem-like declaration was accepted in the positive source scan.

## Clean local build

The local `.lake/build` directory was removed before the release rebuild.  Every AVOC source module, aggregate `AVOC.lean`, and Lean executable entrypoint was compiled directly with warnings treated as errors against the nine exact pinned external dependency caches.

`results/v0.38.0/local_build_summary.json` records:

```text
205 targets
205 current successes
0 bad records
```

The aggregate `AVOC.lean` target is included in those 205 targets.

Several additional `lake build` frontend invocations were attempted after the complete direct rebuild.  They repeatedly exceeded the host's long-command limit while rebuilding cached targets.  They are recorded as inconclusive and are **not** counted as release evidence.  A final complete direct rebuild restored and revalidated all 205 local target records.

External dependency caches were retained.  Lean, mathlib, and their dependencies were not rebuilt from all source, and no independent Lean kernel implementation was used.

## Exact-name axiom audit

`AVOC/FullAudit.lean` imports the aggregate library and issues `#print axioms` for every inventoried theorem/lemma.

Final audit:

- reports: 2,044;
- unique reports: 2,044;
- expected names: 2,044;
- missing: 0;
- extra: 0;
- duplicates: 0;
- unexpected axioms: 0.

## Negative suite

The complete negative suite contains 111 files.  Each was run through the project environment with the local AVOC object path and pinned dependency path.

Final result:

```text
111 / 111 substantive rejections
```

In particular, the formerly inconclusive files

- `FalseFreeRankProbe.lean`
- `FalseProposalPromotion.lean`

were rerun sequentially and reached substantive rejection.

The inherited v0.37 negative wrapper had previously allowed bare-Lean module-path failures.  Such errors were not counted.  The v0.38 runner explicitly excludes timeouts, unknown modules, missing object files, missing executables, and absent records.

Eight new adversarial files reject false claims about interval exactness, overlapping-band dominance, out-of-band artifacts, changed quote evidence, infrastructure faults, unselected-artifact mutation, duplicate acknowledgement charging, and premature singleton collapse.

## Executed robust-quote regression

The independent Python oracle uses exact `fractions.Fraction` arithmetic and a separate finite dynamic-programming implementation.

Final record:

| Check | Result |
|---|---:|
| Lean planning comparisons | **21 passed** |
| Compatible exact realizations enumerated | **1,523 passed** |
| Exact collapse | Passed |
| Uncertainty-induced action change | Passed |
| Certified dominance | Passed |
| Interval overlap without dominance | Passed |
| Artifact inside/outside bounds | Passed |
| Identity mutation | Rejected |
| Fault separation | Passed |
| Unfinished intent | Rejected as non-evidence |
| Recovery and duplicate acknowledgement | Passed |

This is bounded implementation evidence, separate from the universal Lean theorems.

## Selected-only workflow

Two normal workflow cases passed:

- warm-selected execution with the cold artifact path absent: warm calls 1, cold calls 0;
- cold-selected execution with the warm artifact path absent: cold calls 1, warm calls 0.

The SQLite transaction records the exact selected transition and quote evidence.

## Recovery regression

A controlled interpreter exit was injected after warm-result commit and before acknowledgement.

Recovery:

- acknowledged the committed result;
- retained the checked warm artifact and refined evidence;
- did not invoke the warm external operation again;
- kept cold external calls at zero;
- made duplicate resume exactly idempotent.

This is process-interruption evidence, not electrical power-loss, malicious rollback, or universal SQLite/Python refinement certification.

## Inherited lazy-staged regression

The v0.37 warm, cold, invalid-boundary, and crash-recovery cases were rerun separately against the final environment.  All four passed.

## Source lineage

The sole authoritative verified predecessor is `AVOC_Formal_v0.37.0.zip`.  All 174 inherited non-audit AVOC modules are byte-identical.

The complete v0.36 source archive was unavailable.  v0.37 records reconstruction from complete v0.35 source plus retained v0.36 specification.  v0.38 preserves that boundary and does not describe missing v0.36 source as independently verified.

## What this verification does not establish

- empirical coverage of supplied quote probability bands;
- calibrated setup/gross/call-count models for production workloads;
- correctness of Python, SQLite, filesystem, OS, or physical host;
- arbitrary Lean/mathlib artifact checking;
- automatic paid retry of unfinished robust-quote intents;
- hostile rollback or distributed exactly-once execution;
- real LLM productivity, autonomous discovery, or universal optimal AI use.
