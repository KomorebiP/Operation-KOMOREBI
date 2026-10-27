# Proof ledger — Strong Artin Lean v0.16

## Evidence label

Every item below is **Lean-checked as written** under the pinned Lean/mathlib environment. They are algebraic, finite-group, and linearized local statements. Their number-field, local-Tate, automorphic-occurrence, and patching instantiations remain open.

## `AuxiliaryColumnCompletion.lean`

Definitions:

- `auxiliaryMap`
- `augmentedMap`
- `obstructionDual`
- `columnFunctional`

Checked capstone:

- `augmentedMap_surjective_of_obstruction_detection`

If selected auxiliary columns jointly separate `ker J.dualMap`, adjoining those columns makes `J` surjective.

## `RelativeTaylorWilesJacobianCapstone.lean`

Definition:

- `columnSelectionInterface`

Checked capstone:

- `exists_exact_admissible_columns_making_augmentedMap_surjective`

The exact `finrank`-sized admissible set supplied by v0.15 makes the augmented Jacobian surjective.

## `CoprimeKernelSurjectivity.lean`

Checked theorems:

- `map_ker_eq_top_of_coprime_card`
- `exists_lift_in_ker_of_coprime_card`
- `map_ker_eq_top_of_pGroup_label`
- `exists_lift_in_pGroup_kernel`

Prime-power splitting constraints preserve every residual class when the residual finite quotient has order prime to `p`.

## `AffineCocyclePackaging.lean`

Structures:

- `AffineExtension`
- `CocycleData`

Definitions include:

- `CocycleData.affineLift`
- `CocycleData.combinedFiniteLabel`
- `CocycleData.combinedRange`
- `CocycleData.combinedQuotient`

Checked conclusions include:

- the semidirect-product group laws;
- a normalized cocycle is a homomorphism into the affine extension;
- residual, translation, and cyclotomic coordinates are recovered exactly;
- the actual combined range is finite;
- the range-restricted quotient map is surjective.

## `SpectralTraceConjugacy.lean`

Definition:

- `traceProbe`

Checked theorems:

- `traceProbe_conj`
- `traceProbe_coboundary_eq_zero`
- `commute_conj`
- `traceProbe_affine_conjugacy`

The projector trace is invariant under simultaneous conjugation and kills local Frobenius coboundaries when the projector commutes with Frobenius.

## `SpectralDeterminantDifferential.lean`

Checked theorems:

- `derivative_spectralDet_eq_traceProbe`
- `coeff_one_spectralDet_eq_traceProbe`

The projector trace is exactly the derivative/linear coefficient of the selected determinant coordinate.

## `FrobeniusCocycleQuotient.lean`

Definitions:

- `conjugationLinear`
- `frobeniusCoboundaryMap`
- `frobeniusCoboundaries`
- `leftMulLinear`
- `traceProbeLinear`
- `frobeniusQuotientProbe`

Checked capstones:

- `frobeniusCoboundaries_le_ker_traceProbe`
- `frobeniusQuotientProbe_ne_zero_on_mkQ`

A commuting spectral projector defines a well-defined detector on the quotient by `range (1 - Ad A)`.

## `MatrixCocycleConjugacy.lean`

Structure:

- `MatrixCocycleData`

Checked theorems:

- `value_inv`
- `value_conj`
- `traceProbe_value_conj`
- `traceProbe_value_conj_ne_zero`

The matrix cocycle has the exact affine conjugation formula, and the transported spectral detector is constant on the conjugacy class.

## `ChebotarevReadySpectralClass.lean`

Checked capstones:

- `exists_splitting_kernel_spectral_detector`
- `exists_chebotarev_ready_conjugacy_class`
- `exists_indexed_chebotarev_ready_conjugacy_class`

These combine prime-power kernel lifting, the two-candidate cocycle selector, the projector/residual-fibre linkage, and conjugacy stability. They produce the complete finite-group datum to which an external Chebotarev theorem can be applied.

## `LocalTaylorWilesLinearInterface.lean`

Structure:

- `LocalSpectralLinearDatum`

Definition:

- `LocalSpectralLinearDatum.localFunctional`

Checked capstones:

- `localFunctional_eq_spectralDet_derivative`
- `localFunctional_ne_zero_of_spectralDerivative`

The local quotient detector is an actual spectral determinant differential. The arithmetic local Tate-duality normalization is not claimed.

## Axiom audit

The displayed capstones use only ordinary Lean/Mathlib foundations, among:

- `propext`
- `Classical.choice`
- `Quot.sound`

No `sorryAx` or custom axiom is present.
