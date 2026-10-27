import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : ∃ s : ℝ, 0 < s ∧ ∀ i : Fin 2, unequal2 i = s * (1 : ℝ) := by
  refine ⟨1, by norm_num, ?_⟩
  intro i
  fin_cases i <;> norm_num [unequal2]
