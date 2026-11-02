import CoupledRescaling
open Komorebi.SpecialFunctions.Coupled
open Scales
example : ∃ A B : ℂ, A ≠ 0 ∧ B ≠ 0 ∧
    ∀ z, workedScales.V z = A * workedScales.U (B * z) := by
  apply (workedScales.component_rescaling_iff_defect workedScales_positive
    (by norm_num [workedScales])).mpr
  rw [workedScales_defect]
  norm_num
