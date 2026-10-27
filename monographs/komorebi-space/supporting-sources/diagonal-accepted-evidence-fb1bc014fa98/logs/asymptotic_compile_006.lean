import Mathlib.Analysis.SumIntegralComparisons
import Mathlib.Analysis.SpecialFunctions.ImproperIntegrals
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic

set_option autoImplicit false
noncomputable section
open Filter Set MeasureTheory
open scoped Topology
namespace KomorebiSpace.DiagonalRegularization

/-- The integrable decreasing kernel whose square controls correction energy. -/
def kernelH (x : ℝ) : ℝ := (1 + x ^ 2)⁻¹
/-- The correction-energy kernel. -/
def kernelF (x : ℝ) : ℝ := (kernelH x) ^ 2

lemma kernelH_nonneg (x : ℝ) : 0 ≤ kernelH x := by
  unfold kernelH
  positivity

lemma kernelH_le_one (x : ℝ) : kernelH x ≤ 1 := by
  exact inv_le_one_of_one_le₀ (by nlinarith [sq_nonneg x])

lemma kernelH_continuous : Continuous kernelH := by
  unfold kernelH
  exact (show Continuous (fun x : ℝ => 1 + x ^ 2) from
    continuous_const.add (continuous_id.pow 2)).inv₀
    (fun x => ne_of_gt (by nlinarith [sq_nonneg x]))

lemma kernelF_continuous : Continuous kernelF := kernelH_continuous.pow 2

lemma kernelH_integrable : Integrable kernelH := integrable_inv_one_add_sq

lemma kernelF_integrable : Integrable kernelF := by
  apply kernelH_integrable.mono' kernelF_continuous.aestronglyMeasurable
  filter_upwards with x
  rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
  unfold kernelF
  nlinarith [kernelH_nonneg x, kernelH_le_one x]

lemma kernelH_antitone : AntitoneOn kernelH (Ici 0) := by
  intro x hx y hy hxy
  unfold kernelH
  apply inv_anti₀ (by positivity)
  nlinarith [sq_le_sq₀ hx hy |>.mpr hxy]

lemma kernelF_antitone : AntitoneOn kernelF (Ici 0) := by
  intro x hx y hy hxy
  exact (sq_le_sq₀ (kernelH_nonneg y) (kernelH_nonneg x)).mpr
    (kernelH_antitone hx hy hxy)

lemma kernelH_integral : (∫ x in Ioi (0 : ℝ), kernelH x) = Real.pi / 2 := by
  simp [kernelH]

lemma rational_kernel_tendsto :
    Tendsto (fun x : ℝ => x / (1 + x ^ 2)) atTop (𝓝 0) := by
  have hi : Tendsto (fun x : ℝ => x⁻¹) atTop (𝓝 (0 : ℝ)) := tendsto_inv_atTop_zero
  have h : Tendsto (fun x : ℝ => x⁻¹ / (x⁻¹ ^ 2 + 1)) atTop (𝓝 (0 : ℝ)) := by
    convert! hi.div ((hi.pow 2).add_const 1) (by norm_num : (0 : ℝ)^2 + 1 ≠ 0) using 1 <;> norm_num
  apply h.congr'
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with x hx
  field_simp

lemma kernelF_antiderivative (x : ℝ) :
    HasDerivAt (fun x : ℝ => (x / (1 + x ^ 2) + Real.arctan x) / 2) (kernelF x) x := by
  have hden : 1 + x ^ 2 ≠ 0 := by positivity
  have hd : HasDerivAt (fun x : ℝ => 1 + x ^ 2) (2 * x) x := by
    convert! ((hasDerivAt_id x).pow 2).const_add 1 using 1 <;> norm_num
  have hh := (((hasDerivAt_id x).div hd hden).add (Real.hasDerivAt_arctan' x)).div_const 2
  convert! hh using 1
  unfold kernelF kernelH
  dsimp
  field_simp
  <;> ring

lemma kernelF_integral : (∫ x in Ioi (0 : ℝ), kernelF x) = Real.pi / 4 := by
  have ht : Tendsto (fun x : ℝ => (x / (1 + x ^ 2) + Real.arctan x) / 2)
      atTop (𝓝 (Real.pi / 4)) := by
    convert! (rational_kernel_tendsto.add
      (tendsto_nhds_of_tendsto_nhdsWithin Real.tendsto_arctan_atTop)).div_const 2 using 1
    ring
  have hi := integral_Ioi_of_hasDerivAt_of_tendsto'
    (fun x (_ : x ∈ Ici (0 : ℝ)) => kernelF_antiderivative x)
    kernelF_integrable.integrableOn ht
  simpa using hi

end KomorebiSpace.DiagonalRegularization
