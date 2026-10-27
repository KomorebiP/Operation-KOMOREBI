import KomorebiLSM.BaseNorm

/-! Finite-dimensional closed cones with strict mass have compact bases.
The infimum construction is consequently nondegenerate. -/
set_option autoImplicit false
namespace Komorebi.LSM.BaseNorm.ProbabilityCone
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] (C : ProbabilityCone E)

/-- A uniform cone bound is derived by minimizing mass on the unit cone slice. -/
theorem exists_cone_bound : ∃ R > 0, ∀ x ∈ C.carrier, ‖x‖ ≤ R*C.mass x := by
  let S := Metric.sphere (0 : E) 1 ∩ C.carrier
  have hcompact : IsCompact S := (isCompact_sphere (0 : E) 1).inter_right C.closed
  have hunit : ∀ x : E, x ∈ C.carrier → x ≠ 0 → (‖x‖⁻¹ : ℝ) • x ∈ S := by
    intro x hx hn
    have hp : 0 < ‖x‖ := norm_pos_iff.mpr hn
    refine ⟨?_,C.smul_mem (inv_nonneg.mpr (norm_nonneg x)) hx⟩
    change dist ((‖x‖⁻¹ : ℝ) • x) 0 = 1
    simp only [dist_zero_right,norm_smul,Real.norm_eq_abs,abs_inv,abs_norm,
      inv_mul_cancel₀ (ne_of_gt hp)]
  by_cases hs : S.Nonempty
  · obtain ⟨y,hy,hmin⟩ := hcompact.exists_isMinOn hs C.mass.continuous_of_finiteDimensional.continuousOn
    have hny : ‖y‖=1 := by simpa only [Metric.mem_sphere,dist_zero_right] using hy.1
    have hyne : y ≠ 0 := by intro h; simp [h] at hny
    have hd : 0 < C.mass y := C.mass_pos hy.2 hyne
    refine ⟨(C.mass y)⁻¹,inv_pos.mpr hd,?_⟩
    intro x hx
    by_cases hn : x=0
    · simp [hn]
    have hp : 0<‖x‖ := norm_pos_iff.mpr hn
    have hm := hmin (hunit x hx hn)
    change C.mass y ≤ C.mass ((‖x‖⁻¹ : ℝ) • x) at hm
    simp only [map_smul,smul_eq_mul] at hm
    have hm' : C.mass y ≤ C.mass x/‖x‖ := by simpa only [div_eq_mul_inv,mul_comm] using hm
    have he := (le_div_iff₀ hp).mp hm'
    have ht : ‖x‖ ≤ C.mass x / C.mass y := (le_div_iff₀ hd).mpr (by nlinarith)
    simpa only [div_eq_mul_inv,mul_comm] using ht
  · refine ⟨1,by norm_num,?_⟩
    intro x hx
    have hn : x=0 := by
      by_contra h
      exact hs ⟨_,hunit x hx h⟩
    simp [hn]

theorem base_closed : IsClosed C.base :=
  C.closed.inter (isClosed_eq C.mass.continuous_of_finiteDimensional continuous_const)

/-- Compactness follows from the structural cone assumptions. -/
theorem base_compact : IsCompact C.base := by
  obtain ⟨R,_,hR⟩ := C.exists_cone_bound
  apply Metric.isCompact_of_isClosed_isBounded C.base_closed
  apply (Metric.isBounded_iff_subset_closedBall (0 : E)).mpr
  refine ⟨R,?_⟩
  intro x hx
  have h := hR x hx.1
  rw [hx.2,mul_one] at h
  simpa only [Metric.mem_closedBall,dist_zero_right] using h

omit [FiniteDimensional ℝ E] in
theorem base_convex : Convex ℝ C.base := by
  intro x hx y hy a b ha hb hab
  refine ⟨C.add_mem (C.smul_mem ha hx.1) (C.smul_mem hb hy.1),?_⟩
  simp only [map_add,map_smul,smul_eq_mul,hx.2,hy.2,mul_one,hab]

/-- The original ambient norm is bounded by a fixed multiple of the base norm. -/
theorem exists_norm_le_value : ∃ R > 0, ∀ x : E, ‖x‖ ≤ R*C.value x := by
  obtain ⟨R,hRp,hR⟩ := C.exists_cone_bound
  refine ⟨R,hRp,?_⟩
  intro x
  have h : ‖x‖/R ≤ C.value x := by
    apply C.le_value
    intro u hu v hv hx
    apply (div_le_iff₀ hRp).mpr
    have ht := norm_sub_le u v
    rw [hx]
    nlinarith [hR u hu,hR v hv]
  have hm := (div_le_iff₀ hRp).mp h
  simpa only [mul_comm] using hm

@[simp] theorem value_eq_zero_iff (x : E) : C.value x=0 ↔ x=0 := by
  constructor
  · intro h
    obtain ⟨R,_,hR⟩ := C.exists_norm_le_value
    have hb := hR x
    rw [h,mul_zero] at hb
    exact norm_eq_zero.mp (le_antisymm hb (norm_nonneg x))
  · intro h; simp [h]

/-- The actual infimum has every real norm law, including nondegeneracy. -/
theorem base_norm_laws :
    (∀ x, 0 ≤ C.value x) ∧
    (∀ x, C.value x=0 ↔ x=0) ∧
    (∀ x y, C.value (x+y) ≤ C.value x+C.value y) ∧
    (∀ a x, C.value (a • x)=|a| * C.value x) :=
  ⟨C.value_nonneg,C.value_eq_zero_iff,C.value_add_le,C.value_smul⟩

end Komorebi.LSM.BaseNorm.ProbabilityCone
