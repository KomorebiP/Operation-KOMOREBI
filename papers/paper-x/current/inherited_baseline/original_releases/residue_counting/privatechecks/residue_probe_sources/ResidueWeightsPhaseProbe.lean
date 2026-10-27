import PaperX.ResidueLatticeIdeal
import PaperX.ResidueLatticePointSums
import Mathlib.Analysis.Complex.Basic

/-! Complex weighted counts of actual finite additive residue fibers. -/
set_option autoImplicit false
set_option maxHeartbeats 10000
set_option backward.isDefEq.respectTransparency.types false
noncomputable section
namespace PaperX.ResidueLattice
open Set Module MeasureTheory
open scoped Pointwise BigOperators

/-- Summing a common real error bound against arbitrary complex weights. -/
theorem norm_weighted_error_le {Q : Type*} [Fintype Q] (w : Q → ℂ) (a : Q → ℝ)
    (main B : ℝ) (h : ∀ c, |a c - main| ≤ B) :
    ‖(∑ c, w c * (a c : ℂ)) - (main : ℂ) * ∑ c, w c‖ ≤
      (∑ c, ‖w c‖) * B := by
  have he : (∑ c, w c * (a c : ℂ)) - (main : ℂ) * ∑ c, w c =
      ∑ c, w c * ((a c - main : ℝ) : ℂ) := by
    simp only [Complex.ofReal_sub, mul_sub, Finset.sum_sub_distrib,
      Finset.mul_sum]
    congr 1
    exact Finset.sum_congr rfl (fun c _ => mul_comm _ _)
  rw [he, Finset.sum_mul]
  exact (norm_sum_le _ _).trans (Finset.sum_le_sum (fun c _ => by
    rw [norm_mul, Complex.norm_real, Real.norm_eq_abs]
    exact mul_le_mul_of_nonneg_left (h c) (norm_nonneg _)))

/-- The same weighted estimate for natural counting functions, with casts normalized once. -/
theorem norm_weighted_nat_error_le {Q : Type*} [Fintype Q] (w : Q → ℂ) (a : Q → ℕ)
    (main B : ℝ) (h : ∀ c, |(a c : ℝ) - main| ≤ B) :
    ‖(∑ c, w c * (a c : ℂ)) - (main : ℂ) * ∑ c, w c‖ ≤
      (∑ c, ‖w c‖) * B := by
  simpa only [Complex.ofReal_natCast] using norm_weighted_error_le w (fun c => (a c : ℝ)) main B h

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  (L₀ L : Submodule ℤ E) [DiscreteTopology L₀] [IsZLattice ℝ L₀]
  [DiscreteTopology L] [IsZLattice ℝ L]
  [Fintype (Residues L₀ L)]

/-- A single geometric constant controls every complex weight by its finite L1 norm. -/
theorem exists_weightedFiber_bound (h : L₀ ≤ L)
    {ι : Type*} [Fintype ι] (b : Basis ι ℤ L₀) {D : Set E}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LatticeCounting.LipschitzBoundaryAtlas ι
      (LatticeCountingTransport.coordinates L₀ b '' D)) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ (w : Residues L₀ L → ℂ) (t : ℝ), 1 ≤ t →
      ‖weightedFiberCount L₀ L D w t -
        ((t ^ Fintype.card ι * ((volume.real D / ZLattice.covolume L) /
          Nat.card (Residues L₀ L)) : ℝ) : ℂ) * ∑ c, w c‖ ≤
        (∑ c, ‖w c‖) * C * (t ^ (Fintype.card ι - 1) + 1) := by
  trace "entered weighted proof"
  obtain ⟨C, hC, hbound⟩ := exists_fiber_discrepancy_bound L₀ L h (ι := ι) b (D := D) hDm hDb A
  trace "imported bound"
  refine ⟨C, hC, fun w t ht => ?_⟩
  trace "refined witnesses"
  unfold weightedFiberCount
  trace "unfolded"
  calc
    _ ≤ (∑ c, ‖w c‖) * (C * (t ^ (Fintype.card ι - 1) + 1)) :=
      norm_weighted_nat_error_le (Q := Residues L₀ L) w (fun c => fiberCount L₀ L D c t)
        (t ^ Fintype.card ι * ((volume.real D / ZLattice.covolume L) /
          Nat.card (Residues L₀ L))) (C * (t ^ (Fintype.card ι - 1) + 1))
        (fun c => hbound c t ht)
    _ = _ := (mul_assoc (∑ c, ‖w c‖) C (t ^ (Fintype.card ι - 1) + 1)).symm



end PaperX.ResidueLattice
