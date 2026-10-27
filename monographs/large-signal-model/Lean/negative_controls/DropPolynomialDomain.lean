import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : ‖diagonalQuadratic (2,0)-diagonalQuadratic (0,0)‖ ≤
    2*‖((2,0):ℝ×ℝ)-((0,0):ℝ×ℝ)‖ := by
  rw [diagonalQuadratic_formula,diagonalQuadratic_formula]
  norm_num
