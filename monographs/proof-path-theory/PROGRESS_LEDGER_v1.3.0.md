# Proof Path Theory 1.3.0 — progress ledger

## Completed

The full 1.2.0 manuscript has been read, reorganized, and proofread. The monograph
has five parts, a preface and reading guide, coherent theorem references, 14
retained figures, notation and hypothesis guidance, all 33 stable result IDs,
and a complete importable JSON example.

Uniform task sufficiency and leaf-relative least certificate pairs are stated
precisely. Graph, covariance, cost, refinement, and experimental-design
hypotheses have been tightened. The AND-DAG leaf-boundary and exact-cost-selection
bugs are fixed and covered by regression tests. All 111 current tests and the
finite exhaustive/comparison checks pass.

## Formal verification status

Eight production modules and their earlier evidence are unchanged. Identity is
checked by `scripts/verify_editorial.py`. This edition did not run Lean. Its
compiler evidence is inherited from technical release 1.2.0, which remains in
the historical record. The complete manuscript is not Lean-formalized.

## Remaining obligations

A future technical release may formalize the corrected core and uniform-decoder
interfaces not already covered, verify implementations against their abstract
specifications, and perform a new integrated compiler run. Any such run must be
recorded independently of the inherited evidence. Independent mathematical
review, empirical tests of interpretation models, and license selection remain
separate tasks. No claim that all future theory is finished is made here.

## Restart point

Use this full 1.3.0 package. Read `PROOFREADING_REPORT.md`, the stable CSV ledger,
and `editorial/result_crosswalk.csv` before editing. Preserve the inherited
`formal/` and `evidence/lean/` records before a new compiler invocation. The
current delivery evidence is in `data/editorial_verification.json`.
