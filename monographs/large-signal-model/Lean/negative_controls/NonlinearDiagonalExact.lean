import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : fullQuadratic (2,3)=diagonalQuadratic (2,3) := by
  have h := nonlinear_cross_term_numeric
  linarith
