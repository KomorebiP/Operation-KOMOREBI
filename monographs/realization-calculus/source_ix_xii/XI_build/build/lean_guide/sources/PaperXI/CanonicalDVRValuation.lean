import PaperXI.LocalFieldResidueExtension
import Mathlib.RingTheory.Valuation.Discrete.IsDiscreteValuationRing

/-!
# The canonical adic valuation of the constructed upper DVR

The fraction field constructed in `LocalFieldResidueExtension` is literally the
fraction field of the constructed DVR.  Consequently Mathlib's maximal-ideal
valuation identifies that DVR with the valuation unit ball.  This file records
that identification and proves the unit/uniformizer normalization required by
the local-field attachment.
-/

set_option autoImplicit false
noncomputable section

namespace PaperXI.CanonicalDVRValuation

open IsLocalRing IsDiscreteValuationRing Valuation ValuativeRel
open scoped WithZero

section Generic

variable (A F : Type*) [CommRing A] [IsDomain A] [IsDiscreteValuationRing A]
  [Field F] [Algebra A F] [IsFractionRing A F]

/-- The maximal-ideal valuation on the fraction field of a DVR. -/
abbrev canonicalValuation : Valuation F ℤᵐ⁰ :=
  (IsDiscreteValuationRing.maximalIdeal A).valuation F

/-- The DVR is canonically isomorphic to the unit ball of its adic valuation. -/
def integerRingEquiv :
    A ≃+* (canonicalValuation A F).valuationSubring :=
  IsDiscreteValuationRing.equivValuationSubring

@[simp]
theorem integerRingEquiv_coe (x : A) :
    (((integerRingEquiv A F x : (canonicalValuation A F).valuationSubring) : F)) =
      algebraMap A F x := by
  rfl

/-- Literal equality of the embedded DVR and the canonical valuation unit ball. -/
theorem integerRing_image :
    Subring.map (algebraMap A F) ⊤ =
      (canonicalValuation A F).valuationSubring.toSubring :=
  IsDiscreteValuationRing.map_algebraMap_eq_valuationSubring

/-- An element of the fraction field is integral exactly when it is represented
by an element of the DVR. -/
theorem integer_iff_exists_lift (x : F) :
    canonicalValuation A F x ≤ 1 ↔
      ∃ a : A, algebraMap A F a = x := by
  constructor
  · exact fun hx => IsDiscreteValuationRing.exists_lift_of_le_one hx
  · rintro ⟨a, rfl⟩
    exact (IsDiscreteValuationRing.maximalIdeal A).valuation_le_one (K := F) a

/-- Every DVR unit has canonical valuation one. -/
theorem unit_value (u : A) (hu : IsUnit u) :
    canonicalValuation A F (algebraMap A F u) = 1 := by
  exact Valuation.Integers.one_of_isUnit' hu
    (fun x => (IsDiscreteValuationRing.maximalIdeal A).valuation_le_one (K := F) x)

/-- Membership in the DVR maximal ideal is detected by strict valuation. -/
theorem maximalIdeal_iff_value_lt_one (x : A) :
    canonicalValuation A F (algebraMap A F x) < 1 ↔
      x ∈ IsLocalRing.maximalIdeal A := by
  exact (IsDiscreteValuationRing.maximalIdeal A).valuation_lt_one_iff_mem (K := F) x

/-- A chosen generator of the DVR maximal ideal is a uniformizer for the
canonical fraction-field valuation. -/
theorem uniformizer_isUniformizer (π : A)
    (hπ : Ideal.span {π} = IsLocalRing.maximalIdeal A) :
    (canonicalValuation A F).IsUniformizer (algebraMap A F π) := by
  let e := integerRingEquiv A F
  have hgen : IsLocalRing.maximalIdeal (canonicalValuation A F).valuationSubring =
      Ideal.span {e π} := by
    rw [← IsLocalRing.map_ringEquiv_maximalIdeal e, ← hπ, Ideal.map_span]
    simp
  have h := Valuation.isUniformizer_of_maximalIdeal_eq_span (canonicalValuation A F) hgen
  rw [Valuation.IsUniformizer.iff] at h ⊢
  simpa [e, integerRingEquiv_coe] using h

/-- Exact normalization of a maximal-ideal generator. -/
theorem uniformizer_value (π : A)
    (hπ : Ideal.span {π} = IsLocalRing.maximalIdeal A) :
    canonicalValuation A F (algebraMap A F π) =
      (IsRankOneDiscrete.generator (canonicalValuation A F) : ℤᵐ⁰) :=
  Valuation.IsUniformizer.iff.mp (uniformizer_isUniformizer A F π hπ)

/-- A maximal-ideal generator has value strictly below one. -/
theorem uniformizer_value_lt_one (π : A)
    (hπ : Ideal.span {π} = IsLocalRing.maximalIdeal A) :
    canonicalValuation A F (algebraMap A F π) < 1 :=
  (uniformizer_isUniformizer A F π hπ).val_lt_one

end Generic

section Constructed

open PaperXI.LocalFieldResidueExtension PaperXI.ResidueExtensionRealization

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

abbrev upperRing := LocalFieldResidueExtension.ring K s
abbrev upperField := LocalFieldResidueExtension.field K s
abbrev upperValuation : Valuation (upperField K s) ℤᵐ⁰ :=
  canonicalValuation (upperRing K s) (upperField K s)

/-- The constructed upper DVR is the valuation ring of its canonical adic
valuation on the constructed fraction field. -/
def upperIntegerRingEquiv :
    upperRing K s ≃+* (upperValuation K s).valuationSubring :=
  integerRingEquiv (upperRing K s) (upperField K s)

omit [IsUniformAddGroup K] in
@[simp]
theorem upperIntegerRingEquiv_coe (x : upperRing K s) :
    (((upperIntegerRingEquiv K s x : (upperValuation K s).valuationSubring) :
      upperField K s)) = algebraMap (upperRing K s) (upperField K s) x := by
  rfl

omit [IsUniformAddGroup K] in
/-- Literal ambient-field equality between the embedded constructed DVR and the
canonical valuation unit ball. -/
theorem upper_integerRing_image :
    Subring.map (algebraMap (upperRing K s) (upperField K s)) ⊤ =
      (upperValuation K s).valuationSubring.toSubring :=
  integerRing_image (upperRing K s) (upperField K s)

omit [IsUniformAddGroup K] in
/-- Concrete integrality criterion for the constructed fraction field. -/
theorem upper_integer_iff_exists_lift (x : upperField K s) :
    upperValuation K s x ≤ 1 ↔
      ∃ a : upperRing K s,
        algebraMap (upperRing K s) (upperField K s) a = x :=
  integer_iff_exists_lift (upperRing K s) (upperField K s) x

omit [IsUniformAddGroup K] in
/-- Every unit of the constructed upper DVR has value one. -/
theorem upper_unit_value (u : upperRing K s) (hu : IsUnit u) :
    upperValuation K s
      (algebraMap (upperRing K s) (upperField K s) u) = 1 :=
  unit_value (upperRing K s) (upperField K s) u hu

omit [IsUniformAddGroup K] in
/-- Every unit of the original local-field integer ring retains value one after
mapping through the constructed upper DVR into its fraction field. -/
theorem base_unit_value (u : 𝒪[K]) (hu : IsUnit u) :
    upperValuation K s
      (algebraMap (upperRing K s) (upperField K s)
        (algebraMap 𝒪[K] (upperRing K s) u)) = 1 := by
  apply upper_unit_value K s
  exact hu.map (algebraMap 𝒪[K] (upperRing K s))

omit [IsUniformAddGroup K] in
/-- Any base uniformizer remains a generator of the upper maximal ideal. -/
theorem base_uniformizer_generates_upper (π : 𝒪[K])
    (hπ : Ideal.span {π} = IsLocalRing.maximalIdeal 𝒪[K]) :
    Ideal.span {algebraMap 𝒪[K] (upperRing K s) π} =
      IsLocalRing.maximalIdeal (upperRing K s) := by
  exact PaperXI.UnramifiedPolynomial.uniformizer
    (ResidueExtensionRealization.liftedPolynomial 𝒪[K] s) π hπ

omit [IsUniformAddGroup K] in
/-- A base uniformizer is a uniformizer for the canonical valuation of the
constructed upper fraction field. -/
theorem base_uniformizer_isUniformizer (π : 𝒪[K])
    (hπ : Ideal.span {π} = IsLocalRing.maximalIdeal 𝒪[K]) :
    (upperValuation K s).IsUniformizer
      (algebraMap (upperRing K s) (upperField K s)
        (algebraMap 𝒪[K] (upperRing K s) π)) := by
  exact uniformizer_isUniformizer (upperRing K s) (upperField K s)
    (algebraMap 𝒪[K] (upperRing K s) π)
    (base_uniformizer_generates_upper K s π hπ)

omit [IsUniformAddGroup K] in
/-- Exact canonical value of an inherited base uniformizer. -/
theorem base_uniformizer_value (π : 𝒪[K])
    (hπ : Ideal.span {π} = IsLocalRing.maximalIdeal 𝒪[K]) :
    upperValuation K s
      (algebraMap (upperRing K s) (upperField K s)
        (algebraMap 𝒪[K] (upperRing K s) π)) =
      (IsRankOneDiscrete.generator (upperValuation K s) : ℤᵐ⁰) :=
  Valuation.IsUniformizer.iff.mp (base_uniformizer_isUniformizer K s π hπ)

/-- Choose one base uniformizer from the actual DVR of integers. -/
def chosenBaseUniformizer : 𝒪[K] :=
  Classical.choose (IsDiscreteValuationRing.exists_irreducible 𝒪[K])

omit [IsUniformAddGroup K] in
theorem chosenBaseUniformizer_irreducible :
    Irreducible (chosenBaseUniformizer K) :=
  Classical.choose_spec (IsDiscreteValuationRing.exists_irreducible 𝒪[K])

omit [IsUniformAddGroup K] in
theorem chosenBaseUniformizer_span :
    Ideal.span {chosenBaseUniformizer K} = IsLocalRing.maximalIdeal 𝒪[K] := by
  exact (IsDiscreteValuationRing.irreducible_iff_uniformizer
    (chosenBaseUniformizer K)).mp (chosenBaseUniformizer_irreducible K) |>.symm

omit [IsUniformAddGroup K] in
/-- The chosen base uniformizer gives an actual canonical upper uniformizer. -/
theorem chosenBaseUniformizer_isUpperUniformizer :
    (upperValuation K s).IsUniformizer
      (algebraMap (upperRing K s) (upperField K s)
        (algebraMap 𝒪[K] (upperRing K s) (chosenBaseUniformizer K))) :=
  base_uniformizer_isUniformizer K s (chosenBaseUniformizer K)
    (chosenBaseUniformizer_span K)

omit [IsUniformAddGroup K] in
/-- Exact normalization for the chosen inherited upper uniformizer. -/
theorem chosenBaseUniformizer_value :
    upperValuation K s
      (algebraMap (upperRing K s) (upperField K s)
        (algebraMap 𝒪[K] (upperRing K s) (chosenBaseUniformizer K))) =
      (IsRankOneDiscrete.generator (upperValuation K s) : ℤᵐ⁰) :=
  Valuation.IsUniformizer.iff.mp (chosenBaseUniformizer_isUpperUniformizer K s)

end Constructed

end PaperXI.CanonicalDVRValuation
