import KomorebiLSM.BaseNormTopology
import KomorebiLSM.MatrixOrderUnit
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Tactic

/-! The actual positive-definite metric gives an invertible Lorentz transport. -/
set_option autoImplicit false
namespace Komorebi.LSM.OrientedEllipsoid
open scoped BigOperators Matrix MatrixOrder Matrix.Norms.L2Operator

abbrev State (D : Type*) := (Unit ⊕ D) → ℝ
variable {D : Type*}

def mass : State D →ₗ[ℝ] ℝ := LinearMap.proj (Sum.inl ())

def spatial : State D →ₗ[ℝ] (D → ℝ) where
  toFun z i := z (Sum.inr i)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

def point (m : ℝ) (x : D → ℝ) : State D := Sum.elim (fun _ => m) x

@[simp] theorem mass_point (m : ℝ) (x : D → ℝ) : mass (point m x) = m := rfl
@[simp] theorem spatial_point (m : ℝ) (x : D → ℝ) : spatial (point m x) = x := rfl
@[simp] theorem point_mass_spatial (z : State D) : point (mass z) (spatial z) = z := by
  ext i
  rcases i with i | i
  · cases i; rfl
  · rfl

def centered (c : D → ℝ) : State D →ₗ[ℝ] (D → ℝ) := spatial - mass.smulRight c

@[simp] theorem centered_apply (c : D → ℝ) (z : State D) :
    centered c z = spatial z - mass z • c := rfl

variable [Fintype D] [DecidableEq D]

def cone (c : D → ℝ) (H : Matrix D D ℝ) : Set (State D) :=
  {z | 0 ≤ mass z ∧ centered c z ⬝ᵥ (H *ᵥ centered c z) ≤ (mass z)^2}

/-- A positive definite real metric has an actual invertible square factor. -/
theorem exists_factor (H : Matrix D D ℝ) (hH : H.PosDef) :
    ∃ L : Matrix D D ℝ, IsUnit L ∧ L.transpose * L = H := by
  classical
  rcases isEmpty_or_nonempty D with hD | hD
  · let := hD
    exact ⟨1,isUnit_one,Subsingleton.elim _ _⟩
  · let := hD
    have hroot : (CFC.sqrt H).PosSemidef := Matrix.nonneg_iff_posSemidef.mp (CFC.sqrt_nonneg H)
    have hsquare : CFC.sqrt H * CFC.sqrt H = H := by
      simpa only [pow_two] using CFC.sq_sqrt H hH.posSemidef.nonneg
    have hi : IsUnit (CFC.sqrt H) := isUnit_of_mul_isUnit_left (hsquare ▸ hH.isUnit)
    refine ⟨CFC.sqrt H,hi,?_⟩
    have ht : (CFC.sqrt H).transpose = CFC.sqrt H := by
      simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using hroot.isHermitian.eq
    rw [ht,hsquare]

noncomputable def factor (H : Matrix D D ℝ) (hH : H.PosDef) : Matrix D D ℝ :=
  (exists_factor H hH).choose

theorem factor_isUnit (H : Matrix D D ℝ) (hH : H.PosDef) : IsUnit (factor H hH) :=
  (exists_factor H hH).choose_spec.1

theorem factor_square (H : Matrix D D ℝ) (hH : H.PosDef) :
    (factor H hH).transpose * factor H hH = H := (exists_factor H hH).choose_spec.2

/-- The metric factor is an actual linear isomorphism to Euclidean spatial coordinates. -/
noncomputable def factorEquiv (H : Matrix D D ℝ) (hH : H.PosDef) :
    (D → ℝ) ≃ₗ[ℝ] EuclideanSpace ℝ D := by
  classical
  exact (LinearEquiv.ofBijective (factor H hH).mulVecLin
    ⟨Matrix.mulVec_injective_iff_isUnit.mpr (factor_isUnit H hH),
      Matrix.mulVec_surjective_iff_isUnit.mpr (factor_isUnit H hH)⟩).trans
        (WithLp.linearEquiv 2 ℝ (D → ℝ)).symm

theorem factorEquiv_norm_sq (H : Matrix D D ℝ) (hH : H.PosDef) (x : D → ℝ) :
    ‖factorEquiv H hH x‖^2 = x ⬝ᵥ (H *ᵥ x) := by
  classical
  rw [PiLp.norm_sq_eq_of_L2]
  change (∑ i, ‖((factor H hH) *ᵥ x) i‖^2) = _
  simp only [Real.norm_eq_abs,sq_abs]
  calc
    _ = ((factor H hH) *ᵥ x) ⬝ᵥ ((factor H hH) *ᵥ x) := by simp [dotProduct,pow_two]
    _ = x ⬝ᵥ ((factor H hH).transpose *ᵥ ((factor H hH) *ᵥ x)) :=
      (Matrix.dotProduct_transpose_mulVec _ _ _).symm
    _ = x ⬝ᵥ (((factor H hH).transpose * factor H hH) *ᵥ x) := by rw [Matrix.mulVec_mulVec]
    _ = _ := by rw [factor_square]

/-- The standard forward Lorentz sheet for any real normed spatial space. -/
def lorentz {V : Type*} [NormedAddCommGroup V] : Set (ℝ × V) := {z | ‖z.2‖ ≤ z.1}

section Lorentz
variable {V : Type*} [NormedAddCommGroup V] [NormedSpace ℝ V]

noncomputable def lorentzProbabilityCone : BaseNorm.ProbabilityCone (ℝ × V) where
  carrier := lorentz
  zero_mem := by simp [lorentz]
  add_mem := by
    intro x y hx hy
    exact (norm_add_le x.2 y.2).trans (add_le_add hx hy)
  smul_mem := by
    intro a ha x hx
    change ‖a • x.2‖ ≤ a * x.1
    rw [norm_smul,Real.norm_eq_abs,abs_of_nonneg ha]
    exact mul_le_mul_of_nonneg_left hx ha
  spans := by
    apply top_unique
    intro x _
    let a : ℝ := |x.1| + ‖x.2‖
    have hu : (a + x.1,x.2) ∈ lorentz := by
      change ‖x.2‖ ≤ |x.1| + ‖x.2‖ + x.1
      linarith [neg_abs_le x.1]
    have hv : (a,(0 : V)) ∈ lorentz := by
      change ‖(0 : V)‖ ≤ |x.1| + ‖x.2‖
      simpa using add_nonneg (abs_nonneg x.1) (norm_nonneg x.2)
    have he : x = (a + x.1,x.2) - (a,(0 : V)) := by ext <;> simp
    rw [he]
    exact Submodule.sub_mem _ (Submodule.subset_span hu) (Submodule.subset_span hv)
  mass := LinearMap.fst ℝ ℝ V
  mass_pos := by
    intro x hx hn
    change 0 < x.1
    have hnon : 0 ≤ x.1 := (norm_nonneg x.2).trans hx
    apply lt_of_le_of_ne hnon
    intro he
    have hs : x.2 = 0 := norm_eq_zero.mp (le_antisymm (he ▸ hx) (norm_nonneg x.2))
    exact hn (Prod.ext he.symm hs)
  closed := isClosed_le (continuous_snd.norm) continuous_fst
end Lorentz

variable (c : D → ℝ) (H : Matrix D D ℝ) (hH : H.PosDef)

/-- This literal invertible linear change is the mass-preserving Lorentz transport. -/
noncomputable def lorentzTransport : State D ≃ₗ[ℝ] (ℝ × EuclideanSpace ℝ D) where
  toFun z := (mass z,factorEquiv H hH (centered c z))
  invFun p := point p.1 ((factorEquiv H hH).symm p.2 + p.1 • c)
  left_inv z := by
    change point (mass z) ((factorEquiv H hH).symm
      (factorEquiv H hH (spatial z - mass z • c)) + mass z • c) = z
    simp
  right_inv p := by
    apply Prod.ext
    · rfl
    · change factorEquiv H hH (((factorEquiv H hH).symm p.2 + p.1 • c)-p.1 • c) = p.2
      simp
  map_add' x y := by simp only [map_add,Prod.mk_add_mk]
  map_smul' a x := by simp only [map_smul,Prod.smul_mk,RingHom.id_apply]

@[simp] theorem lorentzTransport_mass (z : State D) :
    (lorentzTransport c H hH z).1 = mass z := rfl

/-- The quadratic ellipsoid cone is exactly the inverse image of one Lorentz sheet. -/
theorem cone_iff_lorentz (z : State D) :
    z ∈ cone c H ↔ lorentzTransport c H hH z ∈ lorentz := by
  change (0 ≤ mass z ∧ centered c z ⬝ᵥ (H *ᵥ centered c z) ≤ (mass z)^2) ↔
    ‖factorEquiv H hH (centered c z)‖ ≤ mass z
  rw [← factorEquiv_norm_sq H hH]
  constructor
  · rintro ⟨hm,hq⟩
    nlinarith [norm_nonneg (factorEquiv H hH (centered c z))]
  · intro hn
    constructor
    · exact (norm_nonneg (factorEquiv H hH (centered c z))).trans hn
    · exact pow_le_pow_left₀ (norm_nonneg _) hn 2

/-- Pulling back the standard Lorentz cone gives all actual ellipsoid cone axioms. -/
noncomputable def probabilityCone : BaseNorm.ProbabilityCone (State D) where
  carrier := cone c H
  zero_mem := (cone_iff_lorentz c H hH 0).mpr (by simp [lorentzTransport,lorentz])
  add_mem := by
    intro x y hx hy
    apply (cone_iff_lorentz c H hH _).mpr
    rw [map_add]
    exact lorentzProbabilityCone.add_mem ((cone_iff_lorentz c H hH x).mp hx)
      ((cone_iff_lorentz c H hH y).mp hy)
  smul_mem := by
    intro a ha x hx
    apply (cone_iff_lorentz c H hH _).mpr
    rw [map_smul]
    exact lorentzProbabilityCone.smul_mem ha ((cone_iff_lorentz c H hH x).mp hx)
  spans := by
    apply top_unique
    intro z _
    obtain ⟨u,hu,v,hv,he⟩ := (lorentzProbabilityCone (V := EuclideanSpace ℝ D)).exists_decomposition
      (lorentzTransport c H hH z)
    change u ∈ lorentz at hu
    change v ∈ lorentz at hv
    have hu' : (lorentzTransport c H hH).symm u ∈ cone c H :=
      (cone_iff_lorentz c H hH _).mpr (by simpa only [LinearEquiv.apply_symm_apply] using hu)
    have hv' : (lorentzTransport c H hH).symm v ∈ cone c H :=
      (cone_iff_lorentz c H hH _).mpr (by simpa only [LinearEquiv.apply_symm_apply] using hv)
    have hz : z = (lorentzTransport c H hH).symm u - (lorentzTransport c H hH).symm v := by
      exact ((lorentzTransport c H hH).symm_apply_apply z).symm.trans
        ((congrArg (lorentzTransport c H hH).symm he).trans
          (map_sub (lorentzTransport c H hH).symm u v))
    rw [hz]
    exact Submodule.sub_mem _ (Submodule.subset_span hu') (Submodule.subset_span hv')
  mass := mass
  mass_pos := by
    intro z hz hn
    have ht : lorentzTransport c H hH z ≠ 0 := by
      intro he
      exact hn ((lorentzTransport c H hH).injective (by simpa using he))
    exact lorentzProbabilityCone.mass_pos ((cone_iff_lorentz c H hH z).mp hz) ht
  closed := by
    have he : cone c H = (lorentzTransport c H hH) ⁻¹' lorentz :=
      Set.ext (cone_iff_lorentz c H hH)
    rw [he]
    exact lorentzProbabilityCone.closed.preimage
      (lorentzTransport c H hH).toLinearMap.continuous_of_finiteDimensional

@[simp] theorem probabilityCone_carrier : (probabilityCone c H hH).carrier = cone c H := rfl
@[simp] theorem probabilityCone_mass : (probabilityCone c H hH).mass = mass := rfl

theorem cone_mass_pos (hH : H.PosDef) {z : State D} (hz : z∈cone c H) (hne : z≠0) : 0<mass z :=
  (probabilityCone c H hH).mass_pos hz hne

end Komorebi.LSM.OrientedEllipsoid
