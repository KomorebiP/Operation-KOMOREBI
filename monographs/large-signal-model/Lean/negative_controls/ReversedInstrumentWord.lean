import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : mass (wordAction tinyInstrument.branch [((),true),((),false)] initialPrior) =
    mass (wordAction tinyInstrument.branch [((),false),((),true)] initialPrior) := by
  norm_num [true_then_false_probability,false_then_true_probability]
