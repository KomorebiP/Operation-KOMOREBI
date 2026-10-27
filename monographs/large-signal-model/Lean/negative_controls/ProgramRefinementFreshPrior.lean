import KomorebiLSM.ProgramRefinement

open Komorebi.LSM.ProgramRefinement

-- Assigning the entire former prior to each of two duplicates doubles evidence.
example : childEvidence (1 / 3 : ℝ) (fun _ : Bool => 1) (fun _ => 1) = 1 / 3 := by
  norm_num [childEvidence, childPrior, tsum_fintype]
