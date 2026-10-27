import KomorebiLSM.LegendreCounterexample
open MeasureTheory Komorebi.LSM Komorebi.LSM.LegendreCounterexample

/- Low moments agree at every sequence length, but the actual laws differ. -/
example : SequentialLowerCertificate.lawTV
    (law (1/2) (by norm_num) : Measure ℝ)
    (law (-(1/2)) (by norm_num) : Measure ℝ) = 0 := by
  rw [positive_law_totalVariation (by norm_num : (0 : ℝ) < 1/2) (by norm_num)]
  norm_num
