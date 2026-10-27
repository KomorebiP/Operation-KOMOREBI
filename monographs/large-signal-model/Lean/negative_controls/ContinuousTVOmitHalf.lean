import KomorebiLSM.ContinuousTVDensity
import KomorebiLSM.LegendreCounterexample

/-! Rejected control: omitting the probability-convention factor one half
would double the nonzero TV of the actual Legendre density laws. -/
open MeasureTheory Komorebi.LSM

example : SequentialLowerCertificate.lawTV
    (LegendreCounterexample.law (1/2) (by norm_num) : Measure ℝ)
    (LegendreCounterexample.law (-(1/2)) (by norm_num) : Measure ℝ)=13/40 := by
  rw [LegendreCounterexample.law_totalVariation (1/2) (by norm_num)]
  norm_num
