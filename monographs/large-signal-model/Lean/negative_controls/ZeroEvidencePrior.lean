import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : IsPrior (posterior prior3 (fun _ => 0)) := by
  constructor
  · intro i; simp [posterior, evidence]
  · norm_num [posterior, evidence]
