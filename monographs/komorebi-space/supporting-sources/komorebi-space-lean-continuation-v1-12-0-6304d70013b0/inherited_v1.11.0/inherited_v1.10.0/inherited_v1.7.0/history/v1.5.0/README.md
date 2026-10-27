# Komorebi Space
## Coherent realizations, obstructions, and descent

**Expanded monograph edition 1.5.0 · Komorebi P. · 12 October 2026**

The reader set contains a **125-page monograph**, a **39-page visual guide with 36 plates**, and a **34-page Lean/evidence guide**. The monograph has six parts, 33 numbered sections, and five appendices. It retains the accepted version 1.2.0 formal baseline without changing any formal file.

## The bounded-budget extension

Four new chapters provide the positive counterpart to the escaping Hilbert model. Bounded approximate corrections guarantee an exact solution for a bounded linear Hilbert problem. Minimum-norm solutions of nested closed affine constraints converge strongly precisely when their norms stay bounded. The finite-budget residual minimum is attained and has a sharp dual certificate. Quadratic regularization has a unique protected answer at every positive parameter, but its limit can converge to an exact answer, converge only to a least-squares answer, or escape.

The diagonal model is calculated completely. Its optimal asymptotic residual at correction budget M is pi/(4M), while hard prefix repair has leading constant one. Both escape at vanishing residual for the unattainable datum. A second, attainable datum has an explicit deterministic noisy convergence bound.

**WR01–WR12 are complete written proofs, not new Lean declarations.** They have a separate ledger in `data/written_extensions.json`. The existing **80 KS items and 211 source references** retain their accepted source correspondence. No claim is made that all twelve new statements have been formally verified.

## Executable examples and current evidence

`examples/budgeted_repair.py` performs exact rational protected quadratic repair, retaining the Gram matrix of a nonorthogonal kernel basis. It returns the candidate, preserved values, normal-equation residual, actual and fitted residuals, and a symbolic-normalized budget witness with rational squared norms. The diagonal example returns finite sums with rigorously proved tail enclosures.

Six rerun exact suites pass **178,754 assertions**. The new suite contributes **34,388**, nine false-claim controls, and ten invalid-input cases. It includes independent two-dimensional adjugate and ambient KKT oracles. These finite tests do not prove the infinite-dimensional theorems or universal Python correctness.

All **156 formal-tree files** are unchanged. The **retained v1.2.0** record covers 138 production modules plus a root, 139 compilation targets, 4,745 audited declarations, and 1,507 explicit theorem/lemma declarations including auxiliary results. **No new Lean compilation or axiom audit was run.** The official kernel, compiler, permitted axioms, and pinned dependency caches remain trusted.

## Start here

`publication/` contains the three PDFs. `source/` contains the editable manuscript and figures. `formal/` is the unchanged canonical Lean project. `data/claim_ledger.json` indexes KS statements, while `data/written_extensions.json` indexes the new written results. `audit/publication_release_v1.5.0.json`, `REVIEW_NOTES.md`, and `PROGRESS_LEDGER.md` distinguish execution, written proofs, preserved evidence, and restart tasks.

```bash
python3 checks/verify_payload.py
bash build.sh
python3 examples/budgeted_repair.py
```

The publication build does not invoke Lean. See `BUILD.md` for dependencies, JSON input, rendering, and a separate formal replay. No standalone font files or external runtime are distributed.

## Scope

The historical KS54–KS58 formalization tasks remain closed. WR01–WR12 require new formal modules and an actual new replay before Lean coverage can be claimed. This edition does not prove a universal view doctrine, arbitrary higher-stack theorem, unrestricted semantic realization, universal Python refinement, or a new historical-novelty claim.
