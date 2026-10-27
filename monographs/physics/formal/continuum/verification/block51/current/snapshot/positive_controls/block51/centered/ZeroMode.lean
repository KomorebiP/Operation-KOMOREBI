import KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics
open Relativistic3DCenteredConvergence Relativistic3DFourierHilbertStability
open Relativistic3DFourierGenerator Relativistic3DFourierL2Generator

private theorem zero_mode_symbol (m h : ℝ) : centralHilbertModeOperator m h (fun _ => 0) =
    (m : ℂ) • betaHilbertOperator := by
  by_cases hh : h = 0 <;>
    simp [centralHilbertModeOperator, modeMomentum, sinQuot,
      Relativistic1DContinuumLimit.sinQuot, hh] <;> module

example : centeredCoeffOperator (-2) 0 = 0 := by simp [centeredCoeffOperator]

example : centralHilbertModeOperator (-2) (-1) (fun _ => 0)
    (spinorToHilbert ![1,0,0,0]) = (-2 : ℂ) • spinorToHilbert ![1,0,0,0] := by
  rw [zero_mode_symbol]
  ext j
  fin_cases j <;>
    norm_num [betaHilbertOperator, hilbertCliffordOperator, hilbertCliffordLinear,
      spinorToHilbert, hilbertToSpinor,
      Relativistic3DCliffordHilbertRefinement.hermitianBeta,
      Relativistic3DCliffordHilbertRefinement.cliffordBeta,
      Relativistic3DCliffordTransportU1.beta]
  all_goals rfl
