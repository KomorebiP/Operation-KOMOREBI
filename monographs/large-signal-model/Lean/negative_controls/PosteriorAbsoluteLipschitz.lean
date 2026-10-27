import KomorebiLSM.Block11Examples
open Komorebi.LSM
example :
    ‖Filtering.normalize (ContinuousLinearMap.fst ℝ ℝ ℝ) ((1/4:ℝ),1/4) -
      Filtering.normalize (ContinuousLinearMap.fst ℝ ℝ ℝ) ((1/4:ℝ),0)‖ ≤ (1/4:ℝ) := by
  norm_num [Filtering.normalize, Prod.norm_def]
