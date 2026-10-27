import Mathlib.Analysis.Matrix.PosDef
import Mathlib.Algebra.Order.Star.Real
import Mathlib.Data.Matrix.Block
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic

/-! P63: operator-only affine centers and normalized invariant ellipsoid
proposals. The dimension-one invariant-form hypothesis is a genuine finrank
statement about the symmetric fixed-point subspace. It is used to derive
uniqueness, rather than assuming the desired normalized metric. -/
set_option autoImplicit false
namespace Komorebi.LSM.EllipsoidDiscovery
open Matrix
open scoped BigOperators

variable {D : Type*} [Fintype D]

/-- The actual linear space of real symmetric forms fixed by congruence. -/
def invariantForms (A : Matrix D D ℝ) : Submodule ℝ (Matrix D D ℝ) where
  carrier := {H | H.IsHermitian ∧ A.transpose * H * A=H}
  zero_mem' := ⟨Matrix.isHermitian_zero,by simp⟩
  add_mem' := by
    rintro H K ⟨hH,hA⟩ ⟨hK,hB⟩
    exact ⟨hH.add hK,by simp only [Matrix.mul_add,Matrix.add_mul,hA,hB]⟩
  smul_mem' := by
    intro a H hH
    refine ⟨hH.1.smul (by simp [IsSelfAdjoint]),?_⟩
    simp only [Matrix.mul_smul,Matrix.smul_mul,hH.2]

@[simp] theorem mem_invariantForms (A H : Matrix D D ℝ) :
    H∈invariantForms A ↔ H.IsHermitian ∧ A.transpose * H * A=H := Iff.rfl

/-- Real quadratic evaluation, with no positivity assumed in the definition. -/
def quadratic (H : Matrix D D ℝ) (x : D → ℝ) : ℝ := x ⬝ᵥ (H *ᵥ x)

theorem quadratic_smul (a : ℝ) (H : Matrix D D ℝ) (x : D → ℝ) :
    quadratic (a • H) x=a * quadratic H x := by
  simp [quadratic,Matrix.smul_mulVec,dotProduct_smul]

theorem quadratic_pos {H : Matrix D D ℝ} (hH : H.PosDef)
    {x : D → ℝ} (hx : x≠0) : 0<quadratic H x := by
  simpa only [quadratic,Pi.star_apply,star_trivial] using hH.dotProduct_mulVec_pos hx

/-- One-dimensionality makes every actual symmetric invariant form a multiple
of any specified nonzero member of that subspace. -/
theorem invariant_scalar (A H₀ : Matrix D D ℝ)
    (hdim : Module.finrank ℝ (invariantForms A)=1)
    (hH₀ : H₀∈invariantForms A) (hne : H₀≠0)
    (H : Matrix D D ℝ) (hH : H∈invariantForms A) : ∃ a : ℝ,H=a • H₀ := by
  have hn : (⟨H₀,hH₀⟩ : invariantForms A)≠0 := by
    intro h
    exact hne (congrArg Subtype.val h)
  obtain ⟨a,ha⟩ := exists_smul_eq_of_finrank_eq_one hdim hn (⟨H,hH⟩ : invariantForms A)
  exact ⟨a,(congrArg Subtype.val ha).symm⟩

/-- Normalize the form so the nonzero anchor displacement has squared length one. -/
noncomputable def normalizedMetric (H₀ : Matrix D D ℝ) (δ : D → ℝ) : Matrix D D ℝ :=
  (quadratic H₀ δ)⁻¹ • H₀

theorem normalizedMetric_posDef {H₀ : Matrix D D ℝ} (hH₀ : H₀.PosDef)
    {δ : D → ℝ} (hδ : δ≠0) : (normalizedMetric H₀ δ).PosDef :=
  hH₀.smul (inv_pos.mpr (quadratic_pos hH₀ hδ))

theorem normalizedMetric_invariant (A H₀ : Matrix D D ℝ)
    (hH₀ : H₀∈invariantForms A) (δ : D → ℝ) : normalizedMetric H₀ δ∈invariantForms A :=
  (invariantForms A).smul_mem _ hH₀

theorem normalizedMetric_boundary {H₀ : Matrix D D ℝ} (hH₀ : H₀.PosDef)
    {δ : D → ℝ} (hδ : δ≠0) : quadratic (normalizedMetric H₀ δ) δ=1 := by
  rw [normalizedMetric,quadratic_smul]
  exact inv_mul_cancel₀ (quadratic_pos hH₀ hδ).ne'

/-- The unique normalized member is derived from actual subspace dimension.
Positivity of a competing form is not needed for this stronger uniqueness. -/
theorem normalizedMetric_unique (A H₀ : Matrix D D ℝ)
    (hdim : Module.finrank ℝ (invariantForms A)=1)
    (hH₀ : H₀∈invariantForms A) (hp : H₀.PosDef)
    {δ : D → ℝ} (hδ : δ≠0) (H : Matrix D D ℝ)
    (hH : H∈invariantForms A) (hb : quadratic H δ=1) : H=normalizedMetric H₀ δ := by
  have hq := quadratic_pos hp hδ
  have hn : H₀≠0 := by
    intro h
    subst H₀
    simp [quadratic] at hq
  obtain ⟨a,rfl⟩ := invariant_scalar A H₀ hdim hH₀ hn H hH
  rw [quadratic_smul] at hb
  have ha : a=(quadratic H₀ δ)⁻¹ := by
    have h := congrArg (fun r : ℝ => r * (quadratic H₀ δ)⁻¹) hb
    simpa only [mul_assoc,mul_inv_cancel₀ hq.ne',mul_one,one_mul] using h
  rw [ha]
  rfl

theorem unique_positive_boundary_metric (A H₀ : Matrix D D ℝ)
    (hdim : Module.finrank ℝ (invariantForms A)=1)
    (hH₀ : H₀∈invariantForms A) (hp : H₀.PosDef)
    {δ : D → ℝ} (hδ : δ≠0) :
    ∃! H : Matrix D D ℝ,H∈invariantForms A ∧ H.PosDef ∧ quadratic H δ=1 := by
  refine ⟨normalizedMetric H₀ δ,
    ⟨normalizedMetric_invariant A H₀ hH₀ δ,normalizedMetric_posDef hp hδ,
      normalizedMetric_boundary hp hδ⟩,?_⟩
  intro H hH
  exact normalizedMetric_unique A H₀ hdim hH₀ hp hδ H hH.1 hH.2.2

/-- The metric is independent of which positive invariant reference form was
chosen, hence in particular of its arbitrary positive scale. -/
theorem positive_reference_independent (A H₀ H₁ : Matrix D D ℝ)
    (hdim : Module.finrank ℝ (invariantForms A)=1)
    (hH₀ : H₀∈invariantForms A) (hp₀ : H₀.PosDef)
    (hH₁ : H₁∈invariantForms A) (hp₁ : H₁.PosDef)
    {δ : D → ℝ} (hδ : δ≠0) : normalizedMetric H₁ δ=normalizedMetric H₀ δ :=
  normalizedMetric_unique A H₀ hdim hH₀ hp₀ hδ _
    (normalizedMetric_invariant A H₁ hH₁ δ) (normalizedMetric_boundary hp₁ hδ)

theorem positive_scale_independent (a : ℝ) (ha : 0<a)
    {H₀ : Matrix D D ℝ} (hp : H₀.PosDef) {δ : D → ℝ} (hδ : δ≠0) :
    normalizedMetric (a • H₀) δ=normalizedMetric H₀ δ := by
  have hq := quadratic_pos hp hδ
  unfold normalizedMetric
  rw [quadratic_smul,smul_smul]
  congr 1
  field_simp

section Affine
variable [DecidableEq D]

abbrev State (D : Type*) := (Unit ⊕ D) → ℝ

def mass : State D →ₗ[ℝ] ℝ := LinearMap.proj (Sum.inl ())
def spatial (z : State D) : D → ℝ := fun i => z (Sum.inr i)
def point (m : ℝ) (x : D → ℝ) : State D := Sum.elim (fun _ => m) x

omit [Fintype D] [DecidableEq D] in
@[simp] theorem mass_point (m : ℝ) (x : D → ℝ) : mass (point m x)=m := rfl
omit [Fintype D] [DecidableEq D] in
@[simp] theorem spatial_point (m : ℝ) (x : D → ℝ) : spatial (point m x)=x := rfl

omit [Fintype D] [DecidableEq D] in
theorem point_eta (z : State D) : point (mass z) (spatial z)=z := by
  funext i
  cases i with
  | inl u => cases u; rfl
  | inr i => rfl

/-- The affine mass-first block matrix. -/
noncomputable def affineMatrix (b : D → ℝ) (A : Matrix D D ℝ) :
    Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ :=
  Matrix.fromBlocks 1 0 (fun i _ => b i) A

def translation (F : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) : D → ℝ :=
  fun i => F (Sum.inr i) (Sum.inl ())

def spatialBlock (F : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) : Matrix D D ℝ :=
  fun i j => F (Sum.inr i) (Sum.inr j)

/-- The actual mass-row identity forces the top blocks 1 and 0. -/
theorem mass_first_block (F : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (hm : mass.comp F.mulVecLin=mass) : F=affineMatrix (translation F) (spatialBlock F) := by
  have hrow (j : Unit ⊕ D) : F (Sum.inl ()) j=(Pi.single j (1 : ℝ) : State D) (Sum.inl ()) := by
    have he := congrArg (fun L : State D →ₗ[ℝ] ℝ => L (Pi.single j 1)) hm
    simpa only [LinearMap.comp_apply,Matrix.mulVecLin_apply,Matrix.mulVec_single_one,
      mass,LinearMap.proj_apply,Matrix.col_apply] using he
  funext i j
  cases i with
  | inl u =>
    cases u
    cases j with
    | inl u => cases u; simpa [affineMatrix,Matrix.fromBlocks,Matrix.one_apply] using hrow (Sum.inl ())
    | inr j => simpa [affineMatrix,Matrix.fromBlocks,Matrix.one_apply] using hrow (Sum.inr j)
  | inr i =>
    cases j with
    | inl u => cases u; rfl
    | inr j => rfl

omit [DecidableEq D] in
theorem affineMatrix_apply (b : D → ℝ) (A : Matrix D D ℝ) (z : State D) :
    affineMatrix b A *ᵥ z=point (mass z) (mass z • b+A *ᵥ spatial z) := by
  funext i
  cases i with
  | inl u => cases u; simp [affineMatrix,Matrix.fromBlocks,point,mass,Matrix.mulVec,dotProduct,Fintype.sum_sum_type]
  | inr i => simp [affineMatrix,Matrix.fromBlocks,point,mass,spatial,Matrix.mulVec,dotProduct,Fintype.sum_sum_type,mul_comm]

/-- The fitted ratio is literal matrix multiplication by the actual inverse. -/
noncomputable def ratio (Bₐ Bᵦ : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) := Bᵦ * Bₐ⁻¹

theorem ratio_reconstructs (Bₐ Bᵦ : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (hi : IsUnit Bₐ.det) : ratio Bₐ Bᵦ * Bₐ=Bᵦ := by
  rw [ratio,Matrix.mul_assoc,Matrix.nonsing_inv_mul _ hi,Matrix.mul_one]

theorem ratio_isUnit (Bₐ Bᵦ : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (hₐ : IsUnit Bₐ.det) (hᵦ : IsUnit Bᵦ.det) : IsUnit (ratio Bₐ Bᵦ) := by
  apply (Matrix.isUnit_iff_isUnit_det _).mpr
  rw [ratio,Matrix.det_mul]
  exact hᵦ.mul (Bₐ.isUnit_nonsing_inv_det hₐ)

/-- The proposed center is derived from the actual inverse of I-A. -/
noncomputable def fixedCenter (A : Matrix D D ℝ) (b : D → ℝ) : D → ℝ :=
  (1-A)⁻¹ *ᵥ b

theorem fixedCenter_equation (A : Matrix D D ℝ) (b : D → ℝ)
    (hi : IsUnit (1-A).det) : fixedCenter A b=b+A *ᵥ fixedCenter A b := by
  have he : (1-A) *ᵥ fixedCenter A b=b := by
    rw [fixedCenter,Matrix.mulVec_mulVec,Matrix.mul_nonsing_inv _ hi,Matrix.one_mulVec]
  rw [Matrix.sub_mulVec,Matrix.one_mulVec] at he
  exact sub_eq_iff_eq_add.mp he

theorem fixedCenter_unique (A : Matrix D D ℝ) (b : D → ℝ)
    (hi : IsUnit (1-A).det) (x : D → ℝ) (hx : x=b+A *ᵥ x) : x=fixedCenter A b := by
  have he : (1-A) *ᵥ x=b := by
    rw [Matrix.sub_mulVec,Matrix.one_mulVec]
    exact sub_eq_iff_eq_add.mpr hx
  calc
    x=(1-A)⁻¹ *ᵥ ((1-A) *ᵥ x) := by
      rw [Matrix.mulVec_mulVec,Matrix.nonsing_inv_mul _ hi,Matrix.one_mulVec]
    _=fixedCenter A b := by rw [he]; rfl

theorem unique_fixedCenter (A : Matrix D D ℝ) (b : D → ℝ)
    (hi : IsUnit (1-A).det) : ∃! x : D → ℝ,x=b+A *ᵥ x :=
  ⟨fixedCenter A b,fixedCenter_equation A b hi,fun x hx => fixedCenter_unique A b hi x hx⟩

/-- Centering the normalized affine action leaves precisely the fitted spatial
matrix A; the ratio need not itself be an available action or a positive map. -/
theorem centered_action (A : Matrix D D ℝ) (b : D → ℝ)
    (hi : IsUnit (1-A).det) (w : D → ℝ) :
    b+A *ᵥ (fixedCenter A b+w)=fixedCenter A b+A *ᵥ w := by
  rw [Matrix.mulVec_add,← add_assoc,← fixedCenter_equation A b hi]

theorem centered_affineMatrix (A : Matrix D D ℝ) (b : D → ℝ)
    (hi : IsUnit (1-A).det) (w : D → ℝ) :
    affineMatrix b A *ᵥ point 1 (fixedCenter A b+w)=
      point 1 (fixedCenter A b+A *ᵥ w) := by
  rw [affineMatrix_apply,mass_point,spatial_point,one_smul,centered_action A b hi]

omit [DecidableEq D] in
theorem affine_fixed_point_iff (A : Matrix D D ℝ) (b x : D → ℝ) :
    affineMatrix b A *ᵥ point 1 x=point 1 x ↔ x=b+A *ᵥ x := by
  rw [affineMatrix_apply,mass_point,spatial_point,one_smul]
  constructor
  · intro h
    exact (congrArg spatial h).symm
  · intro h
    exact congrArg (point 1) h.symm

theorem ratio_fixed_center (Bₐ Bᵦ : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (hm : mass.comp (ratio Bₐ Bᵦ).mulVecLin=mass)
    (hi : IsUnit (1-spatialBlock (ratio Bₐ Bᵦ)).det) :
    ∃! x : D → ℝ,ratio Bₐ Bᵦ *ᵥ point 1 x=point 1 x := by
  rw [mass_first_block _ hm]
  simp_rw [affine_fixed_point_iff]
  exact unique_fixedCenter _ _ hi

end Affine

section RankOneAnchor

/-- Normalize a literal branch image by its actual mass row. This is only a
proposal anchor; no probability-domain validity is presumed. -/
noncomputable def normalizedImage (L : State D →ₗ[ℝ] State D) (z : State D) : State D :=
  (mass (L z))⁻¹ • L z

omit [Fintype D] in
theorem normalizedImage_mass (L : State D →ₗ[ℝ] State D) (z : State D)
    (hm : mass (L z)≠0) : mass (normalizedImage L z)=1 := by
  rw [normalizedImage,map_smul,smul_eq_mul]
  exact inv_mul_cancel₀ hm

omit [Fintype D] in
theorem normalizedImage_point (L : State D →ₗ[ℝ] State D) (z : State D)
    (hm : mass (L z)≠0) : normalizedImage L z=point 1 (spatial (normalizedImage L z)) := by
  rw [← normalizedImage_mass L z hm]
  exact (point_eta _).symm

omit [Fintype D] in
theorem normalizedImage_mem_range (L : State D →ₗ[ℝ] State D) (z : State D) :
    normalizedImage L z∈L.range := by
  refine ⟨(mass (L z))⁻¹ • z,?_⟩
  exact L.map_smul _ z

omit [Fintype D] in
/-- A true rank-one range gives the same mass-normalized anchor from every
nonzero-mass image. Rank one is not merely asserted of a chosen output vector. -/
theorem rank_one_normalized_image (L : State D →ₗ[ℝ] State D)
    (hr : Module.finrank ℝ L.range=1) (z w : State D)
    (hz : mass (L z)≠0) (hw : mass (L w)≠0) : normalizedImage L w=normalizedImage L z := by
  have hn : (⟨L z,⟨z,rfl⟩⟩ : L.range)≠0 := by
    intro h
    have hv : L z=0 := congrArg Subtype.val h
    exact hz (by rw [hv,map_zero])
  obtain ⟨a,ha⟩ := exists_smul_eq_of_finrank_eq_one hr hn (⟨L w,⟨w,rfl⟩⟩ : L.range)
  have hv : a • L z=L w := congrArg Subtype.val ha
  have ha0 : a≠0 := by
    intro h
    have hmass := congrArg mass hv
    rw [h,zero_smul,map_zero] at hmass
    exact hw hmass.symm
  unfold normalizedImage
  rw [← hv,map_smul,smul_eq_mul,smul_smul]
  congr 1
  field_simp

/-- The rank-one anchor is mass-normalized, and a noncentral image specifies
exactly one positive invariant form with that chosen boundary placement. -/
theorem rank_one_boundary_proposal (A H₀ : Matrix D D ℝ)
    (hdim : Module.finrank ℝ (invariantForms A)=1)
    (hH₀ : H₀∈invariantForms A) (hp : H₀.PosDef)
    (L : State D →ₗ[ℝ] State D) (hr : Module.finrank ℝ L.range=1)
    (z : State D) (hz : mass (L z)≠0) (c : D → ℝ)
    (hδ : spatial (normalizedImage L z)≠c) :
    normalizedImage L z=point 1 (spatial (normalizedImage L z)) ∧
    (∀ w : State D,mass (L w)≠0 → normalizedImage L w=normalizedImage L z) ∧
    ∃! H : Matrix D D ℝ,H∈invariantForms A ∧ H.PosDef ∧
      quadratic H (spatial (normalizedImage L z)-c)=1 := by
  refine ⟨normalizedImage_point L z hz,fun w hw => rank_one_normalized_image L hr z w hz hw,?_⟩
  exact unique_positive_boundary_metric A H₀ hdim hH₀ hp (sub_ne_zero.mpr hδ)

end RankOneAnchor

section OperatorProposal
variable [DecidableEq D]

/-- The complete operator-only algebraic proposal: literal invertible ratio,
mass-forced affine blocks, unique center, rank-one normalized image, and the
unique positive invariant metric placing that chosen image on the boundary.
This theorem deliberately has no full-family probability conclusion. -/
theorem operator_only_proposal
    (Bₐ Bᵦ : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (hₐ : IsUnit Bₐ.det) (hᵦ : IsUnit Bᵦ.det)
    (hm : mass.comp (ratio Bₐ Bᵦ).mulVecLin=mass)
    (hi : IsUnit (1-spatialBlock (ratio Bₐ Bᵦ)).det)
    (H₀ : Matrix D D ℝ)
    (hdim : Module.finrank ℝ (invariantForms (spatialBlock (ratio Bₐ Bᵦ)))=1)
    (hH₀ : H₀∈invariantForms (spatialBlock (ratio Bₐ Bᵦ))) (hp : H₀.PosDef)
    (L : State D →ₗ[ℝ] State D) (hr : Module.finrank ℝ L.range=1)
    (z : State D) (hz : mass (L z)≠0)
    (hδ : spatial (normalizedImage L z)≠
      fixedCenter (spatialBlock (ratio Bₐ Bᵦ)) (translation (ratio Bₐ Bᵦ))) :
    let F := ratio Bₐ Bᵦ
    let c := fixedCenter (spatialBlock F) (translation F)
    let δ := spatial (normalizedImage L z)-c
    let H := normalizedMetric H₀ δ
    IsUnit F ∧ F=affineMatrix (translation F) (spatialBlock F) ∧
    (∃! x : D → ℝ,F *ᵥ point 1 x=point 1 x) ∧
    (∀ w : D → ℝ,F *ᵥ point 1 (c+w)=point 1 (c+spatialBlock F *ᵥ w)) ∧
    normalizedImage L z=point 1 (spatial (normalizedImage L z)) ∧
    (∀ w : State D,mass (L w)≠0 → normalizedImage L w=normalizedImage L z) ∧
    H∈invariantForms (spatialBlock F) ∧ H.PosDef ∧ quadratic H δ=1 ∧
    (∀ K : Matrix D D ℝ,K∈invariantForms (spatialBlock F) → quadratic K δ=1 → K=H) := by
  dsimp only
  have hn := sub_ne_zero.mpr hδ
  refine ⟨ratio_isUnit Bₐ Bᵦ hₐ hᵦ,mass_first_block _ hm,
    ratio_fixed_center Bₐ Bᵦ hm hi,?_,normalizedImage_point L z hz,
    fun w hw => rank_one_normalized_image L hr z w hz hw,
    normalizedMetric_invariant _ H₀ hH₀ _,normalizedMetric_posDef hp hn,
    normalizedMetric_boundary hp hn,?_⟩
  · intro w
    rw [mass_first_block _ hm]
    exact centered_affineMatrix _ _ hi w
  · intro K hK hboundary
    exact normalizedMetric_unique _ H₀ hdim hH₀ hp hn K hK hboundary

end OperatorProposal

end Komorebi.LSM.EllipsoidDiscovery
