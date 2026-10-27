import PaperX.NormResidueGeneratorAttachment
import PaperX.NormResidueGeneratorSum
import PaperX.NormResidueUnitCounting
import PaperX.IdealNormCharacterBound

/-! Arithmetic norm-character cancellation from a residue-unit witness.
The cone estimate, both sign means, and the exact generator/ideal comparison
are proved dependencies; the displayed arithmetic hypotheses remain supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NormResidueLattice
open Ideal NumberField
open PaperX.IdealClassQuantitative PaperX.ResidueLattice PaperX.NormResidue
open PaperX.IdealNormWeighted PaperX.IdealResidueUnitAction
open scoped nonZeroDivisors Classical Pointwise Real

variable (K : Type*) [Field K] [NumberField K]

/-- The finite residue computation equals the actual bounded generator sum. -/
theorem normWeightedCount_eq_boundedGeneratorSum (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m → ℂ) {t : ℝ} (ht : 0 < t) :
    normWeightedCount K M J m hM χ t =
      boundedGeneratorSum K J (fun n => χ (n : ZMod m)) (t ^ Module.finrank ℚ K) := by
  rw [normWeightedCount_eq_generatorPointSum K M J m hM χ ht]
  exact latticeGeneratorSum_eq_boundedGeneratorSum K J (fun n => χ (n : ZMod m)) ht

/-- The canonical modulus count is independent of its chosen finite enumeration. -/
theorem modulusNormWeightedCount_eq_boundedGeneratorSum (J : (Ideal (𝓞 K))⁰)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m → ℂ) {t : ℝ} (ht : 0 < t) :
    modulusNormWeightedCount K J m hm χ t =
      boundedGeneratorSum K J (fun n => χ (n : ZMod m)) (t ^ Module.finrank ℚ K) := by
  let := Fintype.ofFinite (IdealResidues K (modulusTimesIdeal K J m hm) J)
  unfold modulusNormWeightedCount
  exact normWeightedCount_eq_boundedGeneratorSum K _ J m _ χ ht

/-- The unit witness gives a power-saving estimate on actual algebraic generators,
with all finite-mean and geometric estimates discharged. -/
theorem exists_boundedGeneratorSum_bound_of_unit (J : (Ideal (𝓞 K))⁰)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →* ℂ)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ Y : ℝ, 1 ≤ Y →
      ‖boundedGeneratorSum K J (fun n => χ (n : ZMod m)) Y‖ ≤
        B * (Y ^ countExponent K + 1) := by
  obtain ⟨B, hB0, hB⟩ := exists_modulusNormWeightedCount_bound K J m hm χ u hu
  refine ⟨B, hB0, fun Y hY => ?_⟩
  have hY0 : 0 < Y := lt_of_lt_of_le zero_lt_one hY
  have hd : Module.finrank ℚ K ≠ 0 := (Module.finrank_pos (R := ℚ) (M := K)).ne'
  have ht : 1 ≤ Y ^ (Module.finrank ℚ K : ℝ)⁻¹ :=
    Real.one_le_rpow hY (by positivity)
  have H := hB (Y ^ (Module.finrank ℚ K : ℝ)⁻¹) ht
  rw [modulusNormWeightedCount_eq_boundedGeneratorSum K J m hm χ
      (Real.rpow_pos_of_pos hY0 _),
    Real.rpow_inv_natCast_pow hY0.le hd, root_boundary_power K Y hY0.le] at H
  exact H

/-- Actual ideal norm-character sums in a class have power-saving cancellation
under a residue-unit witness and nonvanishing on the inverse-class representative. -/
theorem exists_classNormSum_bound_of_unit {C : ClassGroup (𝓞 K)}
    {J : (Ideal (𝓞 K))⁰} (hJ : ClassGroup.mk0 J = C⁻¹)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1)
    (hχJ : χ (absNorm (J : Ideal (𝓞 K)) : ZMod m) ≠ 0) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ X : ℝ, 1 ≤ X →
      ‖classNormSum K C (fun n => χ (n : ZMod m)) X‖ ≤
        B * X ^ countExponent K :=
  exists_classNormSum_bound_of_generator_bound K hJ m χ hχJ
    (exists_boundedGeneratorSum_bound_of_unit K J m hm χ.toMonoidHom u hu)

end PaperX.NormResidueLattice
