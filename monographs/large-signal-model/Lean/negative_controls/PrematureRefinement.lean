import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : (partition2 (3 : Fin 6) 4 ↔ partition3 (3 : Fin 6) 4) := by
  norm_num [partition2_rel, partition3_rel, label2, label3]
