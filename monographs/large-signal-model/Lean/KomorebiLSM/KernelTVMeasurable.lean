import KomorebiLSM.ContinuousTVDensity
import Mathlib.Probability.Kernel.RadonNikodym
import Mathlib.Probability.Kernel.MeasurableLIntegral

/-! Measurability of actual probability-kernel total variation follows from
joint Radon--Nikodym densities against the sum kernel. -/
set_option autoImplicit false
namespace Komorebi.LSM.KernelTVMeasurable
open MeasureTheory ProbabilityTheory
open scoped ENNReal
variable {X Y : Type*} [MeasurableSpace X] [MeasurableSpace Y]
variable [MeasurableSpace.CountableOrCountablyGenerated X Y]
variable (κ η : Kernel X Y) [IsMarkovKernel κ] [IsMarkovKernel η]

noncomputable def distance (x : X) : ℝ := SequentialLowerCertificate.lawTV (κ x) (η x)

noncomputable def leftDensity (x : X) (y : Y) : ℝ≥0∞ :=
  ENNReal.ofReal (Kernel.rnDerivAux κ (κ+η) x y)

noncomputable def rightDensity (x : X) (y : Y) : ℝ≥0∞ :=
  ENNReal.ofReal (1-Kernel.rnDerivAux κ (κ+η) x y)

omit [IsMarkovKernel κ] [IsMarkovKernel η] in
theorem leftDensity_measurable : Measurable (Function.uncurry (leftDensity κ η)) :=
  (Kernel.measurable_rnDerivAux κ (κ+η)).ennreal_ofReal

omit [IsMarkovKernel κ] [IsMarkovKernel η] in
theorem rightDensity_measurable : Measurable (Function.uncurry (rightDensity κ η)) :=
  (measurable_const.sub (Kernel.measurable_rnDerivAux κ (κ+η))).ennreal_ofReal

theorem leftDensity_kernel : (κ+η).withDensity (leftDensity κ η)=κ := by
  change (κ+η).withDensity (fun x y => ENNReal.ofReal (Kernel.rnDerivAux κ (κ+η) x y))=κ
  simpa only [ENNReal.ofNNReal_toNNReal] using Kernel.withDensity_rnDerivAux κ η

theorem rightDensity_kernel : (κ+η).withDensity (rightDensity κ η)=η := by
  change (κ+η).withDensity (fun x y => ENNReal.ofReal (1-Kernel.rnDerivAux κ (κ+η) x y))=η
  simpa only [ENNReal.ofNNReal_toNNReal] using Kernel.withDensity_one_sub_rnDerivAux κ η

theorem leftDensity_measure (x : X) :
    ((κ+η) x).withDensity (leftDensity κ η x)=κ x := by
  rw [← Kernel.withDensity_apply _ (leftDensity_measurable κ η),leftDensity_kernel κ η]

theorem rightDensity_measure (x : X) :
    ((κ+η) x).withDensity (rightDensity κ η x)=η x := by
  rw [← Kernel.withDensity_apply _ (rightDensity_measurable κ η),rightDensity_kernel κ η]

/-- The actual total variation has a jointly measurable reference-integral formula. -/
theorem distance_eq_lintegral (x : X) :
    distance κ η x=(1/2:ℝ)*(∫⁻ y,ENNReal.ofReal
      |(leftDensity κ η x y).toReal-(rightDensity κ η x y).toReal|∂(κ+η) x).toReal := by
  have : IsProbabilityMeasure (((κ+η) x).withDensity (leftDensity κ η x)) := by
    rw [leftDensity_measure κ η x]
    infer_instance
  have : IsProbabilityMeasure (((κ+η) x).withDensity (rightDensity κ η x)) := by
    rw [rightDensity_measure κ η x]
    infer_instance
  have h := ContinuousTVDensity.lawTV_withDensity_lintegral ((κ+η) x)
    (leftDensity κ η x) (rightDensity κ η x)
    (leftDensity_measurable κ η).of_uncurry_left.aemeasurable
    (rightDensity_measurable κ η).of_uncurry_left.aemeasurable
  simpa only [leftDensity_measure κ η x,rightDensity_measure κ η x,distance] using h

theorem distance_measurable : Measurable (distance κ η) := by
  have hd : Measurable (fun p : X × Y =>
      (leftDensity κ η p.1 p.2).toReal-(rightDensity κ η p.1 p.2).toReal) :=
    (leftDensity_measurable κ η).ennreal_toReal.sub (rightDensity_measurable κ η).ennreal_toReal
  have hm : Measurable (fun p : X × Y => ENNReal.ofReal
      |(leftDensity κ η p.1 p.2).toReal-(rightDensity κ η p.1 p.2).toReal|) := by
    simpa only [Function.comp_apply,Real.norm_eq_abs] using (measurable_norm.comp hd).ennreal_ofReal
  have he : distance κ η=(fun x => (1/2:ℝ)*(∫⁻ y,ENNReal.ofReal
      |(leftDensity κ η x y).toReal-(rightDensity κ η x y).toReal|∂(κ+η) x).toReal) :=
    funext (distance_eq_lintegral κ η)
  rw [he]
  exact measurable_const.mul (hm.lintegral_kernel_prod_right' (κ := κ+η)).ennreal_toReal

omit [MeasurableSpace.CountableOrCountablyGenerated X Y] in
theorem distance_nonneg (x : X) : 0≤distance κ η x :=
  SequentialLowerCertificate.lawTV_nonneg _ _

omit [MeasurableSpace.CountableOrCountablyGenerated X Y] in
theorem distance_le_one (x : X) : distance κ η x≤1 :=
  SequentialLowerCertificate.lawTV_le_one _ _

theorem distance_integrable (ρ : Measure X) [IsFiniteMeasure ρ] :
    Integrable (distance κ η) ρ := by
  apply Integrable.of_bound (distance_measurable κ η).aestronglyMeasurable 1
  filter_upwards [] with x
  simpa only [Real.norm_eq_abs,abs_of_nonneg (distance_nonneg κ η x)] using distance_le_one κ η x

end Komorebi.LSM.KernelTVMeasurable
