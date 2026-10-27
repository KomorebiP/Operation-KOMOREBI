import PaperX.ResidueLatticeIdealWeights
import PaperX.ResidueLatticeIdealPoints

/-! Actual ideal-residue counts in the norm threshold, with power-saving error. -/
set_option autoImplicit false
noncomputable section
open Ideal Module
open scoped nonZeroDivisors Real Classical Pointwise BigOperators
open NumberField
namespace PaperX.ResidueLattice
open PaperX.IdealClassQuantitative
variable (K : Type*) [Field K] [NumberField K]
  (M J : (Ideal (𝓞 K))⁰)

/-- Actual points of the ideal lattice in one residue with the prescribed norm threshold. -/
def idealNormFiberCount (c : IdealResidues K M J) (y : ℝ) : ℕ :=
  Nat.card {x : idealEuclideanLattice K J //
    (Submodule.Quotient.mk x : IdealResidues K M J) = c ∧ x.1 ∈ coneRegion K y}

/-- Dilation changes the actual cone norm threshold by the number-field degree. -/
theorem idealFiberCount_eq_normFiberCount (c : IdealResidues K M J) {t : ℝ} (ht : 0 < t) :
    idealFiberCount K M J c t = idealNormFiberCount K M J c (t ^ Module.finrank ℚ K) := by
  unfold idealFiberCount fiberCount idealNormFiberCount
  rw [smul_coneRegion_one K ht]

/-- The norm-threshold count is an actual congruence count of algebraic integers of J. -/
theorem idealNormFiberCount_eq_integer_count (a : (J : Ideal (𝓞 K))) (y : ℝ) :
    idealNormFiberCount K M J (Submodule.Quotient.mk (idealPointEquiv K J a)) y =
      Nat.card {x : (J : Ideal (𝓞 K)) // x.1 - a.1 ∈ (M : Ideal (𝓞 K)) ∧
        integerPoint K x.1 ∈ coneRegion K y} := by
  unfold idealNormFiberCount
  exact Nat.card_congr ((idealPointEquiv K J).subtypeEquiv (fun x => by
    simp only [idealPoint_residue_eq_iff]
    rfl)).symm

/-- All actual additive residues have the same main coefficient and a power-saving norm error. -/
theorem exists_idealNormFiber_bound (h : (M : Ideal (𝓞 K)) ≤ J) :
    ∃ B : ℝ, 0 ≤ B ∧ ∀ (c : IdealResidues K M J) (y : ℝ), 1 ≤ y →
      |(idealNormFiberCount K M J c y : ℝ) -
        y * (latticeDensity K J / Nat.card (IdealResidues K M J))| ≤
        B * (y ^ countExponent K + 1) := by
  obtain ⟨B, hB, hb⟩ := exists_idealFiber_bound K h
  refine ⟨B, hB, fun c y hy => ?_⟩
  have hy0 : 0 < y := lt_of_lt_of_le zero_lt_one hy
  have hd : Module.finrank ℚ K ≠ 0 := (Module.finrank_pos (R := ℚ) (M := K)).ne'
  have ht : 1 ≤ y ^ (Module.finrank ℚ K : ℝ)⁻¹ :=
    Real.one_le_rpow hy (by positivity)
  have H := hb c (y ^ (Module.finrank ℚ K : ℝ)⁻¹) ht
  rw [idealFiberCount_eq_normFiberCount K M J c (Real.rpow_pos_of_pos hy0 _),
    Real.rpow_inv_natCast_pow hy0.le hd, root_boundary_power K y hy0.le] at H
  exact H

variable [Fintype (IdealResidues K M J)]

/-- Arbitrary complex residue weights have the actual finite average as leading coefficient. -/
theorem exists_idealNormWeighted_bound (h : (M : Ideal (𝓞 K)) ≤ J) :
    WeightedEstimate (idealNormFiberCount K M J)
      (fun y => y * (latticeDensity K J / Nat.card (IdealResidues K M J)))
      (fun y => y ^ countExponent K + 1) :=
  weightedEstimate_of_uniform_bound _ _ _ (exists_idealNormFiber_bound K M J h)

/-- Zero mean gives genuine power-saving cancellation for actual norm-truncated residue counts. -/
theorem exists_zeroMean_idealNormWeighted_bound (h : (M : Ideal (𝓞 K)) ≤ J) :
    ZeroMeanEstimate (idealNormFiberCount K M J) (fun y => y ^ countExponent K + 1) :=
  (exists_idealNormWeighted_bound K M J h).zeroMean

end PaperX.ResidueLattice
