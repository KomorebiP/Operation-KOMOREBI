import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : aggregate coarse3 (posterior prior3 likelihood3) false -
    posterior (aggregate coarse3 prior3) (fun _ => 1) false = 0 := by
  norm_num [aggregate, posterior, evidence, coarse3, prior3, likelihood3, Fin.sum_univ_succ]
