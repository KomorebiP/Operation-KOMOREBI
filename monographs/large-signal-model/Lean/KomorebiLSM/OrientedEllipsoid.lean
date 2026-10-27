import KomorebiLSM.EllipsoidGeometry
import KomorebiLSM.EllipsoidDualCS
import KomorebiLSM.PolynomialGram

/-! Oriented quadratic certificates on the actual ellipsoid cone. -/
set_option autoImplicit false
namespace Komorebi.LSM.OrientedEllipsoid
open scoped BigOperators Matrix
variable {D : Type*} [Fintype D] [DecidableEq D]

/-- The literal mass-first centering matrix from the monograph. -/
def centerMatrix (c : D → ℝ) : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ :=
  Matrix.fromBlocks 1 0 (fun i _ => -c i) 1

/-- The uncentered quadratic form has one positive mass coordinate. -/
def diagonalForm (H : Matrix D D ℝ) : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ :=
  Matrix.fromBlocks 1 0 0 (-H)

/-- This is literally S_cᵀ diag(1,-H) S_c. -/
def Q (c : D → ℝ) (H : Matrix D D ℝ) : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ :=
  (centerMatrix c).transpose * diagonalForm H * centerMatrix c

theorem centerMatrix_mulVec (c : D → ℝ) (z : State D) :
    centerMatrix c *ᵥ z = point (mass z) (centered c z) := by
  ext i
  rcases i with i | i
  · cases i
    simp [Matrix.fromBlocks,centerMatrix,point,Matrix.mulVec,dotProduct,mass,Fintype.sum_sum_type]
  · simp [Matrix.one_apply,Matrix.fromBlocks,centerMatrix,point,centered,spatial,mass,Matrix.mulVec,dotProduct,
      Fintype.sum_sum_type,sub_eq_add_neg,mul_comm,add_comm]

omit [DecidableEq D] in
theorem diagonalForm_mulVec (H : Matrix D D ℝ) (m : ℝ) (x : D → ℝ) :
    diagonalForm H *ᵥ point m x = point m (-(H *ᵥ x)) := by
  rw [diagonalForm,Matrix.fromBlocks_mulVec]
  ext i
  rcases i with i | i
  · cases i
    simp [point]
  · simp [point,Matrix.neg_mulVec]

omit [DecidableEq D] in
theorem point_dotProduct (m n : ℝ) (x y : D → ℝ) :
    point m x ⬝ᵥ point n y = m*n + x ⬝ᵥ y := by
  simp [dotProduct,Fintype.sum_sum_type,point]

/-- The centered quadratic matrix represents exactly m²-(x-mc)ᵀH(x-mc). -/
theorem quadratic_form (c : D → ℝ) (H : Matrix D D ℝ) (z : State D) :
    z ⬝ᵥ (Q c H *ᵥ z) = (mass z)^2 - centered c z ⬝ᵥ (H *ᵥ centered c z) := by
  rw [Q,← Matrix.mulVec_mulVec,← Matrix.mulVec_mulVec,
    Matrix.dotProduct_transpose_mulVec,centerMatrix_mulVec,
    diagonalForm_mulVec,point_dotProduct,neg_dotProduct,dotProduct_comm (H *ᵥ centered c z)]
  ring

theorem cone_iff_quadratic (c : D → ℝ) (H : Matrix D D ℝ) (z : State D) :
    z∈cone c H ↔ 0≤mass z ∧ 0≤z ⬝ᵥ (Q c H *ᵥ z) := by
  rw [quadratic_form]
  exact and_congr_right (fun _ => sub_nonneg.symm)

def massConstant (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) : ℝ := B (Sum.inl ()) (Sum.inl ())
def massSpatial (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (i : D) : ℝ := B (Sum.inl ()) (Sum.inr i)
def beta (c : D → ℝ) (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) : ℝ :=
  massConstant B + massSpatial B ⬝ᵥ c

omit [DecidableEq D] in
theorem mass_mulVec (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (z : State D) :
    mass (B *ᵥ z) = massConstant B * mass z + massSpatial B ⬝ᵥ spatial z := by
  simp [mass,massConstant,massSpatial,spatial,Matrix.mulVec,dotProduct,Fintype.sum_sum_type]

omit [DecidableEq D] in
theorem mass_mulVec_centered (c : D → ℝ)
    (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (z : State D) :
    mass (B *ᵥ z) = beta c B * mass z + massSpatial B ⬝ᵥ centered c z := by
  rw [mass_mulVec,beta,centered_apply,dotProduct_sub,dotProduct_smul]
  ring

/-- The actual matrix identity propagates the quadratic half of the cone. -/
theorem quadratic_output_nonneg (c : D → ℝ) (H : Matrix D D ℝ)
    (B R : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (tau : ℝ)
    (htau : 0≤tau) (hR : R.PosSemidef)
    (hidentity : B.transpose * Q c H * B - tau • Q c H = R)
    {z : State D} (hz : 0≤z ⬝ᵥ (Q c H *ᵥ z)) :
    0≤(B *ᵥ z) ⬝ᵥ (Q c H *ᵥ (B *ᵥ z)) := by
  have hr : 0≤z ⬝ᵥ (R *ᵥ z) := by simpa only [star_trivial] using hR.dotProduct_mulVec_nonneg z
  have he := congrArg (fun M : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ => z ⬝ᵥ (M *ᵥ z)) hidentity
  simp only [Matrix.sub_mulVec,Matrix.smul_mulVec,dotProduct_sub,dotProduct_smul] at he
  rw [← Matrix.mulVec_mulVec,← Matrix.mulVec_mulVec,Matrix.dotProduct_transpose_mulVec] at he
  rw [dotProduct_comm (Q c H *ᵥ (B *ᵥ z))] at he
  simp only [smul_eq_mul] at he
  nlinarith [mul_nonneg htau hz]

/-- Literal quadratic and orientation witnesses for one actual branch matrix. -/
structure BranchCertificate (c : D → ℝ) (H : Matrix D D ℝ)
    (B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) where
  tau : ℝ
  remainder : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ
  tau_nonneg : 0≤tau
  remainder_positive : remainder.PosSemidef
  identity : B.transpose * Q c H * B - tau • Q c H = remainder
  beta_nonneg : 0≤beta c B
  orientation : 0≤(beta c B)^2 - massSpatial B ⬝ᵥ (H⁻¹ *ᵥ massSpatial B)

/-- The orientation witness selects the forward sheet, including zero-mass inputs. -/
theorem BranchCertificate.preserves {c : D → ℝ} {H : Matrix D D ℝ} (hH : H.PosDef)
    {B : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ} (cert : BranchCertificate c H B)
    {z : State D} (hz : z∈cone c H) : B *ᵥ z ∈ cone c H := by
  apply (cone_iff_quadratic c H _).mpr
  constructor
  · rw [mass_mulVec_centered]
    exact mass_orientation H hH (massSpatial B) (centered c z) (beta c B) (mass z)
      hz.1 hz.2 cert.beta_nonneg cert.orientation
  · exact quadratic_output_nonneg c H B cert.remainder cert.tau cert.tau_nonneg
      cert.remainder_positive cert.identity ((cone_iff_quadratic c H z).mp hz).2

end Komorebi.LSM.OrientedEllipsoid
