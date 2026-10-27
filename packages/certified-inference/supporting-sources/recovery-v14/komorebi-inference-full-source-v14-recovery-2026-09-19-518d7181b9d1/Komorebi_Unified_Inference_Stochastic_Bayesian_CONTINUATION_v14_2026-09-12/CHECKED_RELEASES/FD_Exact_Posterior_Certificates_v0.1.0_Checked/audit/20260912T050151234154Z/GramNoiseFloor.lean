import Komorebi.FDInnovationConditioning

noncomputable section
set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix Komorebi.FiniteDimensionalGaussianKalman
open scoped RealInnerProductSpace

variable {ι υ : Type*} [Fintype ι] [Fintype υ] [DecidableEq ι]

omit [DecidableEq ι] in
/-- An exact rectangular Gram witness certifies semidefiniteness, including rank deficiency. -/
theorem gram_posSemidef (L : Matrix ι υ ℝ) : (L*L.transpose).PosSemidef := by
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    Matrix.posSemidef_self_mul_conjTranspose L

/-- A positive scalar floor plus a Gram witness certifies positive-definite noise. -/
theorem gram_noise_posDef (N : Matrix ι υ ℝ) (σ : ℝ) (hσ : 0 < σ) :
    (N*N.transpose + σ • (1 : Matrix ι ι ℝ)).PosDef := by
  exact Matrix.PosDef.posSemidef_add (gram_posSemidef N) (Matrix.PosDef.one.smul hσ)

/-- The witness supplies the actual Euclidean quadratic lower bound, not an eigenvalue guess. -/
theorem gram_noise_floor (N : Matrix ι υ ℝ) (σ : ℝ) :
    QuadraticLowerBound (N*N.transpose + σ • (1 : Matrix ι ι ℝ)) σ := by
  intro x
  have hg := matrixCLM_inner_nonneg (N*N.transpose) (gram_posSemidef N) x
  have hs : matrixCLM (σ • (1 : Matrix ι ι ℝ)) x = σ • x := by
    ext i
    simp [matrixCLM_apply, Matrix.smul_mulVec]
  simp only [matrixCLM_add, ContinuousLinearMap.add_apply, inner_add_right, hs,
    inner_smul_right, real_inner_self_eq_norm_sq]
  linarith

end Komorebi.ExactPosterior
