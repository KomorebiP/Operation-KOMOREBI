import Komorebi.RichardsonSpectrum
import Komorebi.PacketMatrixEnergy

noncomputable section
set_option autoImplicit false
namespace Komorebi.GainSolver
open Matrix Komorebi.FiniteDimensionalGaussianKalman Komorebi.PacketEnergy
open scoped RealInnerProductSpace
variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq κ]

omit [Fintype ι] in
/-- Right matrix multiplication is transpose action on each Euclidean row. -/
theorem row_action (F : Matrix ι κ ℝ) (T : Matrix κ κ ℝ) (i : ι) :
    (WithLp.toLp 2 ((F*T) i) : EuclideanSpace ℝ κ) =
      matrixCLM T.transpose (WithLp.toLp 2 (F i)) := by
  ext j
  change (∑ l, F i l*T l j) = ∑ l, T l j*F i l
  apply Finset.sum_congr rfl
  intro l _
  ring

omit [DecidableEq κ] in
/-- The explicit squared Frobenius normalization is the sum of squared Euclidean row norms. -/
theorem matrixEnergy_eq_row_norms (F : Matrix ι κ ℝ) :
    matrixEnergy F = ∑ i, ‖(WithLp.toLp 2 (F i) : EuclideanSpace ℝ κ)‖^2 := by
  simp only [EuclideanSpace.real_norm_sq_eq]
  rfl

omit [Fintype ι] in
/-- Richardson's transition acts as identity minus the scaled self-adjoint operator. -/
theorem richardson_action (S : Matrix κ κ ℝ) (Λ : ℝ) (x : EuclideanSpace ℝ κ) :
    matrixCLM (1 - Λ⁻¹ • S) x = x - Λ⁻¹ • matrixCLM S x := by
  ext i
  change ((1-Λ⁻¹ • S)*ᵥ x) i = x i - Λ⁻¹*(S*ᵥ x) i
  rw [Matrix.sub_mulVec, Matrix.one_mulVec, Matrix.smul_mulVec]
  rfl

/-- The Euclidean spectral contraction gives a rectangular Frobenius contraction. -/
theorem richardson_matrix_energy_contract (S : Matrix κ κ ℝ) (hS : S.IsHermitian)
    (σ Λ : ℝ) (hΛ : 0 < Λ)
    (hlo : ∀ i, σ ≤ hS.eigenvalues i) (hhi : ∀ i, hS.eigenvalues i ≤ Λ)
    (F : Matrix ι κ ℝ) :
    matrixEnergy (F*(1-Λ⁻¹ • S)) ≤ (1-σ/Λ)^2 * matrixEnergy F := by
  have hT : (1-Λ⁻¹ • S).transpose = 1-Λ⁻¹ • S := by
    have ht : S.transpose = S := by simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using hS.eq
    simp only [Matrix.transpose_sub, Matrix.transpose_one, Matrix.transpose_smul, ht]
  rw [matrixEnergy_eq_row_norms, matrixEnergy_eq_row_norms, Finset.mul_sum]
  apply Finset.sum_le_sum
  intro i _
  rw [row_action, hT, richardson_action]
  exact richardson_vector_sq_contract S hS σ Λ hΛ hlo hhi _

/-- A computable conservative spectral cap: noise floor plus trace of the innovation. -/
theorem trace_step_energy_contract (S : Matrix κ κ ℝ) (hS : S.PosSemidef)
    (σ : ℝ) (hσ : 0 < σ) (hfloor : QuadraticLowerBound S σ) (F : Matrix ι κ ℝ) :
    matrixEnergy (F*(1-(σ+S.trace)⁻¹ • S)) ≤
      (1-σ/(σ+S.trace))^2 * matrixEnergy F := by
  have ht := psd_trace_nonneg S hS
  exact richardson_matrix_energy_contract S hS.isHermitian σ (σ+S.trace)
    (by positivity) (eigenvalue_lower S hS.isHermitian σ hfloor)
    (fun i => (eigenvalue_le_trace S hS i).trans (by linarith)) F
end Komorebi.GainSolver
