import KomorebiLSM.TimeRecords
import KomorebiLSM.UniformIntervalMoments
import KomorebiLSM.BaseNormModels
open MeasureTheory Komorebi.LSM

noncomputable def constantInstrument : ContinuousInstrument.DensityInstrument (A := Unit)
    BaseNorm.scalarCone UniformIntervalMoments.measure where
  op _ _ := ContinuousLinearMap.id ℝ ℝ
  measurable_op _ := measurable_const
  integrable_op _ := integrable_const _
  positive _ := ae_of_all _ fun _ _ hz => hz
  mass_preserving _ z := by simp

noncomputable def quadraticOp (u : ℝ) : ℝ →L[ℝ] ℝ := (3 * u^2) • ContinuousLinearMap.id ℝ ℝ

theorem quadraticOp_integrable : Integrable quadraticOp UniformIntervalMoments.measure :=
  (UniformIntervalMoments.continuous_integrable (by fun_prop : Continuous (fun u : ℝ => 3 * u^2))).smul_const _

noncomputable def quadraticInstrument : ContinuousInstrument.DensityInstrument (A := Unit)
    BaseNorm.scalarCone UniformIntervalMoments.measure where
  op _ := quadraticOp
  measurable_op _ := by unfold quadraticOp; fun_prop
  integrable_op _ := quadraticOp_integrable
  positive _ := ae_of_all _ fun u z hz => mul_nonneg (by positivity : 0 ≤ 3 * u^2) hz
  mass_preserving _ z := by
    rw [ContinuousLinearMap.integral_apply quadraticOp_integrable z]
    change (∫ u, (3 * u^2) * z ∂UniformIntervalMoments.measure) = z
    rw [integral_mul_const, integral_const_mul]
    change 3 * UniformIntervalMoments.moment 2 * z = z
    rw [UniformIntervalMoments.moment_two]
    ring

/- Step0 has density3u² and step1 has density1. At observations(1,0), the actual
operator product has mass3. Reusing the step0 instrument would instead give0. -/
example : TimeRecords.run (fun n => if n = 0 then quadraticInstrument else constantInstrument) (1 : ℝ) 2
      ((PUnit.unit, ((), (1 : ℝ))), ((), (0 : ℝ))) = 0 := by
  norm_num [TimeRecords.run, quadraticInstrument, quadraticOp, constantInstrument]
