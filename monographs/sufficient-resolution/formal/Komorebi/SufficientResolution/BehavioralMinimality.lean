import Komorebi.SufficientResolution.Behavioral
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-!
# Universal comparison and minimal finite dimension

The comparison is from the image of an arbitrary exact model.  Surjectivity
of that model is not silently assumed.  Ambient dimension is compared only
when that competing ambient state space is finite dimensional.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.BehavioralMinimality

open Behavioral Module

universe uK uX uY uZ uI
variable {K : Type uK} [Field K]
variable {X : Type uX} [AddCommGroup X] [Module K X]
variable {Y : Type uY} [AddCommGroup Y] [Module K Y]
variable {Z : Type uZ} [AddCommGroup Z] [Module K Z]
variable {I : Type uI}
variable (T : I → X →ₗ[K] X) (O : X →ₗ[K] Y)

 theorem quotientMap_surjective : Function.Surjective (quotientMap T O) :=
  (invisible T O).mkQ_surjective

/-- The constructed quotient has no remaining permanently invisible direction. -/
 theorem quotient_is_observable :
    invisible (induced T O) (observation T O) = ⊥ := by
  apply le_antisymm
  · intro s hs
    obtain ⟨x, rfl⟩ := quotientMap_surjective T O s
    have hx : x ∈ invisible T O := by
      intro w
      have h := hs w
      simpa only [all_future_observations_preserved] using h
    change quotientMap T O x = 0
    exact (Submodule.Quotient.mk_eq_zero (invisible T O)).mpr hx
  · exact bot_le

variable (q : X →ₗ[K] Z) (U : I → Z →ₗ[K] Z) (V : Z →ₗ[K] Y)
variable (hT : ∀ i : I, q.comp (T i) = (U i).comp q) (hO : V.comp q = O)

 theorem modelQuotientComparison_surjective :
    Function.Surjective (modelQuotientComparison T O q U V hT hO) := by
  intro s
  obtain ⟨x, rfl⟩ := quotientMap_surjective T O s
  exact ⟨Submodule.Quotient.mk x, rfl⟩

/-- Comparison from the actual image of a possibly non-surjective exact model. -/
def imageComparison : LinearMap.range q →ₗ[K] State T O :=
  (modelQuotientComparison T O q U V hT hO).comp
    q.quotKerEquivRange.symm.toLinearMap

 theorem imageComparison_surjective :
    Function.Surjective (imageComparison T O q U V hT hO) := by
  exact (modelQuotientComparison_surjective T O q U V hT hO).comp
    q.quotKerEquivRange.symm.surjective

 theorem imageComparison_on_state (x : X) :
    imageComparison T O q U V hT hO (q.rangeRestrict x) = quotientMap T O x := by
  change modelQuotientComparison T O q U V hT hO
    (q.quotKerEquivRange.symm (q.rangeRestrict x)) = quotientMap T O x
  have he : q.quotKerEquivRange.symm (q.rangeRestrict x) =
      (Submodule.Quotient.mk x : X ⧸ LinearMap.ker q) := by
    apply q.quotKerEquivRange.injective
    rw [LinearEquiv.apply_symm_apply]
    rfl
  rw [he]
  rfl

/-- Any two image comparisons agreeing on the original states agree everywhere. -/
 theorem imageComparison_unique (f : LinearMap.range q →ₗ[K] State T O)
    (hf : ∀ x : X, f (q.rangeRestrict x) = quotientMap T O x) :
    f = imageComparison T O q U V hT hO := by
  ext z
  obtain ⟨x, hx⟩ := z.property
  have hz : q.rangeRestrict x = z := Subtype.ext hx
  rw [← hz, hf, imageComparison_on_state]

/-- A kernel-exact realization is explicitly equivalent to the canonical minimal state. -/
def minimalImageEquiv (hk : LinearMap.ker q = invisible T O) :
    LinearMap.range q ≃ₗ[K] State T O :=
  q.quotKerEquivRange.symm.trans
    (Submodule.quotEquivOfEq (LinearMap.ker q) (invisible T O) hk)

 theorem minimalImageEquiv_on_state (hk : LinearMap.ker q = invisible T O) (x : X) :
    minimalImageEquiv T O q hk (q.rangeRestrict x) = quotientMap T O x := by
  change Submodule.quotEquivOfEq (LinearMap.ker q) (invisible T O) hk
    (q.quotKerEquivRange.symm (q.rangeRestrict x)) = quotientMap T O x
  have he : q.quotKerEquivRange.symm (q.rangeRestrict x) =
      (Submodule.Quotient.mk x : X ⧸ LinearMap.ker q) := by
    apply q.quotKerEquivRange.injective
    rw [LinearEquiv.apply_symm_apply]
    rfl
  rw [he, Submodule.quotEquivOfEq_mk]
  rfl


variable [FiniteDimensional K X]

 theorem finrank_state_add_invisible :
    finrank K (State T O) + finrank K (invisible T O) = finrank K X :=
  (invisible T O).finrank_quotient_add_finrank

 theorem finrank_state :
    finrank K (State T O) = finrank K X - finrank K (invisible T O) := by
  have h := finrank_state_add_invisible T O
  omega

include hT hO in
 theorem finrank_state_le_image :
    finrank K (State T O) ≤ finrank K (LinearMap.range q) := by
  calc
    finrank K (State T O) ≤ finrank K (X ⧸ LinearMap.ker q) :=
      LinearMap.finrank_le_finrank_of_surjective
        (modelQuotientComparison_surjective T O q U V hT hO)
    _ = finrank K (LinearMap.range q) := q.quotKerEquivRange.finrank_eq

include hT hO in
 theorem finrank_state_le_model [FiniteDimensional K Z] :
    finrank K (State T O) ≤ finrank K Z :=
  (finrank_state_le_image T O q U V hT hO).trans (LinearMap.range q).finrank_le

/-- Dimension excess is exactly the number of unnecessarily retained distinctions. -/
 theorem dimension_excess_identity :
    finrank K (LinearMap.range q) + finrank K (LinearMap.ker q) =
      finrank K (State T O) + finrank K (invisible T O) := by
  rw [finrank_state_add_invisible T O]
  exact q.finrank_range_add_finrank_ker

include hT hO in
/-- An exact model image is minimal precisely when its kernel is the full invisible space. -/
 theorem image_dimension_minimal_iff :
    finrank K (LinearMap.range q) = finrank K (State T O) ↔
      LinearMap.ker q = invisible T O := by
  constructor
  · intro hdim
    have hsum := dimension_excess_identity T O q
    have hk : finrank K (LinearMap.ker q) = finrank K (invisible T O) := by omega
    exact Submodule.eq_of_le_of_finrank_eq (exact_model_kernel_le T O q U V hT hO) hk
  · intro hk
    have hsum := dimension_excess_identity T O q
    rw [hk] at hsum
    omega


end Komorebi.SufficientResolution.BehavioralMinimality
