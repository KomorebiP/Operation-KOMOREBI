import PaperX.ResidueLatticeIdeal
import PaperX.ResidueLatticePointSums
import Mathlib.Analysis.Complex.Basic

/-! Complex weighted counts of actual finite additive residue fibers. -/
set_option autoImplicit false
set_option maxHeartbeats 50000
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

/-- A common weighted discrepancy estimate over a specified finite index type. -/
def WeightedEstimate {Q : Type*} [Fintype Q] (a : Q → ℝ → ℕ)
    (main boundary : ℝ → ℝ) : Prop :=
  ∃ C : ℝ, 0 ≤ C ∧ ∀ (w : Q → ℂ) (t : ℝ), 1 ≤ t →
    ‖(∑ c : Q, w c * (a c t : ℂ)) - (main t : ℂ) * ∑ c : Q, w c‖ ≤
      (∑ c : Q, ‖w c‖) * C * boundary t

/-- The zero-mean version of a weighted discrepancy estimate. -/
def ZeroMeanEstimate {Q : Type*} [Fintype Q] (a : Q → ℝ → ℕ)
    (boundary : ℝ → ℝ) : Prop :=
  ∃ C : ℝ, 0 ≤ C ∧ ∀ (w : Q → ℂ), (∑ c : Q, w c) = 0 →
    ∀ t : ℝ, 1 ≤ t → ‖∑ c : Q, w c * (a c t : ℂ)‖ ≤
      (∑ c : Q, ‖w c‖) * C * boundary t

/-- An abstract finite-family estimate transports uniform counting errors to every complex weight. -/
theorem weightedEstimate_of_uniform_bound {Q : Type*} [Fintype Q]
    (a : Q → ℝ → ℕ) (main boundary : ℝ → ℝ)
    (h : ∃ C : ℝ, 0 ≤ C ∧ ∀ c t, 1 ≤ t → |(a c t : ℝ) - main t| ≤ C * boundary t) :
    WeightedEstimate a main boundary := by
  obtain ⟨C, hC, hb⟩ := h
  refine ⟨C, hC, fun w t ht => ?_⟩
  exact (norm_weighted_nat_error_le w (fun c => a c t) (main t) (C * boundary t)
    (fun c => hb c t ht)).trans_eq (mul_assoc _ _ _).symm

/-- Zero mean cancels the common main coefficient. -/
theorem WeightedEstimate.zeroMean {Q : Type*} [Fintype Q] {a : Q → ℝ → ℕ}
    {main boundary : ℝ → ℝ} (h : WeightedEstimate a main boundary) :
    ZeroMeanEstimate a boundary := by
  obtain ⟨C, hC, hb⟩ := h
  refine ⟨C, hC, fun w hw t ht => ?_⟩
  simpa only [hw, mul_zero, sub_zero] using hb w t ht

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  (L₀ L : Submodule ℤ E) [DiscreteTopology L₀] [IsZLattice ℝ L₀]
  [DiscreteTopology L] [IsZLattice ℝ L]
  [Fintype (Residues L₀ L)]

/-- One constant controls every weight on the actual residue quotient by its finite L1 norm. -/
theorem exists_weightedFiber_bound (h : L₀ ≤ L)
    {ι : Type*} [Fintype ι] (b : Basis ι ℤ L₀) {D : Set E}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LatticeCounting.LipschitzBoundaryAtlas ι
      (LatticeCountingTransport.coordinates L₀ b '' D)) :
    WeightedEstimate (fiberCount L₀ L D)
      (fun t => t ^ Fintype.card ι * ((volume.real D / ZLattice.covolume L) /
        Nat.card (Residues L₀ L)))
      (fun t => t ^ (Fintype.card ι - 1) + 1) :=
  weightedEstimate_of_uniform_bound _ _ _
    (exists_fiber_discrepancy_bound (E := E) L₀ L h (ι := ι) b (D := D) hDm hDb A)

/-- A zero-mean actual residue weight cancels the entire main term. -/
theorem exists_zeroMean_weightedFiber_bound (h : L₀ ≤ L)
    {ι : Type*} [Fintype ι] (b : Basis ι ℤ L₀) {D : Set E}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LatticeCounting.LipschitzBoundaryAtlas ι
      (LatticeCountingTransport.coordinates L₀ b '' D)) :
    ZeroMeanEstimate (fiberCount L₀ L D) (fun t => t ^ (Fintype.card ι - 1) + 1) :=
  (exists_weightedFiber_bound (E := E) L₀ L h (ι := ι) b (D := D) hDm hDb A).zeroMean

end PaperX.ResidueLattice
