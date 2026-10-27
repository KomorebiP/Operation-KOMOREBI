import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : outsideState ∈ realizableBeliefs summary := by
  simp only [mass_one_does_not_imply_realizability.2]
