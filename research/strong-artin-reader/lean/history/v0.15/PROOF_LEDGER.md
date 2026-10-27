# Proof ledger — Strong Artin Lean v0.15

## Evidence label

All statements below are **Lean-checked as written** under the pinned Lean/mathlib environment. They are abstract linear-algebraic selection theorems. Their arithmetic instantiation remains open.

## `AdaptiveAuxiliarySelection.lean`

Definitions:

- `selectedKernel`
- `evaluationMap`

Checked theorems:

1. `mem_selectedKernel`
2. `selectedKernel_empty`
3. `selectedKernel_insert_le`
4. `exists_fresh_probe_strict_drop`
5. `exists_fresh_probe_finrank_drop`
6. `exists_finite_auxiliary_superset`
7. `exists_finite_auxiliary_set`
8. `evaluationMap_apply`
9. `ker_evaluationMap`
10. `selectedKernel_eq_bot_iff_evaluationMap_injective`
11. `finrank_le_card_of_evaluationMap_injective`
12. `exists_finite_auxiliary_set_exact`

### Mechanism

For a nonzero current kernel, choose `v ≠ 0` in it. A detecting probe `i` cannot already be selected, because all selected probes vanish on `v`. Adding `i` removes `v`, hence strictly shrinks the kernel. Strong induction on its finrank terminates after at most the current dimension.

The simultaneous evaluation map has kernel exactly `selectedKernel`. Its injectivity forces the number of scalar coordinates to be at least the source finrank. Combined with the constructive upper bound, the selected set has exactly the active dimension.

## `GoodAuxiliarySelection.lean`

Checked theorems:

13. `exists_finite_good_auxiliary_set_exact`
14. `exists_fresh_good_probe_strict_drop`
15. `exists_finite_good_auxiliary_superset`

### Mechanism

The good-label theorem first restricts to the subtype of labels satisfying the arithmetic predicate, then returns to the original label type without losing cardinality. The adaptive theorem directly preserves goodness at every insertion.

## `RelativeTaylorWilesFiniteSet.lean`

Structure:

- `OnePrimeSelectionInterface`

Checked theorems:

16. `extend_to_relative_TaylorWiles_set`
17. `exists_relative_TaylorWiles_set_exact`

### Formal conclusion

Given a finite-dimensional transverse dual-Selmer vector space `H` and an arithmetic one-prime interface whose scalar local functionals detect every nonzero class, there is a finite admissible set `Q` such that

```text
Q.card = finrank k H
selectedKernel localFunctional Q = ⊥
evaluationMap localFunctional Q is injective.
```

## Axiom audit

The displayed capstones depend only on ordinary Lean/Mathlib foundations:

- `propext`
- `Classical.choice`
- `Quot.sound`

No `sorryAx` or custom axiom is present.
