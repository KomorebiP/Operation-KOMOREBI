# Proof ledger — Strong Artin Lean v0.18

## Evidence label

Every statement below is **Lean-checked as written** under the pinned environment. The results concern finite cyclic group cohomology, the checked matrix Frobenius quotient, the linearized tame relation, and one-dimensional normalization. Continuous local Galois cohomology and arithmetic local Tate duality remain external comparison inputs.

## `FiniteCyclicH1Model.lean`

Definitions:

- `toNormKernel`
- `h1ClassOfValue`
- `h1EquivValueQuotient`

Checked theorems:

1. `toNormKernel_coe`
2. `h1ClassOfValue_apply`
3. `h1ClassOfValue_eq_iff`
4. `groupCohomologyπOdd_surjective`
5. `h1ClassOfValue_surjective`
6. `ker_h1ClassOfValue`
7. `h1EquivValueQuotient_mkQ`

Main conclusion:

```text
A.norm = 0
  -> (A / range(A(g)-1)) ≃ₗ[k] groupCohomology.H1 A.
```

## `FiniteCyclicFrobeniusH1.lean`

Definition:

- `h1EquivFrobeniusQuotient`

Checked theorems:

8. `range_generator_sub_one_eq_frobeniusCoboundaries`
9. `h1EquivFrobeniusQuotient_mkQ`

Main conclusion:

```text
ρ(g) = conjugationLinear F
  -> range(ρ(g)-1) = frobeniusCoboundaries F
  -> Matrix / frobeniusCoboundaries F ≃ₗ[k] H¹(G, Rep.of ρ).
```

## `FiniteCyclicTamePairing.lean`

Definition:

- `centralizerEquivCyclicH1Dual`

Checked theorems:

10. `centralizerEquivCyclicH1Dual_apply_class`
11. `centralizerEquivCyclicH1Dual_ne_zero_iff`
12. `exists_unique_cyclic_h1_representative`

Main conclusion:

```text
frobeniusCentralizer F ≃ₗ[k] Dual k H¹(G, Rep.of ρ),
```

with representative formula `trace(P * X)`.

## `FiniteCyclicTaylorWilesPairingCapstone.lean`

Definition:

- `tameRelationEquivCyclicH1Dual`

Checked theorems:

13. `tameRelationEquivCyclicH1Dual_apply_class`
14. `exists_unique_tame_cyclic_h1_representative`

Main conclusion:

```text
tameInertiaRelationSpace F 1 ≃ₗ[k] Dual k H¹(G, Rep.of ρ).
```

Every cyclic `H¹` functional has one unique representative satisfying the `q=1` linearized tame relation.

## `OneDimensionalPairingNormalization.lean`

Checked theorems:

15. `exists_smul_eq_of_finrank_eq_one`
16. `exists_unique_unit_smul_eq`
17. `unit_smul_apply_ne_zero_iff`
18. `nonzero_functionals_detect_same_vectors`

Main conclusion:

```text
finrank k L = 1, f ≠ 0, g ≠ 0
  -> exists unique u : kˣ, u • g = f
  -> (f x ≠ 0 ↔ g x ≠ 0).
```

## `LocalTateNormalizationBoundary.lean`

Definitions:

- `transportedCyclicTraceFunctional`
- `centralizerEquivComparedH1Dual`

Checked theorems:

19. `transportedCyclicTraceFunctional_apply`
20. `centralizerEquivComparedH1Dual_apply`
21. `transportedCyclicTraceFunctional_ne_zero_iff`
22. `exists_unique_unit_trace_normalization`
23. `tate_ne_zero_iff_transported_trace_ne_zero`
24. `tate_ne_zero_iff_traceProbe_ne_zero`

Main conclusion:

Once a comparison equivalence

```text
L ≃ₗ[k] H¹(G, Rep.of ρ)
```

is supplied for a one-dimensional arithmetic local quotient `L`, every nonzero arithmetic Tate functional agrees with the checked cyclic trace functional up to one unique unit. If a class maps to the cyclic class represented by `X`, then

```text
Tate(x) ≠ 0 ↔ trace(P * X) ≠ 0.
```

## Axiom audit

The displayed capstones use only:

- `propext`
- `Classical.choice`
- `Quot.sound`

No `sorryAx` or custom axiom occurs.
