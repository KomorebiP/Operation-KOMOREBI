import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example :
    (process [((),true)])⁻¹ • history process [((),true)] ≠
      (process [((),true),((),true)])⁻¹ • history process [((),true),((),true)] := by
  rw [different_histories_same_conditional_behavior]
  simp
