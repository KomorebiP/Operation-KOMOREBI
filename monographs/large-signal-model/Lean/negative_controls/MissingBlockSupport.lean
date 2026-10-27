import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : aggregate coarse3 (posterior (pointMass 0) likelihood3) true = 1 := by
  norm_num [aggregate, posterior, evidence, coarse3, pointMass, likelihood3, Fin.sum_univ_succ]
