# Version 1.7.0 preservation note

Both formal source trees and their accepted historical evidence are retained unchanged. This proof-exposition release performs no Lean compilation or axiom audit. The 67 expanded proof blocks and five classical analytic lemmas do not change any evidence status. The following version 1.6.0 scope review is retained as the account of that focused execution.

---

# Formal, written, and implementation scope — 1.6.0

The canonical `formal/` tree is unchanged from the accepted v1.2.0 baseline. A new, separately located `extension/` tree has its own focused replay. Those records have different scopes and must not be combined into a claim of a new full cumulative build.

## Evidence layers

| Layer | Scope |
|---|---|
| Retained canonical Lean | 138 production modules and root; historical 139-target accepted replay, 4,745 audited declarations and 1,507 explicit named theorem/lemma declarations. |
| Retained KS correspondence | 80 exposition IDs and 211 source references, bound to unchanged accepted canonical sources. Editorial correspondence, not proof by translation. |
| New focused Lean | Three new modules, three actual inherited dependencies, and root; fresh seven-target replay and imported axiom audit. Exact counts and accepted receipt are in `audit/extension/release.json`. |
| Complete focused WR counterparts | WR06/WR07/WR13/WR14 principal universal statements. Printed scalar examples and coordinate interpretations are separately scoped. |
| Partial focused WR counterparts | WR09/WR16 pointwise data and solver inequalities. Their limiting consequences still use written WR08. |
| Written-only WR groups | WR01–WR05, WR08, WR10–WR12, WR15. Complete printed proofs, no assigned new typed coverage. |
| Exact finite implementation | Seven finite suites, including an independent inexact-certificate verifier oracle. Not universal Python refinement. |

The prior KS54–KS58 closure remains intact. The focused source inventory includes auxiliary definitions and lemmas, not counts of mathematical discoveries. Generated declarations are included in the imported axiom audit but not in the lexical explicit-theorem count.

## Actual mathematical interfaces

The new construction uses real Hilbert spaces and a positive parameter. Its inverse comes from a proved coercive continuous bilinear form through the pinned Lax–Milgram theorem. It does not assume a regularized optimizer as input. The bridge uses the original `ProtectedHilbertRepair.restricted` operator on the actual protected kernel, with the inherited metric. Its adjoint is identified with the ambient adjoint projected to that kernel.

The normal residual certifies distance to the optimizer at the chosen parameter. The fit residual instead reports agreement with data. The duality gap brackets the global objective without first solving the problem. None of these statements, by itself, proves existence of an exact unregularized realization or correctness of a measured datum.

The manuscript's coercive inverse proof uses a self-adjoint closed-range argument, while Lean uses the equivalent bilinear-form theorem. The principal result and optimizer are unchanged. WR07's typed budget formulation is the universal competitor inequality plus an explicit attaining correction and support witness, rather than a second independent implementation of the written numerical profile.

## Inexact and coordinate boundaries

The universal normal-residual inequalities and two-square primal/dual identity are typed. The finite-basis identity `q^T G^-1 q` and invertible basis-change invariance are printed and exactly tested, not newly Lean-formalized. The pointwise solver/data triangle estimate is typed, but passing to a vanishing parameter uses the still-written regularization limit theorem.

The exact rational program verifies a complete permitted basis, exact preservation, a normal covector, its Gram-corrected Hilbert norm, and arbitrary dual witnesses. Its independent regression oracle uses determinant-based full ambient constrained equations. It does not infer infinite-dimensional convergence from finite examples or treat a small residual as an existence theorem.

## Interrupted and failed work

`audit/formal/baseline16/` remains INTERRUPTED. It is not a completed current cumulative replay. The first focused attempt compiled all seven sources but timed out during axiom/type export and remains FAIL. Later accepted execution must be read from the focused release summary. Development failures and exact snapshots are retained; no new project axiom or admitted theorem bypassed them.

## Trust boundary

The official Lean compiler/kernel, standard axioms `propext`, `Classical.choice`, `Quot.sound`, and pinned imported caches are trusted. No independent kernel, full-source mathlib rebuild, native Windows run, or universal Python refinement was performed. Universal view doctrines, general infinity-stacks and unrestricted semantic realization remain separate questions.
