import KomorebiLSM.EllipsoidGeometry
import KomorebiLSM.BaseNormIntegration

/-! The Lorentz cylinder norm is the actual positive-decomposition base norm. -/
set_option autoImplicit false
namespace Komorebi.LSM.LorentzCylinder
open scoped BigOperators
variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

abbrev State (V : Type*) := ℝ × V
abbrev cone : Set (State V) := OrientedEllipsoid.lorentz
noncomputable abbrev probabilityCone : BaseNorm.ProbabilityCone (State V) :=
  OrientedEllipsoid.lorentzProbabilityCone

omit [NormedSpace ℝ V] in
@[simp] theorem mem_cone (z : State V) : z∈cone ↔ ‖z.2‖≤z.1 := Iff.rfl
@[simp] theorem mass_apply (z : State V) : probabilityCone.mass z=z.1 := rfl

omit [NormedSpace ℝ V] in
theorem max_le_cost {z u v : State V} (hu : u∈cone) (hv : v∈cone) (hz : z=u-v) :
    max |z.1| ‖z.2‖≤u.1+v.1 := by
  have hu0 : 0≤u.1 := (norm_nonneg _).trans hu
  have hv0 : 0≤v.1 := (norm_nonneg _).trans hv
  apply max_le
  · rw [hz,Prod.fst_sub]
    exact abs_sub_le_iff.mpr ⟨by linarith,by linarith⟩
  · rw [hz,Prod.snd_sub]
    exact (norm_sub_le _ _).trans (add_le_add hu hv)

theorem ray_mem {a : ℝ} (ha : 0≤a) {q : V} (hq : ‖q‖≤1) : (a,a • q)∈cone := by
  change ‖a • q‖≤a
  rw [norm_smul,Real.norm_eq_abs,abs_of_nonneg ha]
  simpa using mul_le_mul_of_nonneg_left hq ha

/-- The infimum is attained by two actual opposite positive rays. -/
theorem exists_minimal_decomposition (z : State V) :
    ∃ u∈cone,∃ v∈cone,z=u-v ∧ u.1+v.1=max |z.1| ‖z.2‖ := by
  let M : ℝ := max |z.1| ‖z.2‖
  have hM : 0≤M := (norm_nonneg z.2).trans (le_max_right _ _)
  have htM : |z.1|≤M := le_max_left _ _
  have hsM : ‖z.2‖≤M := le_max_right _ _
  by_cases hzero : M=0
  · rw [hzero] at htM hsM
    have ht : z.1=0 := abs_eq_zero.mp (le_antisymm htM (abs_nonneg _))
    have hs : z.2=0 := norm_eq_zero.mp (le_antisymm hsM (norm_nonneg _))
    have hz : z=0 := Prod.ext ht hs
    subst z
    exact ⟨0,probabilityCone.zero_mem,0,probabilityCone.zero_mem,by simp,by simp⟩
  · have hMp : 0<M := lt_of_le_of_ne hM (Ne.symm hzero)
    let q : V := M⁻¹ • z.2
    let a : ℝ := (M+z.1)/2
    let b : ℝ := (M-z.1)/2
    have ha : 0≤a := by dsimp [a]; linarith [neg_abs_le z.1]
    have hb : 0≤b := by dsimp [b]; linarith [le_abs_self z.1]
    have hab : a+b=M := by dsimp [a,b]; ring
    have hd : a-b=z.1 := by dsimp [a,b]; ring
    have hq : ‖q‖≤1 := by
      change ‖(M⁻¹ : ℝ) • z.2‖≤1
      rw [norm_smul,Real.norm_eq_abs,abs_of_nonneg (inv_nonneg.mpr hM)]
      exact (inv_mul_le_iff₀ hMp).mpr (by simpa using hsM)
    refine ⟨(a,a • q),ray_mem ha hq,(b,b • -q),ray_mem hb (by simpa using hq),?_,?_⟩
    · apply Prod.ext
      · exact hd.symm
      · change z.2=a • q-b • -q
        rw [smul_neg,sub_neg_eq_add,← add_smul,hab,smul_smul,mul_inv_cancel₀ hzero,one_smul]
    · exact hab

/-- This equality derives the stated norm from the actual cone infimum. -/
theorem value_eq (z : State V) : probabilityCone.value z=max |z.1| ‖z.2‖ := by
  apply le_antisymm
  · obtain ⟨u,hu,v,hv,hz,hcost⟩ := exists_minimal_decomposition z
    exact (probabilityCone.value_le_cost hu hv hz).trans_eq hcost
  · apply probabilityCone.le_value
    exact fun _ hu _ hv hz => max_le_cost hu hv hz

@[simp] theorem value_zero_mass (v : V) : probabilityCone.value (0,v)=‖v‖ := by
  rw [value_eq,abs_zero,max_eq_right (norm_nonneg _)]

@[simp] theorem mem_base (z : State V) : z∈probabilityCone.base ↔ z.1=1 ∧ ‖z.2‖≤1 := by
  change (‖z.2‖≤z.1 ∧ z.1=1) ↔ _
  constructor
  · rintro ⟨h,h1⟩
    exact ⟨h1,h.trans_eq h1⟩
  · rintro ⟨h1,h⟩
    exact ⟨h.trans_eq h1.symm,h1⟩

/-- A mass-preserving atlas pulls back every actual cone axiom. -/
noncomputable def atlasCone {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [FiniteDimensional ℝ E] (T : E ≃ₗ[ℝ] State V) : BaseNorm.ProbabilityCone E where
  carrier := T ⁻¹' cone
  zero_mem := by simp only [Set.mem_preimage,map_zero]; exact probabilityCone.zero_mem
  add_mem := by
    intro x y hx hy
    change T (x+y)∈cone
    rw [map_add]
    exact probabilityCone.add_mem hx hy
  smul_mem := by
    intro a ha x hx
    change T (a • x)∈cone
    rw [map_smul]
    exact probabilityCone.smul_mem ha hx
  spans := by
    apply top_unique
    intro z _
    obtain ⟨u,hu,v,hv,he⟩ := probabilityCone.exists_decomposition (T z)
    change u∈cone at hu
    change v∈cone at hv
    have he' : z=T.symm u-T.symm v :=
      (T.symm_apply_apply z).symm.trans ((congrArg T.symm he).trans (map_sub T.symm u v))
    rw [he']
    exact Submodule.sub_mem _
      (Submodule.subset_span (show T.symm u∈T ⁻¹' cone from by simpa only [Set.mem_preimage,LinearEquiv.apply_symm_apply] using hu))
      (Submodule.subset_span (show T.symm v∈T ⁻¹' cone from by simpa only [Set.mem_preimage,LinearEquiv.apply_symm_apply] using hv))
  mass := probabilityCone.mass.comp T.toLinearMap
  mass_pos := by
    intro x hx hne
    exact probabilityCone.mass_pos hx (by intro h; exact hne (T.injective (by simpa using h)))
  closed := probabilityCone.closed.preimage T.toLinearMap.continuous_of_finiteDimensional

@[simp] theorem atlasCone_mass {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [FiniteDimensional ℝ E] (T : E ≃ₗ[ℝ] State V) (z : E) :
    (atlasCone T).mass z=(T z).1 := rfl

end Komorebi.LSM.LorentzCylinder
