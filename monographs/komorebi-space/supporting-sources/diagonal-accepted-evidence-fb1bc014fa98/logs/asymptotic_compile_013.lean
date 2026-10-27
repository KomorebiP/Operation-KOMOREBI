import KomorebiSpace.InfiniteDiagonalModel
import KomorebiSpace.MonotoneBudgetAsymptotic
import KomorebiSpace.BudgetProfileGeometry
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

lemma A_nonneg (m : ℕ) : 0 ≤ A m := tsum_nonneg (fun _ => sq_nonneg _)
lemma B_nonneg (m : ℕ) : 0 ≤ B m := tsum_nonneg (fun _ => sq_nonneg _)

lemma A_pos {m : ℕ} (hm : 1 ≤ m) : 0 < A m := by
  have hmp : (0 : ℝ) < m := by exact_mod_cast (show 0 < m by omega)
  exact lt_of_lt_of_le (div_pos hmp (by norm_num)) (A_lower m hm)

lemma aCoord_monotone (j : ℕ) : Monotone (fun m => aCoord m j) := by
  intro m n hmn
  have hsq : (m : ℝ)^2 ≤ (n : ℝ)^2 :=
    (sq_le_sq₀ (Nat.cast_nonneg m) (Nat.cast_nonneg n)).mpr (by exact_mod_cast hmn)
  unfold aCoord
  apply (div_le_div_iff₀ (denominator_pos m j) (denominator_pos n j)).mpr
  nlinarith [mul_nonneg (sub_nonneg.mpr hsq) (sq_nonneg (index j))]

lemma A_monotone : Monotone A := by
  intro m n hmn
  exact Summable.tsum_le_tsum (fun j => (sq_le_sq₀ (aCoord_nonneg m j) (aCoord_nonneg n j)).mpr
    (aCoord_monotone j hmn)) (summable_aCoord_sq m) (summable_aCoord_sq n)

lemma A_tendsto_atTop : Tendsto A atTop atTop := by
  apply tendsto_atTop_mono' atTop ?_
    ((tendsto_natCast_atTop_atTop : Tendsto (fun m : ℕ => (m : ℝ)) atTop atTop).atTop_div_const (by norm_num : (0 : ℝ) < 4))
  filter_upwards [eventually_ge_atTop 1] with m hm
  exact A_lower m hm

lemma A_successor_ratio_tendsto :
    Tendsto (fun m : ℕ => A (m+1) / A m) atTop (𝓝 1) := by
  have hc : Real.pi / 4 ≠ 0 := ne_of_gt (div_pos Real.pi_pos (by norm_num))
  have hn : Tendsto (fun m : ℕ => A (m+1) / ((m+1 : ℕ) : ℝ)) atTop (𝓝 (Real.pi / 4)) :=
    tendsto_A_div.comp (tendsto_add_atTop_nat 1)
  have hrat : Tendsto (fun m : ℕ => ((m : ℝ)+1) / m) atTop (𝓝 1) := by
    convert! tendsto_add_mul_div_add_mul_atTop_nhds (1 : ℝ) 0 1 (by norm_num : (1 : ℝ) ≠ 0) using 1 <;> simp [add_comm]
  have h : Tendsto (fun m : ℕ =>
      (A (m+1) / ((m+1 : ℕ) : ℝ)) / (A m / m) * (((m : ℝ)+1) / m)) atTop (𝓝 1) := by
    convert! (hn.div tendsto_A_div hc).mul hrat using 1
    simp [hc]
  apply h.congr'
  filter_upwards [eventually_ge_atTop 1] with m hm
  have hm0 : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  have hn0 : (m : ℝ) + 1 ≠ 0 := by positivity
  have ha0 : A m ≠ 0 := ne_of_gt (A_pos hm)
  push_cast
  field_simp

lemma sqrt_A_mul_sqrt_B_tendsto :
    Tendsto (fun m : ℕ => Real.sqrt (A m) * Real.sqrt (B m)) atTop (𝓝 (Real.pi / 4)) := by
  have h : Tendsto (fun m : ℕ => Real.sqrt ((A m / m) * ((m : ℝ) * B m)))
      atTop (𝓝 (Real.pi / 4)) := by
    have ht := Real.continuous_sqrt.continuousAt.tendsto.comp (tendsto_A_div.mul tendsto_mul_B)
    simpa only [Function.comp_def, Real.sqrt_mul_self (by positivity : 0 ≤ Real.pi / 4)] using ht
  apply h.congr'
  filter_upwards [eventually_ge_atTop 1] with m hm
  have hm0 : (m : ℝ) ≠ 0 := by exact_mod_cast (show m ≠ 0 by omega)
  rw [← Real.sqrt_mul (A_nonneg m)]
  congr 1
  field_simp

/-- A strictly positive mesh of actual correction norms. -/
def budgetMesh (n : ℕ) : ℝ := Real.sqrt (A (n+1))

lemma budgetMesh_pos (n : ℕ) : 0 < budgetMesh n := Real.sqrt_pos.mpr (A_pos (by omega))

lemma budgetMesh_monotone : Monotone budgetMesh := by
  intro m n hmn
  exact Real.sqrt_le_sqrt (A_monotone (Nat.add_le_add_right hmn 1))

lemma budgetMesh_tendsto_atTop : Tendsto budgetMesh atTop atTop :=
  Real.tendsto_sqrt_atTop.comp (A_tendsto_atTop.comp (tendsto_add_atTop_nat 1))

lemma budgetMesh_ratio_tendsto :
    Tendsto (fun n => budgetMesh (n+1) / budgetMesh n) atTop (𝓝 1) := by
  have h := Real.continuous_sqrt.continuousAt.tendsto.comp
    (A_successor_ratio_tendsto.comp (tendsto_add_atTop_nat 1))
  simpa only [Function.comp_def, Real.sqrt_one, Real.sqrt_div (A_nonneg _), budgetMesh] using h

lemma budgetMesh_product_tendsto :
    Tendsto (fun n => budgetMesh n * BudgetProfile.beta T w (budgetMesh n))
      atTop (𝓝 (Real.pi / 4)) := by
  have h := sqrt_A_mul_sqrt_B_tendsto.comp (tendsto_add_atTop_nat 1)
  convert! h using 1
  ext n
  rw [budgetMesh, budget_at_sqrt_A (by omega)]
  rfl

/-- The limit holds over all real correction budgets, not only the regularization mesh. -/
theorem tendsto_actual_budget_product :
    Tendsto (fun M : ℝ => M * BudgetProfile.beta T w M) atTop (𝓝 (Real.pi / 4)) := by
  apply tendsto_budget_product_of_mesh budgetMesh (BudgetProfile.beta T w) (Real.pi / 4)
    budgetMesh_pos budgetMesh_monotone budgetMesh_tendsto_atTop
  · intro x hx y hy hxy
    exact BudgetProfileGeometry.beta_antitone T w hx hxy
  · intro M hM
    exact BudgetProfile.beta_nonneg T w M
  · exact budgetMesh_ratio_tendsto
  · exact budgetMesh_product_tendsto

/-- The omitted reciprocal-square energy after a hard prefix. -/
def hardPrefixTail (N : ℕ) : ℝ := ∑' j, (wCoord (j + N))^2

lemma hardPrefixTail_eq_pseries (N : ℕ) :
    hardPrefixTail N = ∑' j : ℕ, 1 / ((N : ℝ) + j + 1)^2 := by
  apply tsum_congr
  intro j
  simp [wCoord, index, Nat.cast_add, one_div, inv_pow, add_comm]

lemma hardPrefixTail_bounds (N : ℕ) (hN : 1 ≤ N) :
    1 / ((N : ℝ)+1) ≤ hardPrefixTail N ∧ hardPrefixTail N ≤ 1 / (N : ℝ) := by
  rw [hardPrefixTail_eq_pseries]
  exact ⟨series_tail_sq_lower N (summable_tail_pseries N 2 (by norm_num)),
    series_tail_sq_upper N hN⟩

lemma mul_hardPrefixTail_tendsto :
    Tendsto (fun N : ℕ => (N : ℝ) * hardPrefixTail N) atTop (𝓝 1) := by
  apply tendsto_of_tendsto_of_tendsto_of_le_of_le'
    (tendsto_natCast_div_add_atTop (1 : ℝ)) tendsto_const_nhds
  · filter_upwards [eventually_ge_atTop 1] with N hN
    have h := mul_le_mul_of_nonneg_left (hardPrefixTail_bounds N hN).1 (Nat.cast_nonneg N : (0 : ℝ) ≤ N)
    simpa only [mul_one_div] using h
  · filter_upwards [eventually_ge_atTop 1] with N hN
    have hn0 : (N : ℝ) ≠ 0 := by exact_mod_cast (show N ≠ 0 by omega)
    have h := mul_le_mul_of_nonneg_left (hardPrefixTail_bounds N hN).2 (Nat.cast_nonneg N : (0 : ℝ) ≤ N)
    simpa [hn0] using h

/-- The hard-prefix residual product tends to one at its actual correction norm budget. -/
theorem tendsto_hardPrefix_product :
    Tendsto (fun N : ℕ => ‖hardPrefix N‖ * ‖w - T (hardPrefix N)‖) atTop (𝓝 1) := by
  have h := Real.continuous_sqrt.continuousAt.tendsto.comp mul_hardPrefixTail_tendsto
  have hr (N : ℕ) : ‖w - T (hardPrefix N)‖ = Real.sqrt (hardPrefixTail N) := by
    unfold hardPrefixTail
    rw [← norm_hardPrefix_residual_sq, Real.sqrt_sq (norm_nonneg _)]
  simpa only [Function.comp_def, Real.sqrt_one, norm_hardPrefix, hr,
    Real.sqrt_mul (Nat.cast_nonneg _)] using h

end KomorebiSpace.DiagonalRegularization
