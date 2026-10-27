# AVOC Formal v0.13.0 — verification record

## Result

**PASS: 64/64 clean local compilations, 593/593 theorem axiom reports, 17/17 expected negative rejections.**

- 59 new theorem/lemma declarations in five modules.
- Complete corpus: 593 theorem/lemma declarations, 229 definition-like declarations, 10,464 non-audit Lean source lines, 63 non-audit modules.
- The inherited source contains 534 theorem/lemma declarations. The prior reported 512 omitted 22 declarations with inline attributes. See `results/v0.13.0/count_correction.json`.
- Every one of the 58 inherited non-audit modules is byte-for-byte unchanged from v0.12.

## Toolchain and clean scope

Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The portable bundle passed all seven part CRC/SHA checks and combined SHA-256 verification. The new runner verified all nine dependency revision pins. It deleted only the local project build directory and recompiled the 63 local source modules plus aggregate `AVOC.lean` in import order. Cached external dependencies were retained. This is **not a new full-source rebuild of mathlib** and is not reported as a dependency-wide Lake job count.

The first host-limited call was interrupted while entering module 16. It was not counted as success. That unfinished module and the remaining import graph were recompiled; every final per-file record has return code zero and no timeout. No old build log is substituted for this run.

## Full axiom audit

`AVOC/FullAudit.lean` names all 593 declarations. It passes with warnings as errors. The audit parser confirms the exact expected name set. The union of reported axiom dependencies is only:

`propext`, `Classical.choice`, `Quot.sound`.

No project-specific or native-evaluation axiom appears. The source scan finds no proof placeholders, project axioms, `native_decide`, or unsafe theorem-like declarations.

## Deliberately invalid files

All 17 files under `tests/negative/` are rejected with no import failure or timeout. New cases are:

- `FalsePrematureDiamond.lean`: tries to execute the terminal task before its prerequisites, against the proved negative schedule theorem.
- `FalseAntichainReady.lean`: tries to infer readiness from singleton antichainhood despite missing prerequisites.
- `FalseSchedulingProvesTruth.lean`: attempts to derive `False` solely from readiness.

The positive library independently proves the corresponding obstruction statements. Negative proof-script failure alone is not treated as a proof of mathematical negation.

## Independent Python regression

The separately implemented structural planner passes exact tests covering all forward-edge DAG inputs on 0 through 5 vertices (fixed natural topological order). Duplicate transitive closures are skipped:

- 1,100 DAG inputs; 408 distinct dependency orders;
- 5,231 ideal states;
- 160,433 batch characterizations;
- 43,848 complete-order comparisons;
- 15,693 structural plans;
- five invalid graph/state cases rejected.

The oracle uses Floyd-Warshall and bitset predicates; the planner uses recursive prerequisite closure. Neither the bounded experiment nor the Python program is represented as a Lean-extracted implementation. The generic scheduling theorems are established separately by Lean.

## Evidence

Per-file commands, elapsed times, return codes, source hashes and output hashes are under `results/v0.13.0/`. Source and archive integrity are additional packaging checks, not substitutes for the proof checks.
