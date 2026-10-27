import KomorebiLSM.ContinuousRealizationP61
open MeasureTheory Komorebi.LSM
private def policy : ContinuousRecords.Policy (A := Unit) (Y := ℝ) where
  probability _ _ _ := 1
  measurable_probability _ _ := measurable_const
  sum_one _ _ := by simp
/-- A valid exact polynomial density instrument does not make a negative-mass
initial vector into a probability state. The independent initial check matters. -/
example : ContinuousRecords.recordLaw ContinuousBins.QuadraticExample.instrument policy (-1) 0 Set.univ=1 := by
  norm_num [ContinuousRecords.recordLaw,ContinuousRecords.reference,ContinuousRecords.recordDensity,
    ContinuousRecords.Policy.weight,ContinuousRecords.run,BaseNorm.scalarCone]
