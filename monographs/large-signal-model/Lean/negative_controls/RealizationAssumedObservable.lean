import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example : hiddenModel.IsObservable := by
  simp only [hidden_model_not_observable]
