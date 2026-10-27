# Current status — v0.9.0

Base: the exact supplied v0.8.0 PDF, TeX, and full package. See `audit/base_sha256.json`. Current PDF: 86 pages. The source retains all 126 inherited theorem/lemma/proposition/corollary/proof blocks verbatim. This preservation check is not a fresh proof audit of those blocks.

## New written results

| ID | Result | Essential restriction |
|---|---|---|
| K53 | Natural kernel–reduction exact sequence | Finite free lattices over Z_p; target torsion-free |
| K54 | Sharp finite precision window | The same fixed integral linear constraints; exact Smith/rank data |
| K55 | Invariant-vector residual is H¹[p^n] | Supplied lattice action of a finite group |
| K56 | Lifting equivariant maps and isomorphisms | Both integral lattices/actions already supplied |
| K57 | Norm-quotient lattice family | Finite cyclic group, explicit integral action |
| K58 | Perfect-base derived comparison | Coefficient target perfect over source |
| K59 | Nonzero canonical derived exchange | Odd p, Z/p²→F_p, invertible J, unbounded derived categories |
| K60 | One-step representation nonlifting | The specified I+pJ action cannot lift to p³ |
| K61 | Exact exchange for coefficient-lifted inputs | R and S perfect over a common O; actual lift N supplied |

Proofs: `proofs/intrinsic_arithmetic_exchange.tex`, manuscript Sections 16–17, pp. 47–56. The proofs received self-review, not an independent referee review or Lean verification.

## Verified computational scope

All four deterministic finite regression suites passed. The new suite checks 625 integer matrices in 3,125 matrix/precision cases, 2,500 finite lifting-window cases, 25 intertwiner pairs, 2,544 invertible mod-p action matrices, 3,107 next-level lifts of three selected matrices, and four independently implemented bar-resolution fixtures. Exact families and exclusions are in `checks/intrinsic_results.json`; execution provenance is in `checks/all_runs.json`.

## Important negative results retained

- Ordinary invariants are not exact; their defect is not automatically a defect of fully derived invariants.
- The canonical derived comparison is an equivalence for perfect coefficient change.
- The nonperfect finite-level counterexample has an unbounded defect. An exact functor killing it kills Perf(k); killing all of D(k) additionally requires preservation of coproducts.
- The counterexample's action does not extend even to the next coefficient level.
- A nonzero comparison cone obstructs a supplied coefficient lift. The converse has not been proved.
- Earlier ordered-filtration independence remains refuted.

## Next executable mathematical target

Formulate a sufficient lifting criterion for a specified finite-group representation tower. Separate the obstruction for lifting vectors or intertwiners under fixed constraints from the obstruction for lifting the constraints/group action itself. Compare the canonical exchange cone with explicitly defined relation/deformation obstruction classes. Do not silently turn K61's necessary condition into an equivalence.

K17 arithmetic/automorphic reciprocity, K18 Lean formalization, arbitrary higher-coherent rewriting, and the nonadditive universal construction remain open in this project. No automorphic realization is obtained from these finite-group examples.
