import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : partition3 (3 : Fin 6) 4 := by
  norm_num [partition3_rel, label3]
