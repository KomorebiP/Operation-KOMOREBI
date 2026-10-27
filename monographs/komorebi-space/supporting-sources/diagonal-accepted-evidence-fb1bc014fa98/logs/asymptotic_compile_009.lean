import KomorebiSpace.DiagonalSeriesBounds
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
    convert! hi.div ((hi.pow 2).add_const 1) (by norm_num : (0 : ℝ)^2 + 1 ≠ 0) using 1
    norm_num
  apply h.congr'
  filter_upwards [eventually_gt_atTop (0 : ℝ)] with x hx
  field_simp

lemma kernelF_antiderivative (x : ℝ) :
    HasDerivAt (fun x : ℝ => (x / (1 + x ^ 2) + Real.arctan x) / 2) (kernelF x) x := by
  have hden : 1 + x ^ 2 ≠ 0 := by positivity
  have hd : HasDerivAt (fun x : ℝ => 1 + x ^ 2) (2 * x) x := by
    convert! ((hasDerivAt_id x).pow 2).const_add 1 using 1
    norm_num
  have hh := (((hasDerivAt_id x).div hd hden).add (Real.hasDerivAt_arctan' x)).div_const 2
  convert! hh using 1
  unfold kernelF kernelH
  dsimp
  field_simp
  ring

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

/-- Scaled positive-integer samples, without replacing the infinite series by a truncation. -/
def rightSum (k : ℝ → ℝ) (m : ℝ) : ℝ := (∑' n : ℕ, k (((n : ℝ) + 1) / m)) / m

lemma scaled_kernel_integrable {k : ℝ → ℝ} (hk : Integrable k) {m : ℝ} (hm : 0 < m) :
    Integrable (fun x : ℝ => k (x / m)) := by
  convert! hk.comp_mul_left' (inv_ne_zero hm.ne') using 1
  ext x
  congr 1
  ring

lemma scaled_kernel_integral (k : ℝ → ℝ) {m : ℝ} (hm : 0 < m) :
    (∫ x in Ioi (0 : ℝ), k (x / m)) = m * ∫ x in Ioi (0 : ℝ), k x := by
  simpa only [div_eq_mul_inv, inv_inv, zero_mul, smul_eq_mul] using
    integral_comp_mul_right_Ioi k 0 (inv_pos.mpr hm)

/-- The right-sampling error of a nonnegative decreasing kernel is at most its
initial height divided by the scale. -/
lemma rightSum_bounds {k : ℝ → ℝ} (hk : Integrable k)
    (ha : AntitoneOn k (Ici 0)) (hn : ∀ x, 0 ≤ k x) {m : ℝ} (hm : 0 < m) :
    (∫ x in Ioi (0 : ℝ), k x) - k 0 / m ≤ rightSum k m ∧
    rightSum k m ≤ ∫ x in Ioi (0 : ℝ), k x := by
  have hi := (scaled_kernel_integrable hk hm).integrableOn (s := Ioi 0)
  have ha' : AntitoneOn (fun x : ℝ => k (x / m)) (Ici 0) := by
    intro x hx y hy hxy
    exact ha (div_nonneg hx hm.le) (div_nonneg hy hm.le)
      (div_le_div_of_nonneg_right hxy hm.le)
  have hn' : ∀ x ∈ Ioi (0 : ℝ), 0 ≤ k (x / m) := fun x _ => hn _
  have hs := ha'.summable_of_integrableOn_Ioi_zero hi hn'
  have hu := ha'.tsum_add_one_le_integral hi hn'
  have hl := ha'.integral_le_tsum hs hn'
  rw [scaled_kernel_integral k hm] at hu hl
  rw [hs.tsum_eq_zero_add] at hl
  simp only [Nat.cast_zero, zero_div, Nat.cast_add, Nat.cast_one] at hu hl
  unfold rightSum
  constructor
  · apply (le_div_iff₀ hm).mpr
    calc
      ((∫ x in Ioi (0 : ℝ), k x) - k 0 / m) * m =
          m * (∫ x in Ioi (0 : ℝ), k x) - k 0 := by field_simp
      _ ≤ ∑' n : ℕ, k (((n : ℝ) + 1) / m) := by linarith
  · apply (div_le_iff₀ hm).mpr
    simpa only [mul_comm] using hu

lemma rightSum_tendsto {k : ℝ → ℝ} (hk : Integrable k)
    (ha : AntitoneOn k (Ici 0)) (hn : ∀ x, 0 ≤ k x) :
    Tendsto (fun m : ℕ => rightSum k m) atTop (𝓝 (∫ x in Ioi (0 : ℝ), k x)) := by
  have hlo : Tendsto (fun m : ℕ => (∫ x in Ioi (0 : ℝ), k x) - k 0 / m)
      atTop (𝓝 (∫ x in Ioi (0 : ℝ), k x)) := by
    simpa using tendsto_const_nhds.sub (tendsto_const_div_atTop_nhds_zero_nat (k 0))
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le' hlo tendsto_const_nhds
  · filter_upwards [eventually_ge_atTop 1] with m hm
    exact (rightSum_bounds hk ha hn (by exact_mod_cast (show 0 < m by omega))).1
  · filter_upwards [eventually_ge_atTop 1] with m hm
    exact (rightSum_bounds hk ha hn (by exact_mod_cast (show 0 < m by omega))).2

lemma kernelF_sample {m : ℕ} (hm : 1 ≤ m) (j : ℕ) :
    kernelF (((j : ℝ) + 1) / m) = (aCoord m j)^2 := by
  have hm0 : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  have hd := ne_of_gt (denominator_pos m j)
  unfold kernelF kernelH aCoord index at *
  field_simp

lemma kernelH_sample {m : ℕ} (hm : 1 ≤ m) (j : ℕ) :
    kernelH (((j : ℝ) + 1) / m) = (aCoord m j)^2 + (m : ℝ)^2 * (vCoord m j)^2 := by
  have hm0 : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  have hd := ne_of_gt (denominator_pos m j)
  unfold kernelH aCoord vCoord index at *
  field_simp

lemma A_div_eq_rightSum {m : ℕ} (hm : 1 ≤ m) : A m / m = rightSum kernelF m := by
  unfold A rightSum
  congr 1
  exact tsum_congr (fun j => (kernelF_sample hm j).symm)

lemma mul_B_eq_rightSum_sub {m : ℕ} (hm : 1 ≤ m) :
    (m : ℝ) * B m = rightSum kernelH m - rightSum kernelF m := by
  have hm0 : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  rw [← A_div_eq_rightSum hm]
  unfold rightSum
  rw [tsum_congr (kernelH_sample hm)]
  rw [(summable_aCoord_sq m).tsum_add ((summable_vCoord_sq m).mul_left ((m : ℝ)^2))]
  rw [(summable_vCoord_sq m).tsum_mul_left]
  change (m : ℝ) * B m = (A m + (m : ℝ)^2 * B m) / m - A m / m
  field_simp
  ring

/-- The actual infinite correction energy has leading coefficient pi/4. -/
theorem tendsto_A_div : Tendsto (fun m : ℕ => A m / m) atTop (𝓝 (Real.pi / 4)) := by
  have h := rightSum_tendsto kernelF_integrable kernelF_antitone (fun x => sq_nonneg (kernelH x))
  rw [kernelF_integral] at h
  apply h.congr'
  filter_upwards [eventually_ge_atTop 1] with m hm
  exact (A_div_eq_rightSum hm).symm

/-- The actual infinite residual energy has leading coefficient pi/4. -/
theorem tendsto_mul_B : Tendsto (fun m : ℕ => (m : ℝ) * B m) atTop (𝓝 (Real.pi / 4)) := by
  have hh := rightSum_tendsto kernelH_integrable kernelH_antitone kernelH_nonneg
  have hf := rightSum_tendsto kernelF_integrable kernelF_antitone (fun x => sq_nonneg (kernelH x))
  rw [kernelH_integral] at hh
  rw [kernelF_integral] at hf
  have h : Tendsto (fun m : ℕ => rightSum kernelH m - rightSum kernelF m)
      atTop (𝓝 (Real.pi / 4)) := by
    convert! hh.sub hf using 1
    ring
  apply h.congr'
  filter_upwards [eventually_ge_atTop 1] with m hm
  exact (mul_B_eq_rightSum_sub hm).symm

end KomorebiSpace.DiagonalRegularization
