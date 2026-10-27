import KomorebiLSM.ContinuousBins
import KomorebiLSM.CellDistance

open MeasureTheory Komorebi.LSM
/- An unnormalized half-cell operator is not the normalized constant density.
Omitting division by the actual reference mass loses half the mass. -/
example : ContinuousBins.cellOperator UniformIntervalMoments.measure
    (fun _ : ℝ => ContinuousLinearMap.id ℝ ℝ) (Set.Ioc (-1:ℝ) 0) (1:ℝ)=1 := by
  rw [ContinuousBins.cellOperator_apply UniformIntervalMoments.measure
    (fun _ : ℝ => ContinuousLinearMap.id ℝ ℝ) (integrable_const _) (Set.Ioc (-1:ℝ) 0) 1]
  simp only [ContinuousLinearMap.id_apply]
  rw [setIntegral_const]
  change UniformIntervalMoments.measure.real (Set.Ioc (-1:ℝ) 0)*1=1
  rw [CellDistance.uniform_cell_mass (-1) 0 (by norm_num) (by norm_num) (by norm_num)]
  norm_num
