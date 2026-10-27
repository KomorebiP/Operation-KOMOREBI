# Proof ledger — Strong Artin Lean v0.14.0

## Evidence policy

A statement is marked **checked** only if its source compiled under the pinned Lean/mathlib environment with warnings as errors and no prohibited proof escape. No theorem below is promoted to a global number-theoretic assertion beyond its literal formal hypotheses.

## A. Two-point element selection

### `PreChebotarevSelector.lean`

**Checked:**

- `cocycle_mul_of_action_eq_one`
- `probe_detects_base_or_adjusted`
- `exists_label_preserving_detected_element`

**Content.** If `sigma` acts trivially on the coefficient representation and a probe detects `f sigma`, then the probe detects either `f g` or `f (sigma * g)`. If `sigma` is also invisible to residual and cyclotomic labels, the chosen candidate preserves both labels.

## B. Actual projector specialization

### `ProjectorPreChebotarevSelector.lean`

**Checked:**

- `conjugation_action_eq_one_of_residual_eq_one`
- `exists_same_residual_cyclotomic_trivial_projector_detected`
- `exists_centered_projector_detecting_nonscalar_value`
- `exists_centered_projector_and_label_preserving_detected_element`

**Content.** The abstract probe is realized by the trace pairing with an actual centered projector. This module contains the ambient-adjoint formulation and records the exact nonscalar-value interface.

### `RelativePreChebotarevSelector.lean`

**Checked:**

- `exists_preChebotarev_element_of_relative_detection`

**Content.** The v0.13 relative/off-scalar spectral-detection hypothesis automatically supplies the raw separation used by the actual-projector selector.

## C. Degree-one cohomology

### `FiniteGroupH1Averaging.lean`

**Checked:**

- `cocycle_mem_coboundaries_of_card_ne_zero`
- `H1_subsingleton_of_card_ne_zero`

**Content.** For a finite group whose order is nonzero in the coefficient field, every `1`-cocycle is explicitly a coboundary. The averaging primitive is `-|G|⁻¹ * sum_g f(g)`.

### `H1RestrictionInjective.lean`

**Checked:**

- `H1_restriction_map_injective_of_quotient_card_ne_zero`
- `H1_restriction_injective_of_quotient_card_ne_zero`
- `H1_restriction_map_ne_zero_of_ne_zero`
- `exists_subgroup_element_with_nonzero_cocycle_value`

**Content.** Inflation–restriction plus the averaging theorem makes restriction on `H¹` injective across a finite quotient of order nonzero in the field. A nonzero class consequently has a nonzero cocycle value on the subgroup.

### `CohomologicalRelativePreChebotarev.lean`

**Checked:**

- `exists_preChebotarev_element_from_nonzero_H1_class`

**Content.** Ambient-adjoint cohomological capstone. It keeps an explicit hypothesis ensuring nonzero subgroup values are transverse to the scalar line. This theorem is retained as an interface theorem, but the quotient formulation below is stronger for the intended application.

## D. Quotient adjoint representation

### `TransverseAdjointRepresentation.lean`

**Checked definitions:**

- `scalarLine`
- `transverseAdjointRep`

**Checked theorems:**

- `scalarLine_invariant`
- `transverseAdjoint_action_eq_one_of_residual_eq_one`

**Content.** The scalar/cyclic line is stable under conjugation, hence `End(W)/k·1` is a genuine quotient representation. A residual-kernel element acts trivially on it.

### `TransverseQuotientProjectorProbes.lean`

**Checked definition:**

- `transverseProjectorProbe`

**Checked theorems:**

- `transverseProjectorProbe_mk`
- `transverseProjectorProbes_separate`
- `exists_transverseProjectorProbe_ne_zero`

**Content.** Actual centered projector traces descend to the quotient and separate every nonzero transverse class under the v0.13 relative spectral hypothesis.

### `TransverseCohomologicalPreChebotarev.lean`

**Checked:**

- `exists_detected_label_preserving_element_from_transverse_H1`

**Content.** A nonzero class in `H¹(G, End(W)/k·1)` yields a residual/cyclotomic-label-preserving element detected by an actual centered projector. No separate nonscalar-value hypothesis remains.

## E. Cyclotomic-depth survival

### `CyclotomicDepthSurvival.lean`

**Checked:**

- `cocycle_conjugate_of_action_eq_one`
- `exists_deeper_nonzero_value_of_central_quotient`
- `exists_deeper_nonzero_value_from_nonzero_H1`

**Content.** If `T ≤ S`, `S` acts trivially, conjugation is trivial on `S/T`, and the coefficient representation has no fixed vectors, a cocycle nonzero on `S` remains nonzero on `T`. The `H¹` version obtains nonvanishing on `S` by restriction injectivity.

## F. No fixed vectors in the transverse quotient

### `QuotientFixedVectorAveraging.lean`

**Checked:**

- `quotient_fixed_eq_zero_of_card_ne_zero`

**Content.** Finite-group averaging lifts a fixed quotient class to a fixed ambient vector. If all fixed ambient vectors lie in the quotient subspace, the quotient class is zero.

### `TransverseAdjointNoFixed.lean`

**Checked:**

- `conjugation_fixed_mem_scalarLine_of_irreducible`
- `transverseAdjoint_fixed_eq_zero_of_irreducible`

**Content.** Schur’s lemma identifies fixed ambient endomorphisms with scalar endomorphisms. Averaging then proves the transverse quotient has no fixed vectors when the residual finite-image order is nonzero in the coefficient field.

### `TransverseAdjointPullbackNoFixed.lean`

**Checked:**

- `pullback_transverseAdjoint_fixed_eq_zero`

**Content.** Pullback along a surjective global-to-residual homomorphism introduces no new fixed vectors.

### `RelativeCyclotomicDepthSurvival.lean`

**Checked:**

- `exists_deep_transverse_cocycle_value`

**Content.** Combines irreducibility, prime-to-characteristic finite residual image, surjective pullback, prime-to-characteristic restriction injectivity, and centrality of `S/T` to obtain a nonzero transverse cocycle value on the deeper subgroup.

## G. Final v0.14 capstone

### `RelativeTaylorWilesPreChebotarev.lean`

**Checked:**

- `exists_deep_label_preserving_projector_detected_element`

**Formal conclusion.** For a nonzero transverse `H¹` class and the literal hypotheses in the theorem, there exist an actual centered projector index `i` and a group element `gamma` such that:

```text
res gamma = res g
cyc gamma = 1
transverseProjectorProbe i (f gamma) != 0.
```

**Not included in the conclusion:** Frobenius realization, unramifiedness, local Tate-duality interpretation, auxiliary-prime cardinality, patching, or automorphy.

## Inventory

- additive source modules: **15**
- theorem/lemma declarations: **29**
- definitions/abbreviations: **3**
- prohibited proof escapes: **0**
