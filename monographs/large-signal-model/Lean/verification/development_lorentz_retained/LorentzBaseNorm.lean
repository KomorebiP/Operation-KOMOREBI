import KomorebiLSM.BaseNorm
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FinCases

/-! The actual positive-decomposition base norm of the Lorentz cone. -/
set_option autoImplicit false
namespace Komorebi.LSM.LorentzBaseNorm
open BaseNorm

abbrev State := Fin 3 → ℝ

def spatial : State →ₗ[ℝ] ℂ where
  toFun z := ⟨z 1,z 2⟩
  map_add' := by intro x y; apply Complex.ext <;> rfl
  map_smul' := by intro a z; apply Complex.ext <;> simp [Pi.smul_apply]

def point (t : ℝ) (w : ℂ) : State := ![t,w.re,w.im]

def mass : State →ₗ[ℝ] ℝ := LinearMap.proj 0

def carrier : Set State := {z | ‖spatial z‖ ≤ z 0}

@[simp] theorem mass_apply (z : State) : mass z=z 0 := rfl
@[simp] theorem spatial_apply_re (z : State) : (spatial z).re=z 1 := rfl
@[simp] theorem spatial_apply_im (z : State) : (spatial z).im=z 2 := rfl
@[simp] theorem point_zero (t : ℝ) (w : ℂ) : point t w 0=t := by simp [point]
@[simp] theorem point_one (t : ℝ) (w : ℂ) : point t w 1=w.re := by simp [point]
@[simp] theorem point_two (t : ℝ) (w : ℂ) : point t w 2=w.im := by simp [point]
@[simp] theorem spatial_point (t : ℝ) (w : ℂ) : spatial (point t w)=w := by apply Complex.ext <;> simp
@[simp] theorem point_mass_spatial (z : State) : point (z 0) (spatial z)=z := by
  funext i; fin_cases i <;> simp

theorem spatial_norm (z : State) : ‖spatial z‖=Real.sqrt (z 1^2+z 2^2) := by
  rw [Complex.norm_eq_sqrt_sq_add_sq]
  rfl

theorem carrier_zero : (0:State) ∈ carrier := by simp [carrier]

theorem carrier_mass_nonneg {z : State} (hz : z∈carrier) : 0≤z 0 :=
  (norm_nonneg _).trans hz

theorem carrier_add {x y : State} (hx : x∈carrier) (hy : y∈carrier) : x+y∈carrier := by
  change ‖spatial (x+y)‖ ≤ x 0+y 0
  rw [map_add]
  exact (norm_add_le _ _).trans (add_le_add hx hy)

theorem carrier_smul {a : ℝ} (ha : 0≤a) {z : State} (hz : z∈carrier) : a • z∈carrier := by
  change ‖spatial (a • z)‖ ≤ a*z 0
  rw [map_smul,norm_smul,Real.norm_eq_abs,abs_of_nonneg ha]
  exact mul_le_mul_of_nonneg_left hz ha

theorem spatial_eq_zero_and_mass_eq_zero {z : State} (hs : spatial z=0) (ht : z 0=0) : z=0 := by
  rw [← point_mass_spatial z, hs, ht]
  funext i; fin_cases i <;> simp

theorem carrier_mass_pos {z : State} (hz : z∈carrier) (hne : z≠0) : 0<z 0 := by
  have hn := carrier_mass_nonneg hz
  apply lt_of_le_of_ne hn
  intro he
  have hs : spatial z=0 := norm_eq_zero.mp (le_antisymm (hz.trans_eq he.symm) (norm_nonneg _))
  exact hne (spatial_eq_zero_and_mass_eq_zero hs he.symm)

theorem carrier_closed : IsClosed carrier := by
  exact isClosed_le (spatial.continuous_of_finiteDimensional.norm) (continuous_apply 0)

/-- Every vector is an actual difference of two Lorentz-positive vectors. -/
theorem exists_positive_decomposition (z : State) :
    ∃ u∈carrier, ∃ v∈carrier, z=u-v := by
  let M : ℝ := ‖spatial z‖+|z 0|
  refine ⟨point M (spatial z), ?_, point (M-z 0) 0, ?_, ?_⟩
  · change ‖spatial (point M (spatial z))‖ ≤ M
    simp only [spatial_point]
    exact le_add_of_nonneg_right (abs_nonneg _)
  · change ‖spatial (point (M-z 0) 0)‖ ≤ M-z 0
    rw [spatial_point,norm_zero]
    dsimp [M]
    linarith [norm_nonneg (spatial z), le_abs_self (z 0)]
  · funext i
    fin_cases i <;> simp [point]

theorem carrier_spans : Submodule.span ℝ carrier=⊤ := by
  apply top_unique
  intro z _
  obtain ⟨u,hu,v,hv,hz⟩ := exists_positive_decomposition z
  rw [hz]
  exact Submodule.sub_mem _ (Submodule.subset_span hu) (Submodule.subset_span hv)

noncomputable def coneInstance : ProbabilityCone State where
  carrier := carrier
  zero_mem := carrier_zero
  add_mem := carrier_add
  smul_mem := carrier_smul
  spans := carrier_spans
  mass := mass
  mass_pos := carrier_mass_pos
  closed := carrier_closed

@[simp] theorem coneInstance_carrier (z : State) : z∈coneInstance.carrier ↔ ‖spatial z‖≤z 0 := Iff.rfl
@[simp] theorem coneInstance_mass (z : State) : coneInstance.mass z=z 0 := rfl

theorem max_le_cost {z u v : State} (hu : u∈carrier) (hv : v∈carrier) (hz : z=u-v) :
    max |z 0| ‖spatial z‖ ≤ u 0+v 0 := by
  apply max_le
  · rw [hz,Pi.sub_apply]
    exact abs_sub_le_iff.mpr ⟨by linarith [carrier_mass_nonneg hv], by linarith [carrier_mass_nonneg hu]⟩
  · rw [hz,map_sub]
    exact (norm_sub_le _ _).trans (add_le_add hu hv)

/-- A unit spatial direction supplies positive rays at both opposite boundary points. -/
theorem point_ray_mem {a : ℝ} (ha : 0≤a) {q : ℂ} (hq : ‖q‖≤1) :
    point a (a • q)∈carrier := by
  change ‖spatial (point a (a • q))‖ ≤ a
  rw [spatial_point,norm_smul,Real.norm_eq_abs,abs_of_nonneg ha]
  simpa using mul_le_mul_of_nonneg_left hq ha

/-- The minimum positive-decomposition cost is attained, including zero. -/
theorem exists_minimal_decomposition (z : State) :
    ∃ u∈carrier, ∃ v∈carrier, z=u-v ∧
      u 0+v 0=max |z 0| ‖spatial z‖ := by
  let M : ℝ := max |z 0| ‖spatial z‖
  have hM : 0≤M := (norm_nonneg (spatial z)).trans (le_max_right _ _)
  have htM : |z 0|≤M := le_max_left _ _
  have hsM : ‖spatial z‖≤M := le_max_right _ _
  by_cases hzero : M=0
  · rw [hzero] at htM hsM
    have ht : z 0=0 := abs_eq_zero.mp (le_antisymm htM (abs_nonneg _))
    have hs : spatial z=0 := norm_eq_zero.mp (le_antisymm hsM (norm_nonneg _))
    have hz := spatial_eq_zero_and_mass_eq_zero hs ht
    subst z
    exact ⟨0,carrier_zero,0,carrier_zero,by simp,by simp⟩
  · have hMp : 0<M := lt_of_le_of_ne hM (Ne.symm hzero)
    let q : ℂ := M⁻¹ • spatial z
    let a : ℝ := (M+z 0)/2
    let b : ℝ := (M-z 0)/2
    have ht : |z 0|≤M := le_max_left _ _
    have ha : 0≤a := by dsimp [a]; linarith [neg_abs_le (z 0)]
    have hb : 0≤b := by dsimp [b]; linarith [le_abs_self (z 0)]
    have hab : a+b=M := by dsimp [a,b]; ring
    have hd : a-b=z 0 := by dsimp [a,b]; ring
    have hq : ‖q‖≤1 := by
      change ‖(M⁻¹ : ℝ) • spatial z‖≤1
      rw [norm_smul,Real.norm_eq_abs,abs_of_nonneg (inv_nonneg.mpr hM)]
      have hs : ‖spatial z‖≤M := le_max_right _ _
      exact (inv_mul_le_iff₀ hMp).mpr (by simpa using hs)
    refine ⟨point a (a • q),point_ray_mem ha hq,point b (b • -q),point_ray_mem hb (by simpa using hq),?_,?_⟩
    · have hsp : a • q-b • -q=spatial z := by
        rw [smul_neg,sub_neg_eq_add,← add_smul,hab]
        change (M:ℝ) • ((M⁻¹:ℝ) • spatial z)=spatial z
        rw [smul_smul,mul_inv_cancel₀ hzero,one_smul]
      have he : point a (a • q)-point b (b • -q)=point (z 0) (spatial z) := by
        funext i
        fin_cases i
        · simpa [point] using hd
        · simpa [point,Complex.sub_re] using congrArg Complex.re hsp
        · simpa [point,Complex.sub_im] using congrArg Complex.im hsp
      exact (he.trans (point_mass_spatial z)).symm
    · simpa only [point_zero] using hab

/-- The base norm is the cylinder norm claimed in P47, derived from the actual infimum. -/
theorem value_eq (z : State) : coneInstance.value z=max |z 0| ‖spatial z‖ := by
  apply le_antisymm
  · obtain ⟨u,hu,v,hv,hz,hcost⟩ := exists_minimal_decomposition z
    exact (coneInstance.value_le_cost hu hv hz).trans_eq hcost
  · apply coneInstance.le_value
    exact fun _ hu _ hv hz => max_le_cost hu hv hz

theorem value_eq_sqrt (z : State) :
    coneInstance.value z=max |z 0| (Real.sqrt (z 1^2+z 2^2)) := by
  rw [value_eq,spatial_norm]

end Komorebi.LSM.LorentzBaseNorm
