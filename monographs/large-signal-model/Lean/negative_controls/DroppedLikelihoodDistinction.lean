import KomorebiLSM.Block3Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FinitePartitions Komorebi.LSM.Block3Examples
open scoped BigOperators

example : likelihood6 () (3 : Fin 6) = likelihood6 () (5 : Fin 6) := by
  norm_num [likelihood6]
