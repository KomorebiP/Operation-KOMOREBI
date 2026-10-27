import KomorebiLSM.LegendreCounterexample
open MeasureTheory Komorebi.LSM Komorebi.LSM.LegendreCounterexample

/- Probability total variation is half the variation of the density difference. -/
example : SequentialLowerCertificate.lawTV
    (law (1/2) (by norm_num) : Measure ℝ)
    (law (-(1/2)) (by norm_num) : Measure ℝ) = 13/40 := by
  rw [positive_law_totalVariation (by norm_num : (0 : ℝ) < 1/2) (by norm_num)]
  norm_num
