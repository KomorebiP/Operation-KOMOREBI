import PaperX.NormResidueLatticeMap
import PaperX.NormSignDilation

/-! Computed finite norm weights on the two actual sign regions.
The zero-mean premise concerns the actual ideal-lattice quotient; it is not
inferred from nontriviality of a character on a larger residue ring. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NormResidueLattice
open Ideal NumberField Module MeasureTheory
open PaperX.IdealClassQuantitative PaperX.ResidueLattice PaperX.NormResidue
open PaperX.NormSignGeometry PaperX.NormSignArithmetic
open scoped nonZeroDivisors Pointwise Classical

variable (K : Type*) [Field K] [NumberField K]

/-- A finite arithmetic norm weight, corrected for the sign of the field norm. -/
def normWeight (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (χ : ZMod m → ℂ) (positive : Bool) (c : IdealResidues K M J) : ℂ :=
  χ (if positive then residueNorm K M J m hM c else -residueNorm K M J m hM c)

/-- At every counted integer, the computed residue weight is its actual absolute principal norm. -/
theorem normWeight_mk (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (χ : ZMod m → ℂ) (positive : Bool) (x : (J : Ideal (𝓞 K)))
    {t : ℝ} (ht : 0 < t) (hx : integerPoint K x.1 ∈ t • signRegion K positive) :
    normWeight K M J m hM χ positive (Submodule.Quotient.mk (idealPointEquiv K J x)) =
      χ (Ideal.absNorm (Ideal.span {x.1}) : ZMod m) := by
  cases positive with
  | true =>
    have hs := (integer_norm_pos_of_mem_smul_signRegion K ht hx).le
    have hn := principal_absNorm_residue_nonneg K m hs
    rw [integerQuotientNorm_mk] at hn
    simp only [normWeight, ↓reduceIte, residueNorm_mk]
    exact congrArg χ hn.symm
  | false =>
    have hs := (integer_norm_neg_of_mem_smul_signRegion K ht hx).le
    have hn := principal_absNorm_residue_nonpos K m hs
    rw [integerQuotientNorm_mk] at hn
    simp only [normWeight, Bool.false_eq_true, ↓reduceIte, residueNorm_mk]
    exact congrArg χ hn.symm

/-- The two sign portions recombined before any roots-of-unity division. -/
def normWeightedCount (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m → ℂ) (t : ℝ) : ℂ :=
  ∑ positive : Bool,
    weightedFiberCount (idealEuclideanLattice K M) (idealEuclideanLattice K J)
      (signRegion K positive) (normWeight K M J m hM χ positive) t

/-- Vanishing of the two actual finite norm averages yields a surface-order bound
for the recombined arithmetic norm count. -/
theorem exists_normWeightedCount_bound {M J : (Ideal (𝓞 K))⁰}
    (hMJ : (M : Ideal (𝓞 K)) ≤ J) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m → ℂ)
    (hmean : ∀ positive : Bool, ∑ c : IdealResidues K M J, normWeight K M J m hM χ positive c = 0) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ t : ℝ, 1 ≤ t →
      ‖normWeightedCount K M J m hM χ t‖ ≤
        B * (t ^ (Module.finrank ℚ K - 1) + 1) := by
  choose B hB0 hB using exists_sign_zeroMean_bound K hMJ
  refine ⟨∑ positive : Bool,
    (∑ c : IdealResidues K M J, ‖normWeight K M J m hM χ positive c‖) * B positive, ?_, ?_⟩
  · exact Finset.sum_nonneg (fun positive _ =>
      mul_nonneg (Finset.sum_nonneg (fun _ _ => norm_nonneg _)) (hB0 positive))
  · intro t ht
    unfold normWeightedCount
    calc
      _ ≤ ∑ positive : Bool,
          ‖weightedFiberCount (idealEuclideanLattice K M) (idealEuclideanLattice K J)
            (signRegion K positive) (normWeight K M J m hM χ positive) t‖ := norm_sum_le _ _
      _ ≤ ∑ positive : Bool,
          ((∑ c : IdealResidues K M J, ‖normWeight K M J m hM χ positive c‖) * B positive) *
            (t ^ (Module.finrank ℚ K - 1) + 1) := by
          exact Finset.sum_le_sum (fun positive _ => hB positive _ (hmean positive) t ht)
      _ = _ := (Finset.sum_mul _ _ _).symm

end PaperX.NormResidueLattice
