import KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics
open Relativistic3DCenteredConvergence
open Relativistic3DFourierHilbertStability

example (f : Relativistic3DCenteredConvergence.CoeffL2)
    (n : Relativistic3DCenteredConvergence.Mode) :
    centeredCoeffOperator (-2) (-1) f n = centralHilbertModeOperator (-2) (-1) n (f n) :=
  centeredCoeffOperator_apply (-2) (-1) (by norm_num) f n

example : ‖centeredCoeffOperator (-2) (-1)‖ ≤ Real.sqrt 7 := by
  simpa using centeredCoeffOperator_norm_le (-2) (-1) (by norm_num)

example : IsSelfAdjoint (centeredCoeffOperator (-2) (-1)) :=
  centeredCoeffOperator_selfAdjoint (-2) (-1)

example (ψ : Relativistic3DCenteredConvergence.HilbertSpinor) :
    ‖centralHilbertModeOperator (-2) (-1) (fun _ => 0) ψ‖ ≤
      ‖continuumHilbertModeOperator (-2) (fun _ => 0) ψ‖ :=
  centered_mode_norm_le_continuum (-2) (-1) (fun _ => 0) ψ
