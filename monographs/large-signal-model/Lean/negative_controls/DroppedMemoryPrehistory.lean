import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : finiteMemory (scale 0) (fun _ => scale 1) 1
    (fun s : ℤ => if s = -1 then (1:ℝ) else 0) 0 = 0 := by
  norm_num [finiteMemory]
