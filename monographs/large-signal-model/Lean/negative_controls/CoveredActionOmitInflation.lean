import KomorebiLSM.CoveredActionBoundaries

/-! With positive coverage one half, the actual weighted observation can be
two; retaining the unweighted unit range is false. -/
set_option autoImplicit false
open Komorebi.LSM.CoveredAdaptiveActions
open Komorebi.LSM.CoveredAdaptiveActions.Boundaries
example : weightedTest halfPolicy oneTest true ((),(true,true))≤1 := by
  rw [covered_weight_two]
  norm_num
