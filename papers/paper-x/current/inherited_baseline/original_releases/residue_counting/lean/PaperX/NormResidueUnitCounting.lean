import PaperX.NormResidueWeightedCounting
import PaperX.IdealResidueUnitActionMean

/-! Actual norm-weighted residue counts with finite mean derived from a unit witness.
Both signed averages are proved, rather than included as counting hypotheses. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NormResidueLattice
open Ideal NumberField
open PaperX.ResidueLattice PaperX.NormResidue PaperX.IdealResidueUnitAction
open scoped nonZeroDivisors BigOperators

variable (K : Type*) [Field K] [NumberField K]

/-- The unit permutation proves the zero mean for each of the two actual sign weights. -/
theorem normWeight_sum_eq_zero (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hprod : modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)) ≤ M)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m →* ℂ)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1)
    (positive : Bool) :
    ∑ c : IdealResidues K M J, normWeight K M J m hM χ positive c = 0 := by
  cases positive with
  | false =>
    simpa [normWeight] using
      sum_mul_residueNorm_eq_zero K M J m hprod hM χ u hu (-1)
  | true =>
    simpa [normWeight] using
      sum_mul_residueNorm_eq_zero K M J m hprod hM χ u hu 1

/-- The arithmetic unit witness supplies the cancellation needed by actual signed-region counting. -/
theorem exists_normWeightedCount_bound_of_unit {M J : (Ideal (𝓞 K))⁰}
    (hMJ : (M : Ideal (𝓞 K)) ≤ J) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (hprod : modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)) ≤ M)
    [Fintype (IdealResidues K M J)] (χ : ZMod m →* ℂ)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ t : ℝ, 1 ≤ t →
      ‖normWeightedCount K M J m hM χ t‖ ≤
        B * (t ^ (Module.finrank ℚ K - 1) + 1) :=
  exists_normWeightedCount_bound K hMJ m hM χ
    (normWeight_sum_eq_zero K M J m hprod hM χ u hu)

/-- The actual count for the canonical ideal modulus mJ, with its finite enumeration derived. -/
def modulusNormWeightedCount (J : (Ideal (𝓞 K))⁰) (m : ℕ) (hm : m ≠ 0)
    (χ : ZMod m → ℂ) (t : ℝ) : ℂ :=
  letI := Fintype.ofFinite (IdealResidues K (modulusTimesIdeal K J m hm) J)
  normWeightedCount K (modulusTimesIdeal K J m hm) J m
    (modulusTimesIdeal_le_modulus K J m hm) χ t

/-- Surface-order cancellation for actual J/mJ weights, with no supplied finite mean
or coprimality condition on J. The residue-unit witness remains explicit. -/
theorem exists_modulusNormWeightedCount_bound (J : (Ideal (𝓞 K))⁰)
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →* ℂ)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ t : ℝ, 1 ≤ t →
      ‖modulusNormWeightedCount K J m hm χ t‖ ≤
        B * (t ^ (Module.finrank ℚ K - 1) + 1) := by
  let := Fintype.ofFinite (IdealResidues K (modulusTimesIdeal K J m hm) J)
  exact exists_normWeightedCount_bound_of_unit K (modulusTimesIdeal_le K J m hm) m
    (modulusTimesIdeal_le_modulus K J m hm) le_rfl χ u hu

end PaperX.NormResidueLattice
