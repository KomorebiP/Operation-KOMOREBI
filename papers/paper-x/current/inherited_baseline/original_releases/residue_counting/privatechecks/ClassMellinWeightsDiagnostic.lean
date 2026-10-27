import PaperX.ResidueLatticeIdeal
import PaperX.ResidueLatticePointSums
set_option autoImplicit false
set_option maxHeartbeats 10000
set_option diagnostics true
noncomputable section
open Set Module MeasureTheory
open scoped Pointwise BigOperators
open PaperX.ResidueLattice
#check @weightedFiberCount
#check @exists_fiber_discrepancy_bound
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  (L₀ L : Submodule ℤ E) [DiscreteTopology L₀] [IsZLattice ℝ L₀]
  [DiscreteTopology L] [IsZLattice ℝ L]
  [Fintype (Residues L₀ L)] {ι : Type*} [Fintype ι] (D : Set E)
#check (∃ C : ℝ, 0 ≤ C ∧ ∀ (w : Residues L₀ L → ℂ) (t : ℝ), 1 ≤ t →
      ‖weightedFiberCount L₀ L D w t -
        ((t ^ Fintype.card ι * ((volume.real D / ZLattice.covolume L) /
          Nat.card (Residues L₀ L)) : ℝ) : ℂ) * ∑ c : Residues L₀ L, w c‖ ≤
        (∑ c : Residues L₀ L, ‖w c‖) * C * (t ^ (Fintype.card ι - 1) + 1) : Prop)
