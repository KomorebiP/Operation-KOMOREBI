import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example : (core process selected selected)⁻¹ * shiftedCore process selected selected ((),false) =
    reconstructed process selected selected ((),false) := by
  rw [inverse_core_explicit,shifted_false,learned_false]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [Matrix.mul_apply,Fin.sum_univ_succ]
