import KomorebiLSM.StatisticalRefinement

open MeasureTheory
open scoped ENNReal MeasureTheory

/- A finer information set gives a weak improvement. A zero target cannot
have a strictly positive improvement. This strengthening must be rejected. -/
example {Ω : Type*} {m₀ : MeasurableSpace Ω} {μ : Measure Ω}
    {mF mG : MeasurableSpace Ω} (hF : mF ≤ m₀) (hG : mG ≤ m₀) :
    Komorebi.LSM.StatisticalRefinement.squaredRisk (0 : Lp ℝ 2 μ)
        (condExpL2 ℝ ℝ hG (0 : Lp ℝ 2 μ) : Lp ℝ 2 μ) <
      Komorebi.LSM.StatisticalRefinement.squaredRisk (0 : Lp ℝ 2 μ)
        (condExpL2 ℝ ℝ hF (0 : Lp ℝ 2 μ) : Lp ℝ 2 μ) := by
  norm_num [Komorebi.LSM.StatisticalRefinement.squaredRisk_eq_norm_sq]
