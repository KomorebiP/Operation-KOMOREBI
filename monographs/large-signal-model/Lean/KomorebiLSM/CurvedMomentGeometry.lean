import KomorebiLSM.MatrixRotation
import Mathlib.Analysis.Convex.Hull
import Mathlib.Tactic

/-! The exact three-coordinate truncated moment cone on [-1,1]. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open scoped Matrix BigOperators
abbrev State := Fin 3 → ℝ

def curve (u : ℝ) : State := ![1,u,u^2]
noncomputable def mass : State →ₗ[ℝ] ℝ := LinearMap.proj 0
noncomputable def momentMatrix : State →ₗ[ℝ] Matrix (Fin 2) (Fin 2) ℝ where
  toFun z := !![z 0,z 1;z 1,z 2]
  map_add' z w := by ext i j; fin_cases i <;> fin_cases j <;> simp
  map_smul' c z := by ext i j; fin_cases i <;> fin_cases j <;> simp

def cone : Set State := {z | (momentMatrix z).PosSemidef ∧ z 2 ≤ z 0}
def normalized : Set State := {z | z 0=1 ∧ (z 1)^2 ≤ z 2 ∧ z 2 ≤ 1}

@[simp] theorem mass_apply (z : State) : mass z=z 0 := rfl
@[simp] theorem momentMatrix_apply (z : State) : momentMatrix z=!![z 0,z 1;z 1,z 2] := rfl

theorem momentMatrix_psd_iff (z : State) :
    (momentMatrix z).PosSemidef ↔ 0≤z 0 ∧ 0≤z 2 ∧ (z 1)^2≤z 0*z 2 := by
  constructor
  · intro h
    have hd := h.det_nonneg
    rw [momentMatrix_apply,Matrix.det_fin_two] at hd
    change 0≤z 0*z 2-z 1*z 1 at hd
    exact ⟨h.diag_nonneg (i:=0),h.diag_nonneg (i:=1),by nlinarith⟩
  · rintro ⟨hm,hy,hxy⟩
    apply Matrix.PosSemidef.of_dotProduct_mulVec_nonneg
    · unfold Matrix.IsHermitian
      ext i j
      fin_cases i <;> fin_cases j <;> simp [Matrix.conjTranspose_apply]
    · intro v
      have h := MatrixRotation.binary_quadratic_nonneg _ _ _ hm hy hxy (v 0) (v 1)
      have he : star v ⬝ᵥ (momentMatrix z *ᵥ v)=z 0*(v 0)^2+2*z 1*v 0*v 1+z 2*(v 1)^2 := by
        simp [Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
        ring
      rw [he]
      exact h

theorem cone_iff (z : State) : z∈cone ↔
    0≤z 0 ∧ 0≤z 2 ∧ (z 1)^2≤z 0*z 2 ∧ z 2≤z 0 := by
  simp only [cone,Set.mem_ofPred_eq,momentMatrix_psd_iff]
  tauto

theorem curve_mem (u : ℝ) (hu : u∈Set.Icc (-1:ℝ) 1) : curve u∈cone := by
  rw [cone_iff]
  change 0≤(1:ℝ) ∧ 0≤u^2 ∧ u^2≤1*u^2 ∧ u^2≤1
  exact ⟨by norm_num,sq_nonneg _,by simp,by nlinarith [hu.1,hu.2]⟩

theorem cone_zero : (0:State)∈cone := by rw [cone_iff]; norm_num

theorem cone_add {x y : State} (hx : x∈cone) (hy : y∈cone) : x+y∈cone := by
  exact ⟨by simpa only [map_add] using hx.1.add hy.1,add_le_add hx.2 hy.2⟩

theorem cone_smul {a : ℝ} (ha : 0≤a) {z : State} (hz : z∈cone) : a•z∈cone := by
  exact ⟨by simpa only [map_smul] using hz.1.smul ha,mul_le_mul_of_nonneg_left hz.2 ha⟩

theorem cone_mass_zero {z : State} (hz : z∈cone) (hm : z 0=0) : z=0 := by
  obtain ⟨_,hy,hxy,hym⟩ := (cone_iff z).mp hz
  have h2 : z 2=0 := by linarith
  have h1 : z 1=0 := by nlinarith [sq_nonneg (z 1)]
  ext i
  fin_cases i <;> simp_all

theorem cone_spans : Submodule.span ℝ cone=⊤ := by
  apply top_unique
  intro z _
  have h0 : curve 0∈Submodule.span ℝ cone := Submodule.subset_span (curve_mem 0 (by norm_num))
  have h1 : curve 1∈Submodule.span ℝ cone := Submodule.subset_span (curve_mem 1 (by norm_num))
  have hn : curve (-1)∈Submodule.span ℝ cone := Submodule.subset_span (curve_mem (-1) (by norm_num))
  have he : z=(z 0-z 2)•curve 0+((z 2+z 1)/2)•curve 1+((z 2-z 1)/2)•curve (-1) := by
    ext i
    fin_cases i <;> simp [curve] <;> ring
  rw [he]
  exact Submodule.add_mem _ (Submodule.add_mem _ (Submodule.smul_mem _ _ h0)
    (Submodule.smul_mem _ _ h1)) (Submodule.smul_mem _ _ hn)

theorem cone_closed : IsClosed cone := by
  exact (Matrix.posSemidef_is_closed.preimage momentMatrix.continuous_of_finiteDimensional).inter
    (isClosed_le (continuous_apply 2) (continuous_apply 0))

noncomputable def probabilityCone : BaseNorm.ProbabilityCone State where
  carrier := cone
  zero_mem := cone_zero
  add_mem := cone_add
  smul_mem := cone_smul
  spans := cone_spans
  mass := mass
  mass_pos := by
    intro z hz hn
    have hm := (momentMatrix_psd_iff z).mp hz.1
    exact lt_of_le_of_ne hm.1 (fun he => hn (cone_mass_zero hz he.symm))
  closed := cone_closed

theorem base_eq_normalized : probabilityCone.base=normalized := by
  ext z
  simp only [BaseNorm.ProbabilityCone.base,probabilityCone,Set.mem_ofPred_eq,mass_apply,
    normalized,cone_iff]
  constructor
  · rintro ⟨⟨_,_,hxy,hym⟩,hm⟩
    exact ⟨hm,by simpa [hm] using hxy,by simpa [hm] using hym⟩
  · rintro ⟨hm,hxy,hym⟩
    exact ⟨⟨by simp [hm],(sq_nonneg _).trans hxy,by simpa [hm] using hxy,
      by simpa [hm] using hym⟩,hm⟩

theorem normalized_bounds {z : State} (hz : z∈normalized) :
    |z 1|≤1 ∧ 0≤z 2 ∧ z 2≤1 := by
  have h2 := (sq_nonneg (z 1)).trans hz.2.1
  exact ⟨abs_le.mpr ⟨by nlinarith [hz.2.1,hz.2.2],by nlinarith [hz.2.1,hz.2.2]⟩,h2,hz.2.2⟩

theorem convex_hull_curve : convexHull ℝ (curve '' Set.Icc (-1:ℝ) 1)=normalized := by
  apply Set.Subset.antisymm
  · apply convexHull_min
    · rintro _ ⟨u,hu,rfl⟩
      rw [←base_eq_normalized]
      exact ⟨curve_mem u hu,rfl⟩
    · rw [←base_eq_normalized]
      intro x hx y hy a b ha hb hab
      refine ⟨probabilityCone.convex_carrier hx.1 hy.1 ha hb hab,?_⟩
      simp only [map_add,map_smul,hx.2,hy.2,smul_eq_mul,mul_one]
      exact hab
  · intro z hz
    have hcv := convex_convexHull ℝ (curve '' Set.Icc (-1:ℝ) 1)
    have hmem (u : ℝ) (hu : u∈Set.Icc (-1:ℝ) 1) :
        curve u∈convexHull ℝ (curve '' Set.Icc (-1:ℝ) 1) := subset_convexHull ℝ _ ⟨u,hu,rfl⟩
    have hb := normalized_bounds hz
    have hx : z 1∈Set.Icc (-1:ℝ) 1 := abs_le.mp hb.1
    have he : ![1,z 1,1] = ((1-z 1)/2)•curve (-1)+((1+z 1)/2)•curve 1 := by
      ext i
      fin_cases i <;> simp [curve] <;> ring
    have htop : ![1,z 1,1]∈convexHull ℝ (curve '' Set.Icc (-1:ℝ) 1) := by
      rw [he]
      exact hcv (hmem (-1) (by norm_num)) (hmem 1 (by norm_num))
        (by linarith [hx.2]) (by linarith [hx.1]) (by ring)
    by_cases hsq : (z 1)^2=1
    · have heq : z=curve (z 1) := by
        ext i
        fin_cases i
        · exact hz.1
        · rfl
        · change z 2=(z 1)^2
          nlinarith [hz.2.1,hz.2.2]
      rw [heq]
      exact hmem _ hx
    · have hd : 0<1-(z 1)^2 := by
        have hh : (z 1)^2<1 := lt_of_le_of_ne (hz.2.1.trans hz.2.2) hsq
        linarith
      let t := (z 2-(z 1)^2)/(1-(z 1)^2)
      have ht0 : 0≤t := div_nonneg (sub_nonneg.mpr hz.2.1) hd.le
      have ht1 : t≤1 := (div_le_one hd).mpr (by linarith [hz.2.2])
      have heq : z=(1-t)•curve (z 1)+t•![1,z 1,1] := by
        ext i
        fin_cases i <;> simp [curve,t,hz.1] <;> field_simp [ne_of_gt hd] <;> ring
      rw [heq]
      exact hcv (hmem _ hx) htop (by linarith) ht0 (by ring)

end Komorebi.LSM.CurvedMoment
