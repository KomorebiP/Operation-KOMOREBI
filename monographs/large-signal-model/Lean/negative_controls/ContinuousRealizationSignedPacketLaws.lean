import KomorebiLSM.ContinuousRealizationP61
open MeasureTheory Komorebi.LSM
private def policy : ContinuousRecords.Policy (A := Unit) (Y := ℝ) where
  probability _ _ _ := 1
  measurable_probability _ _ := measurable_const
  sum_one _ _ := by simp
/-- The signed packets 2 and -1 synthesize to 1. Their separately clipped raw
measures cannot be added as if each signed packet were a probability state. -/
example : ContinuousRecords.recordLaw ContinuousBins.QuadraticExample.instrument policy 2 0 Set.univ+
    ContinuousRecords.recordLaw ContinuousBins.QuadraticExample.instrument policy (-1) 0 Set.univ=
      ContinuousRecords.recordLaw ContinuousBins.QuadraticExample.instrument policy 1 0 Set.univ := by
  norm_num [ContinuousRecords.recordLaw,ContinuousRecords.reference,ContinuousRecords.recordDensity,
    ContinuousRecords.Policy.weight,ContinuousRecords.run,BaseNorm.scalarCone]
  rw [ENNReal.ofReal_eq_zero.mpr (by norm_num : (-1 : ℝ)≤0)]
  norm_num
