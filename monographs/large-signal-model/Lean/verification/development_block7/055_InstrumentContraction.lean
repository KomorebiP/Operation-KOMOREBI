import KomorebiLSM.BaseNormTopology
import KomorebiLSM.RobustFiniteDomains

/-! P42: contraction in the constructed base norm and finite-generator maxima. -/
set_option autoImplicit false
namespace Komorebi.LSM.BaseNorm.ProbabilityCone
open scoped BigOperators
variable {E O : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [Fintype O] (C : ProbabilityCone E)

/-- These are positivity and mass constraints, not a contraction assumption. -/
def Instrument (B : O → E →ₗ[ℝ] E) : Prop :=
  (∀ o x, x ∈ C.carrier → B o x ∈ C.carrier) ∧
  (∀ x, ∑ o, C.mass (B o x)=C.mass x)

/-- P42's summed contraction, derived by taking the positive-decomposition infimum. -/
theorem instrument_contraction (B : O → E →ₗ[ℝ] E) (hB : C.Instrument B) (x : E) :
    ∑ o, C.value (B o x) ≤ C.value x := by
  apply C.le_value
  intro u hu v hv hx
  calc
    ∑ o, C.value (B o x) ≤ ∑ o, (C.mass (B o u)+C.mass (B o v)) := by
      apply Finset.sum_le_sum
      intro o _
      exact C.value_le_cost (hB.1 o u hu) (hB.1 o v hv) (by rw [hx,map_sub])
    _ = C.mass u+C.mass v := by rw [Finset.sum_add_distrib,hB.2,hB.2]

noncomputable def discrepancy (B D : O → E →ₗ[ℝ] E) (x : E) : ℝ :=
  ∑ o, C.value ((B o-D o) x)

noncomputable def instrumentError (B D : O → E →ₗ[ℝ] E) : ℝ :=
  sSup (C.discrepancy B D '' C.base)

theorem discrepancy_nonneg (B D : O → E →ₗ[ℝ] E) (x : E) : 0 ≤ C.discrepancy B D x :=
  Finset.sum_nonneg (fun o _ => C.value_nonneg _)

theorem discrepancy_smul (B D : O → E →ₗ[ℝ] E) {a : ℝ} (ha : 0 ≤ a) (x : E) :
    C.discrepancy B D (a • x) = a*C.discrepancy B D x := by
  simp only [discrepancy,map_smul,C.value_smul_of_nonneg ha,Finset.mul_sum]

theorem discrepancy_add_le (B D : O → E →ₗ[ℝ] E) (x y : E) :
    C.discrepancy B D (x+y) ≤ C.discrepancy B D x+C.discrepancy B D y := by
  simp only [discrepancy,map_add,← Finset.sum_add_distrib]
  exact Finset.sum_le_sum (fun o _ => C.value_add_le _ _)

theorem discrepancy_convex (B D : O → E →ₗ[ℝ] E) :
    ConvexOn ℝ Set.univ (C.discrepancy B D) := by
  refine ⟨convex_univ,?_⟩
  intro x _ y _ a b ha hb _
  simpa only [C.discrepancy_smul B D ha,C.discrepancy_smul B D hb,smul_eq_mul] using
    C.discrepancy_add_le B D (a • x) (b • y)

theorem discrepancy_le_two (B D : O → E →ₗ[ℝ] E)
    (hB : C.Instrument B) (hD : C.Instrument D) {x : E} (hx : x ∈ C.base) :
    C.discrepancy B D x ≤ 2 := by
  calc
    C.discrepancy B D x ≤ ∑ o, (C.value (B o x)+C.value (D o x)) :=
      Finset.sum_le_sum (fun o _ => C.value_sub_le _ _)
    _ = ∑ o, (C.mass (B o x)+C.mass (D o x)) := by
      apply Finset.sum_congr rfl
      intro o _
      rw [C.value_on_cone (hB.1 o x hx.1),C.value_on_cone (hD.1 o x hx.1)]
    _ = 2 := by rw [Finset.sum_add_distrib,hB.2,hD.2,hx.2]; norm_num

/-- A finite normalized generating hull has a genuine maximizing generator. -/
theorem discrepancy_max_generator {J : Type*} [Fintype J] [Nonempty J]
    (v : J → E) (hv : C.base = convexHull ℝ (Set.range v))
    (B D : O → E →ₗ[ℝ] E) :
    ∃ j, v j ∈ C.base ∧ C.instrumentError B D=C.discrepancy B D (v j) ∧
      ∀ x ∈ C.base, C.discrepancy B D x ≤ C.discrepancy B D (v j) := by
  classical
  obtain ⟨j,_,hj⟩ := Finset.exists_max_image Finset.univ
    (fun j => C.discrepancy B D (v j)) Finset.univ_nonempty
  have hjbase : v j ∈ C.base := by rw [hv]; exact subset_convexHull ℝ _ ⟨j,rfl⟩
  have hc : Convex ℝ {x | C.discrepancy B D x ≤ C.discrepancy B D (v j)} := by
    intro x hx y hy a b ha hb hab
    have he := (C.discrepancy_convex B D).2 (Set.mem_univ x) (Set.mem_univ y) ha hb hab
    change C.discrepancy B D (a • x+b • y) ≤ C.discrepancy B D (v j)
    have hm₁ := mul_le_mul_of_nonneg_left hx ha
    have hm₂ := mul_le_mul_of_nonneg_left hy hb
    simp only [smul_eq_mul] at he
    nlinarith
  have hK : ∀ x ∈ C.base, C.discrepancy B D x ≤ C.discrepancy B D (v j) := by
    rw [hv]
    apply convexHull_min _ hc
    rintro _ ⟨i,rfl⟩
    exact hj i (Finset.mem_univ i)
  refine ⟨j,hjbase,?_,hK⟩
  apply le_antisymm
  · exact csSup_le ⟨_,j,hjbase,rfl⟩ (by rintro r ⟨x,hx,rfl⟩; exact hK x hx)
  · apply le_csSup
    · exact ⟨_,by rintro r ⟨x,hx,rfl⟩; exact hK x hx⟩
    · exact ⟨v j,hjbase,rfl⟩

/-- The all-state supremum is at most two for two valid instruments. -/
theorem instrumentError_le_two (B D : O → E →ₗ[ℝ] E)
    (hB : C.Instrument B) (hD : C.Instrument D) (hne : C.base.Nonempty) :
    C.instrumentError B D ≤ 2 := by
  apply csSup_le (hne.image _)
  rintro r ⟨x,hx,rfl⟩
  exact C.discrepancy_le_two B D hB hD hx

/-- Normalization is used only on positive-mass states, with the zero state handled separately. -/
theorem discrepancy_homogeneous_bound (B D : O → E →ₗ[ℝ] E) (ε : ℝ)
    (hε : ∀ x ∈ C.base, C.discrepancy B D x ≤ ε)
    {y : E} (hy : y ∈ C.carrier) : C.discrepancy B D y ≤ ε*C.mass y := by
  by_cases hz : y=0
  · subst y; simp [discrepancy]
  have hm : 0<C.mass y := C.mass_pos hy hz
  let z := (C.mass y)⁻¹ • y
  have hb : z ∈ C.base := by
    refine ⟨C.smul_mem (inv_nonneg.mpr hm.le) hy,?_⟩
    simp [z,ne_of_gt hm]
  have he : y=C.mass y • z := by simp [z,smul_smul,ne_of_gt hm]
  calc
    C.discrepancy B D y = C.mass y*C.discrepancy B D z := by
      conv_lhs => rw [he]
      exact C.discrepancy_smul B D hm.le z
    _ ≤ C.mass y*ε := mul_le_mul_of_nonneg_left (hε z hb) hm.le
    _ = ε*C.mass y := mul_comm _ _

/-- One node of the observation tree, before conditioning. -/
theorem instrument_pair_step (B D : O → E →ₗ[ℝ] E) (hB : C.Instrument B)
    (ε : ℝ) (hε : ∀ x ∈ C.base, C.discrepancy B D x ≤ ε)
    (x : E) {y : E} (hy : y ∈ C.carrier) :
    ∑ o, C.value (B o x-D o y) ≤ C.value (x-y)+ε*C.mass y := by
  calc
    ∑ o, C.value (B o x-D o y) ≤
        ∑ o, (C.value (B o (x-y))+C.value ((B o-D o) y)) := by
      apply Finset.sum_le_sum
      intro o _
      have he : B o x-D o y = B o (x-y)+(B o-D o) y := by
        simp only [map_sub,LinearMap.sub_apply]; abel
      rw [he]
      exact C.value_add_le _ _
    _ = (∑ o, C.value (B o (x-y)))+C.discrepancy B D y := by
      rw [Finset.sum_add_distrib]; rfl
    _ ≤ C.value (x-y)+ε*C.mass y :=
      add_le_add (C.instrument_contraction B hB _) (C.discrepancy_homogeneous_bound B D ε hε hy)

end Komorebi.LSM.BaseNorm.ProbabilityCone
