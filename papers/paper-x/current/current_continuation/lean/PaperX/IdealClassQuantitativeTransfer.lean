import PaperX.IdealClassQuantitativeConstant

/-!
# Transfer of a quantitative bound on the actual cone to actual ideal classes

The geometric hypothesis is deliberately stated on the actual ideal lattice and
ordinary fundamental cone. The resulting ideal-class count is not an abstract
label or a supplied arithmetic counting function.
-/

set_option autoImplicit false
noncomputable section

open Ideal MeasureTheory Filter Asymptotics
open scoped nonZeroDivisors Real Classical Pointwise
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.euclidean NumberField.mixedEmbedding.fundamentalCone
open NumberField.Units

namespace PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- The codimension-one boundary exponent in the ideal norm variable. -/
def countExponent : ℝ := 1 - (Module.finrank ℚ K : ℝ)⁻¹

theorem countExponent_nonneg : 0 ≤ countExponent K := by
  have hdeg : (1 : ℝ) ≤ Module.finrank ℚ K := by
    exact_mod_cast (Module.finrank_pos (R := ℚ) (M := K))
  exact sub_nonneg.mpr (inv_le_one_of_one_le₀ hdeg)

/-- Reparametrization changes boundary degree `d-1` into norm exponent `1-1/d`. -/
theorem root_boundary_power (y : ℝ) (hy : 0 ≤ y) :
    (y ^ (Module.finrank ℚ K : ℝ)⁻¹) ^ (Module.finrank ℚ K - 1) =
      y ^ countExponent K := by
  have hd : 1 ≤ Module.finrank ℚ K := Module.finrank_pos (R := ℚ) (M := K)
  have hd0 : (Module.finrank ℚ K : ℝ) ≠ 0 := by exact_mod_cast (Nat.ne_zero_of_lt hd)
  rw [← Real.rpow_natCast, ← Real.rpow_mul hy]
  congr 1
  rw [Nat.cast_sub hd, Nat.cast_one, countExponent]
  field_simp

/-- A boundary bound in radial scale yields the corresponding norm-scale bound. -/
theorem norm_bound_of_dilation_bound (J : (Ideal (𝓞 K))⁰) (B : ℝ)
    (hB : ∀ t : ℝ, 1 ≤ t →
      |(Nat.card (t • coneRegion K 1 ∩ idealEuclideanLattice K J :
        Set (euclidean.mixedSpace K)) : ℝ) -
        latticeDensity K J * t ^ Module.finrank ℚ K| ≤
          B * (t ^ (Module.finrank ℚ K - 1) + 1)) :
    ∀ y : ℝ, 1 ≤ y →
      |(latticeCount K J y : ℝ) - latticeDensity K J * y| ≤
        B * (y ^ countExponent K + 1) := by
  intro y hy
  have hy0 : 0 < y := lt_of_lt_of_le zero_lt_one hy
  have hd : Module.finrank ℚ K ≠ 0 := (Module.finrank_pos (R := ℚ) (M := K)).ne'
  have ht : 1 ≤ y ^ (Module.finrank ℚ K : ℝ)⁻¹ :=
    Real.one_le_rpow hy (by positivity)
  have h := hB (y ^ (Module.finrank ℚ K : ℝ)⁻¹) ht
  rw [smul_coneRegion_one K (Real.rpow_pos_of_pos hy0 _),
    Real.rpow_inv_natCast_pow hy0.le hd, root_boundary_power K y hy0.le] at h
  exact h

/-- A bound for the actual ideal lattice yields a uniform-in-threshold ideal-class bound. -/
theorem class_bound_of_norm_bound {C : ClassGroup (𝓞 K)} {J : (Ideal (𝓞 K))⁰}
    (hJ : ClassGroup.mk0 J = C⁻¹) {B : ℝ} (hB0 : 0 ≤ B)
    (hB : ∀ y : ℝ, 1 ≤ y →
      |(latticeCount K J y : ℝ) - latticeDensity K J * y| ≤
        B * (y ^ countExponent K + 1)) :
    ∀ s : ℝ, 1 ≤ s →
      |(classCount K C s : ℝ) - classResidue K * s| ≤
        (B / torsionOrder K * ((absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1)) *
          s ^ countExponent K := by
  intro s hs
  have hN : (1 : ℝ) ≤ absNorm (J : Ideal (𝓞 K)) := by
    exact_mod_cast absNorm_pos_of_nonZeroDivisors J
  have hs0 : 0 ≤ s := le_trans zero_le_one hs
  have hN0 : (0 : ℝ) ≤ absNorm (J : Ideal (𝓞 K)) := le_trans zero_le_one hN
  have hy : 1 ≤ s * absNorm (J : Ideal (𝓞 K)) := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hs) (sub_nonneg.mpr hN)]
  have hp : 1 ≤ s ^ countExponent K := Real.one_le_rpow hs (countExponent_nonneg K)
  rw [class_error_eq_lattice_error K hJ, abs_div, abs_of_pos (torsionOrder_cast_pos K)]
  calc
    _ ≤ B * ((s * (absNorm (J : Ideal (𝓞 K)) : ℝ)) ^ countExponent K + 1) /
          torsionOrder K :=
      div_le_div_of_nonneg_right (hB _ hy) (torsionOrder_cast_pos K).le
    _ ≤ (B / torsionOrder K * ((absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1)) *
          s ^ countExponent K := by
      rw [Real.mul_rpow hs0 hN0]
      have hpos : 0 ≤ B / (torsionOrder K : ℝ) := div_nonneg hB0 (torsionOrder_cast_pos K).le
      calc
        _ = (B / torsionOrder K) * (s ^ countExponent K *
            (absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1) := by ring
        _ ≤ (B / torsionOrder K) * (s ^ countExponent K *
            (absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K +
            s ^ countExponent K) := mul_le_mul_of_nonneg_left (by linarith) hpos
        _ = _ := by ring

/-- The concrete error is big-O once the concrete lattice discrepancy is bounded. -/
theorem class_isBigO_of_dilation_bound {C : ClassGroup (𝓞 K)} {J : (Ideal (𝓞 K))⁰}
    (hJ : ClassGroup.mk0 J = C⁻¹) {B : ℝ} (hB0 : 0 ≤ B)
    (hB : ∀ t : ℝ, 1 ≤ t →
      |(Nat.card (t • coneRegion K 1 ∩ idealEuclideanLattice K J :
        Set (euclidean.mixedSpace K)) : ℝ) -
        latticeDensity K J * t ^ Module.finrank ℚ K| ≤
          B * (t ^ (Module.finrank ℚ K - 1) + 1)) :
    (fun s : ℝ => (classCount K C s : ℝ) - classResidue K * s) =O[atTop]
      (fun s : ℝ => s ^ countExponent K) := by
  apply IsBigO.of_bound
    (B / torsionOrder K * ((absNorm (J : Ideal (𝓞 K)) : ℝ) ^ countExponent K + 1))
  filter_upwards [eventually_ge_atTop (1 : ℝ)] with s hs
  rw [Real.norm_eq_abs, Real.norm_eq_abs,
    abs_of_nonneg (Real.rpow_nonneg (le_trans zero_le_one hs) _)]
  exact class_bound_of_norm_bound K hJ hB0 (norm_bound_of_dilation_bound K J B hB) s hs

end PaperX.IdealClassQuantitative
