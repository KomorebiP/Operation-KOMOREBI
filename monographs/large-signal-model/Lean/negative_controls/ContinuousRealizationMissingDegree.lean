import KomorebiLSM.ContinuousRealizationP61
import KomorebiLSM.LegendreCounterexample
open MeasureTheory Komorebi.LSM.LegendreCounterexample
/-- Validity and identical moments zero through two do not identify an
unrestricted density class; P61 must retain its declared degree assumption. -/
example : (law (1/2) (by norm_num) : Measure ℝ)=
    (law (-(1/2)) (by norm_num) : Measure ℝ) := by
  have hn : (law (1/2) (by norm_num) : Measure ℝ)≠
      (law (-(1/2)) (by norm_num) : Measure ℝ) :=
    laws_distinct (by norm_num) (by norm_num)
  simp only [hn]
