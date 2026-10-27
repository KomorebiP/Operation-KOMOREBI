import KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics
open Relativistic3DCenteredConvergence Relativistic3DFourierHilbertStability
open Relativistic3DFourierGenerator Relativistic3DFourierL2Generator

example (m h : ℝ) : centralHilbertModeOperator m h (fun _ => 0) =
    (m : ℂ) • betaHilbertOperator := by
  by_cases hh : h = 0 <;>
    simp [centralHilbertModeOperator, modeMomentum, sinQuot,
      Relativistic1DContinuumLimit.sinQuot, hh]

example : centeredCoeffOperator (-2) 0 = 0 := by simp [centeredCoeffOperator]

example : centralHilbertModeOperator (-2) (-1) (fun _ => 0)
    (spinorToHilbert ![1,0,0,0]) = (-2 : ℂ) • spinorToHilbert ![1,0,0,0] := by
  ext j
  fin_cases j <;>
    norm_num [centralHilbertModeOperator, modeMomentum, sinQuot,
      Relativistic1DContinuumLimit.sinQuot, betaHilbertOperator,
      hilbertCliffordOperator, spinorToHilbert, hilbertToSpinor,
      Relativistic3DCliffordTransportU1.hermitianBeta,
      Relativistic3DCliffordTransportU1.beta]
