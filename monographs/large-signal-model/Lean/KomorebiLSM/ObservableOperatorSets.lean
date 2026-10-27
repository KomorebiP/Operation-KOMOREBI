import KomorebiLSM.ObservableMomentAlgebra
import KomorebiLSM.ObservableMomentProcess

/-! Known linear moment inversion defines actual coefficient confidence sets.
Exact integrated mass is imposed only by its literal affine constraints. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservableMoments
open MeasureTheory Matrix FiniteMomentIdentification
open scoped BigOperators Matrix

section Matrices
variable {p r : ℕ}

noncomputable def operatorMatrix (L : (Fin r → ℝ) →L[ℝ] (Fin r → ℝ)) :
    Matrix (Fin r) (Fin r) ℝ := LinearMap.toMatrix' L.toLinearMap

@[simp] theorem operatorMatrix_mulVec (L : (Fin r → ℝ) →L[ℝ] (Fin r → ℝ)) (z : Fin r → ℝ) :
    operatorMatrix L *ᵥ z=L z := LinearMap.toMatrix'_mulVec _ _

theorem operatorMatrix_sum (B : Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ)) (w : Fin p → ℝ) :
    operatorMatrix (∑ k,w k • B k)=∑ k,w k • operatorMatrix (B k) := by
  unfold operatorMatrix
  simp only [ContinuousLinearMap.toLinearMap_sum,ContinuousLinearMap.toLinearMap_smul,map_sum,map_smul]

end Matrices

section ActualCoefficients
variable {A Y : Type*} {p r : ℕ} [MeasurableSpace Y]
variable {C : BaseNorm.ProbabilityCone (Fin r → ℝ)} {ν : Measure Y}
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν)

/-- The actual coefficient matrices of the submitted operator density. -/
noncomputable def coefficientMatrices
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ)) :
    A → Fin p → Matrix (Fin r) (Fin r) ℝ := fun a k => operatorMatrix (B a k)

/-- Actual observation-basis integration commutes with the fixed coordinate
matrix representation used by the row regressions. -/
theorem matrix_moment_mixing (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ))
    (g ψ : Fin p → Y → ℝ) (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν) (a : A) :
    (fun j => momentMatrix D (g j) a)=
      mix (basisMomentMatrix (ν := ν) g ψ) (coefficientMatrices B a) := by
  funext j
  change operatorMatrix (momentOperator D (g j) a)=_
  rw [congrFun (momentOperator_mixing D B g ψ hB hgψ a) j]
  exact operatorMatrix_sum _ _

/-- Literal true coefficients, rather than arbitrary target matrices, are
reconstructed from the actual instrument moment matrices. -/
theorem matrix_coefficient_reconstruction
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ))
    (g ψ : Fin p → Y → ℝ) (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν)
    (hW : IsUnit (basisMomentMatrix (ν := ν) g ψ)) (a : A) :
    coefficientMatrices B a=
      mix (basisMomentMatrix (ν := ν) g ψ)⁻¹ (fun j => momentMatrix D (g j) a) := by
  rw [matrix_moment_mixing D B g ψ hB hgψ a,inverse_mix _ hW]

noncomputable def basisIntegral (ψ : Fin p → Y → ℝ) (k : Fin p) : ℝ := ∫ y,ψ k y∂ν

theorem integratedOperator_expansion
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ)) (ψ : Fin p → Y → ℝ)
    (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hψ : ∀ k,Integrable (ψ k) ν) (a : A) :
    (∫ y,D.op a y∂ν)=∑ k,basisIntegral (ν := ν) ψ k • B a k := by
  simp_rw [hB]
  rw [integral_finsetSum _ (fun k _ => (hψ k).smul_const (B a k))]
  apply Finset.sum_congr rfl
  intro k _
  exact integral_smul_const _ _

end ActualCoefficients

section Sets
variable {A : Type*} {p r : ℕ}
abbrev CoefficientFamily (A : Type*) (p r : ℕ) := A → Fin p → Matrix (Fin r) (Fin r) ℝ

/-- The row ellipsoids are defined using the actual positive-definite design
matrix norm, not entrywise or Euclidean surrogate errors. -/
def momentRegion (Mhat : CoefficientFamily A p r) (V : A → Matrix (Fin r) (Fin r) ℝ)
    (β : A → Fin p → Fin r → ℝ) : Set (CoefficientFamily A p r) :=
  {M | ∀ a j i,RegressionConfidence.weightedNorm (V a) (fun l => Mhat a j i l-M a j i l)≤β a j i}

/-- The known inverse integration map gives the coefficient set exactly. -/
def coefficientRegion (W : Matrix (Fin p) (Fin p) ℝ) (Mhat : CoefficientFamily A p r)
    (V : A → Matrix (Fin r) (Fin r) ℝ) (β : A → Fin p → Fin r → ℝ) :
    Set (CoefficientFamily A p r) :=
  {F | ∃ M∈momentRegion Mhat V β,∀ a,F a=mix W⁻¹ (M a)}

/-- Invertibility makes coefficient-set membership exactly a row-ellipsoid
condition on the known forward moment map. No arbitrary projection event is
substituted for the actual confidence event. -/
theorem coefficientRegion_iff (W : Matrix (Fin p) (Fin p) ℝ) (hW : IsUnit W)
    (Mhat : CoefficientFamily A p r) (V : A → Matrix (Fin r) (Fin r) ℝ)
    (β : A → Fin p → Fin r → ℝ) (F : CoefficientFamily A p r) :
    F∈coefficientRegion W Mhat V β ↔ (fun a => mix W (F a))∈momentRegion Mhat V β := by
  constructor
  · rintro ⟨M,hM,hF⟩
    have he (a : A) : mix W (F a)=M a := by
      rw [hF a,mix_mul,Matrix.mul_nonsing_inv W ((Matrix.isUnit_iff_isUnit_det W).mp hW),mix_one]
    simpa only [he] using hM
  · intro hM
    exact ⟨(fun a => mix W (F a)),hM,fun a => (inverse_mix W hW (F a)).symm⟩

/-- Every integrated mass constraint is a real linear map of the submitted
coefficient array, with the known basis integrals kept explicit. -/
noncomputable def massConstraint (l : (Fin r → ℝ) →ₗ[ℝ] ℝ) (η : Fin p → ℝ)
    (a : A) (z : Fin r → ℝ) : CoefficientFamily A p r →ₗ[ℝ] ℝ where
  toFun F := l ((∑ k,η k • F a k) *ᵥ z)
  map_add' F G := by
    simp only [Pi.add_apply,smul_add,Finset.sum_add_distrib,Matrix.add_mulVec,map_add]
  map_smul' c F := by
    have he : (∑ k,η k • (c • F a k))=c • ∑ k,η k • F a k := by
      simp only [Finset.smul_sum,smul_smul]
      apply Finset.sum_congr rfl
      intro k _
      rw [mul_comm]
    change l ((∑ k,η k • (c • F a k)) *ᵥ z)=c*l ((∑ k,η k • F a k) *ᵥ z)
    rw [he,Matrix.smul_mulVec,map_smul]
    rfl

/-- Literal integrated mass, an affine slice independent of the data. -/
def exactMassRegion (l : (Fin r → ℝ) →ₗ[ℝ] ℝ) (η : Fin p → ℝ) :
    Set (CoefficientFamily A p r) := {F | ∀ a z,massConstraint l η a z F=l z}

def massConstrainedRegion (W : Matrix (Fin p) (Fin p) ℝ)
    (Mhat : CoefficientFamily A p r) (V : A → Matrix (Fin r) (Fin r) ℝ)
    (β : A → Fin p → Fin r → ℝ) (l : (Fin r → ℝ) →ₗ[ℝ] ℝ) (η : Fin p → ℝ) :
    Set (CoefficientFamily A p r) := coefficientRegion W Mhat V β ∩ exactMassRegion l η

/-- Every coefficient candidate inherits the genuine directional row bound
from a moment ellipsoid through the known inverse map. -/
theorem coefficient_region_directional (W : Matrix (Fin p) (Fin p) ℝ)
    (Mhat : CoefficientFamily A p r) (V : A → Matrix (Fin r) (Fin r) ℝ)
    (hV : ∀ a,(V a).PosDef) (β : A → Fin p → Fin r → ℝ)
    {F : CoefficientFamily A p r} (hF : F∈coefficientRegion W Mhat V β)
    (a : A) (k : Fin p) (i : Fin r) (x : Fin r → ℝ) :
    |(mix W⁻¹ (Mhat a) k *ᵥ x) i-(F a k *ᵥ x) i|≤
      ∑ j,|W⁻¹ k j| * β a j i*RegressionConfidence.weightedNorm (V a)⁻¹ x := by
  obtain ⟨M,hM,hFM⟩ := hF
  rw [hFM a]
  exact mixed_directional_error W⁻¹ (Mhat a) (M a) (V a) (hV a) (β a) (hM a) k i x

end Sets

section Truth
variable {A Y : Type*} {p r : ℕ} [MeasurableSpace Y]
variable {C : BaseNorm.ProbabilityCone (Fin r → ℝ)} {ν : Measure Y}
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν)

/-- The actual instrument's mass law places the true coefficient family in
the exact affine slice; entrywise confidence bounds play no role here. -/
theorem true_coefficients_exact_mass
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ)) (ψ : Fin p → Y → ℝ)
    (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k) (hψ : ∀ k,Integrable (ψ k) ν) :
    coefficientMatrices B∈exactMassRegion C.mass (basisIntegral (ν := ν) ψ) := by
  intro a z
  change C.mass ((∑ k,basisIntegral (ν := ν) ψ k • operatorMatrix (B a k)) *ᵥ z)=C.mass z
  rw [← operatorMatrix_sum,operatorMatrix_mulVec,← integratedOperator_expansion D B ψ hB hψ a]
  exact D.mass_preserving a z

/-- Exact mass intersection preserves inclusion of the literal true
coefficients whenever the actual moment rows obey their confidence bounds. -/
theorem true_coefficients_in_mass_region
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ))
    (g ψ : Fin p → Y → ℝ) (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν) (hψ : ∀ k,Integrable (ψ k) ν)
    (hW : IsUnit (basisMomentMatrix (ν := ν) g ψ))
    (Mhat : CoefficientFamily A p r) (V : A → Matrix (Fin r) (Fin r) ℝ)
    (β : A → Fin p → Fin r → ℝ)
    (hb : ∀ a j i,RegressionConfidence.weightedNorm (V a)
      (fun l => Mhat a j i l-momentMatrix D (g j) a i l)≤β a j i) :
    coefficientMatrices B∈massConstrainedRegion (basisMomentMatrix (ν := ν) g ψ)
      Mhat V β C.mass (basisIntegral (ν := ν) ψ) := by
  constructor
  · exact ⟨(fun a j => momentMatrix D (g j) a),hb,
      matrix_coefficient_reconstruction D B g ψ hB hgψ hW⟩
  · exact true_coefficients_exact_mass D B ψ hB hψ

/-- The literal true-coefficient coverage event is exactly the actual moment
row confidence event. Intersecting exact mass costs no probability, because
the real instrument supplies that mass law. -/
theorem true_mass_region_iff
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ))
    (g ψ : Fin p → Y → ℝ) (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν) (hψ : ∀ k,Integrable (ψ k) ν)
    (hW : IsUnit (basisMomentMatrix (ν := ν) g ψ))
    (Mhat : CoefficientFamily A p r) (V : A → Matrix (Fin r) (Fin r) ℝ)
    (β : A → Fin p → Fin r → ℝ) :
    coefficientMatrices B∈massConstrainedRegion (basisMomentMatrix (ν := ν) g ψ)
      Mhat V β C.mass (basisIntegral (ν := ν) ψ) ↔
    ∀ a j i,RegressionConfidence.weightedNorm (V a)
      (fun l => Mhat a j i l-momentMatrix D (g j) a i l)≤β a j i := by
  change (coefficientMatrices B∈coefficientRegion (basisMomentMatrix (ν := ν) g ψ) Mhat V β ∧
    coefficientMatrices B∈exactMassRegion C.mass (basisIntegral (ν := ν) ψ)) ↔ _
  rw [and_iff_left (true_coefficients_exact_mass D B ψ hB hψ),
    coefficientRegion_iff _ hW]
  have he : (fun a => mix (basisMomentMatrix (ν := ν) g ψ) (coefficientMatrices B a))=
      (fun a j => momentMatrix D (g j) a) := by
    funext a
    exact (matrix_moment_mixing D B g ψ hB hgψ a).symm
  rw [he]
  rfl

end Truth
end Komorebi.LSM.ObservableMoments
