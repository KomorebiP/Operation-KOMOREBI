import Mathlib.RingTheory.Valuation.RamificationGroup
import Mathlib.Tactic

/-!+# Valuation inertia fixes a square root of minus one away from two

The inertia group here is Mathlib's actual kernel of the residue-field action
of a valuation's decomposition subgroup. No identification of that subgroup
with an entire absolute Galois group is asserted.
-/

noncomputable section

namespace PaperX.QuadraticValuationInertia

variable {L : Type*} [Field L]

theorem inverse_of_square_neg_one {y : L} (hy : y ^ 2 = -1) : y⁻¹ = -y := by
  have hy0 : y ≠ 0 := by
    intro h
    simp [h] at hy
  have hi : y * (-y) = 1 := by linear_combination -hy
  calc
    y⁻¹ = y⁻¹ * (y * (-y)) := by rw [hi, mul_one]
    _ = -y := by rw [← mul_assoc, inv_mul_cancel₀ hy0, one_mul]

theorem mem_of_square_neg_one (A : ValuationSubring L) {y : L}
    (hy : y ^ 2 = -1) : y ∈ A := by
  rcases A.mem_or_inv_mem y with h | h
  · exact h
  · simpa [inverse_of_square_neg_one hy] using A.neg_mem _ h

def integralRoot (A : ValuationSubring L) (y : L) (hy : y ^ 2 = -1) : A :=
  ⟨y, mem_of_square_neg_one A hy⟩

@[simp] theorem integralRoot_val (A : ValuationSubring L) (y : L)
    (hy : y ^ 2 = -1) : (integralRoot A y hy : L) = y := rfl

theorem integralRoot_sq (A : ValuationSubring L) (y : L)
    (hy : y ^ 2 = -1) : integralRoot A y hy ^ 2 = -1 := by
  apply Subtype.ext
  exact hy

theorem integralRoot_isUnit (A : ValuationSubring L) (y : L)
    (hy : y ^ 2 = -1) : IsUnit (integralRoot A y hy) := by
  apply isUnit_iff_exists_inv.mpr
  refine ⟨-integralRoot A y hy, ?_⟩
  linear_combination -(integralRoot_sq A y hy)

variable (K : Type*) [Field K] [Algebra K L]

theorem inertia_fixes_square_neg_one (A : ValuationSubring L)
    (h2 : IsUnit (2 : A)) (y : L) (hy : y ^ 2 = -1)
    (σ : A.decompositionSubgroup K) (hσ : σ ∈ A.inertiaSubgroup K) :
    (σ.val : L ≃ₐ[K] L) y = y := by
  let z : A := integralRoot A y hy
  have hz : z ^ 2 = -1 := integralRoot_sq A y hy
  have hzu : IsUnit z := integralRoot_isUnit A y hy
  have hres : IsLocalRing.residue A (σ • z) = IsLocalRing.residue A z := by
    change MulSemiringAction.toRingAut (A.decompositionSubgroup K)
      (IsLocalRing.ResidueField A) σ = 1 at hσ
    exact congrArg (fun f : RingAut (IsLocalRing.ResidueField A) =>
      f (IsLocalRing.residue A z)) hσ
  have hs : (σ • z) ^ 2 = z ^ 2 := by
    change (MulSemiringAction.toRingAut (A.decompositionSubgroup K) A σ z) ^ 2 = z ^ 2
    rw [← map_pow, hz, map_neg, map_one]
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp hs with heq | hneg
  · exact congrArg (fun t : A => (t : L)) heq
  · have hr : IsLocalRing.residue A (-z) = IsLocalRing.residue A z := by
      rwa [hneg] at hres
    have hz0 : IsLocalRing.residue A z ≠ 0 :=
      (IsLocalRing.residue_ne_zero_iff_isUnit z).mpr hzu
    have h20 : (2 : IsLocalRing.ResidueField A) ≠ 0 := by
      have := (IsLocalRing.residue_ne_zero_iff_isUnit (2 : A)).mpr h2
      simpa only [map_ofNat] using this
    have hm : (2 : IsLocalRing.ResidueField A) * IsLocalRing.residue A z = 0 := by
      simp only [map_neg] at hr
      linear_combination -hr
    exact False.elim ((mul_ne_zero h20 hz0) hm)

end PaperX.QuadraticValuationInertia
