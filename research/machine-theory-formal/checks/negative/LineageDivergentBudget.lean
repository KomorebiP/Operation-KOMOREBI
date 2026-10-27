import MachineTheory.Lineage
open MeasureTheory Set
open scoped ENNReal
open Komorebi.MachineTheory

example {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ] :
    μ.real (⋃ _ : ℕ, (univ : Set Ω)) ≤ ∑' _ : ℕ, (1 : ℝ) := by
  rw [Lineage.divergent_real_tsum_zero]
  simp only [Set.iUnion_const, measureReal_def, measure_univ, ENNReal.toReal_one]
  norm_num
