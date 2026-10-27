# Large Signal Model Lean — persistent progress ledger

**Current: 0.9.0 · Frozen theory: 1.0.0 · 35 complete / 87 · 52 outstanding.**

## Versioned completed work

| Block | New numbered mappings | Cumulative complete | Remaining |
|---|---|---:|---:|
| 0.1.0 | P1, P2, P4, P5, P6, P7, P10 and P22; P3 was partial | 8 | 78 unformalized and 1 partial |
| 0.2.0 | P3 and P8 | 10 | 77 |
| 0.3.0 | P9 and P12 | 12 | 75 |
| 0.4.0 | P26 and P36 | 14 | 73 |
| 0.5.0 | P27, P28 and P30 | 17 | 70 |
| 0.6.0 | P29 and P38–P41 | 22 | 65 |
| 0.7.0 | P42–P44 | 25 | 62 |
| 0.8.0 | P13 and P18–P21 | 30 | 57 |
| 0.9.0 | P14–P17 and P25 | 35 | 52 |

The rows are historical records. The current source-candidate run rebuilds the cumulative active source and replays all 74 project modules. Counts are neither difficulty weighted nor novelty claims.

## Completed in Block 9

Actual finite delay maps, quotient transitions, rank closure and causal all-horizon output. Exact data-span interpolation, ambient extensions, nonidentification outside a sampled span, and a constructed orthogonal pseudoinverse satisfying the four Penrose conditions. A variational singular-value definition with unit-sphere equivalence, strict perturbation rank preservation, pseudoinverse norm control, and the complete identification error identity. Universal rational nilpotent finite-prefix counterexamples. Conditional data-only recovery, atlas and packet preservation, actual noisy rollouts, contraction and decoder bounds.

Seven modules add 64 named theorems, including nine example-module theorems. Six negative controls test the assumptions most likely to be overclaimed. The theory and production software are unchanged.

## Verification

The accepted source run completed 218 stages: 75 compiled targets, 1,256 explicit axiom records, 74 project kernel replays, and 68 expected proof rejections. The separate metadata suite passes 72 checks. Permitted axiom identities remain `propext`, `Classical.choice`, and `Quot.sound`.

Development records contain 36 invocations, 20 successful and 16 failed. The failed attempts and source snapshots remain available. The new guide describes the main repairs. The existing runtime was reused after exact compiler/dependency pin checks, with its documented executable-path adapter.

All predecessor source and control identities are preserved. The delivered ZIP is verified from a separate extraction. Its actual outcome and exact archive hash are in the external delivery verification report, not inferred from this ledger.

## Open obligations and restart

P45 is next: exact rational certificate search under the frozen statement's hypotheses. P32–P34 remain in the identification/stability track. `ROADMAP_1.0.json` lists all 52 remaining propositions exactly once. Noncomputable pseudoinverse construction does not close P45.

## Publication and unexecuted scope

`PUBLICATION_STATUS.md` dates the old release-candidate and no-Lean sentences. The frozen source hashes and existing PDFs are unchanged. No new typeset revision, license change, model training, empirical coverage experiment, production-code verification, independent referee, second prover, exhaustive upstream Mathlib replay, Windows wrapper run or external publication is claimed.
