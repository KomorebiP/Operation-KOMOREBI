import KomorebiLSM.PredictableResidual
/- Even the first two time weights exceed a half-unit total budget. -/
example : (∑ n ∈ Finset.range 2, Komorebi.LSM.PredictableResidual.timeWeight n) ≤
    (1/2:NNReal) := by
  norm_num [Komorebi.LSM.PredictableResidual.timeWeight,Finset.sum_range_succ]
