import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example :
    summary (normalize mass (tinyInstrument.branch ((),true) initialPrior)) 1 -
      normalize summaryMass (wrongBranch (summary initialPrior)) 1 =
    oblique summaryMass (normalize summaryMass (wrongBranch (summary initialPrior))) actualDefect 1 := by
  rw [normalized_defect_coordinates.2,oblique_defect_coordinates.2]
  norm_num
