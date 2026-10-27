import Komorebi.FDGaussianTransport

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix

variable {ι κ τ : Type*} [Fintype ι] [Fintype κ] [Fintype τ]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq τ]

@[simp] theorem matrixCLM_mul (A : Matrix τ κ ℝ) (B : Matrix κ ι ℝ) :
    matrixCLM (A * B) = (matrixCLM A).comp (matrixCLM B) := by
  ext x i
  change ((A * B) *ᵥ x) i = (A *ᵥ (B *ᵥ x)) i
  rw [Matrix.mulVec_mulVec]

@[simp] theorem matrixCLM_add (A B : Matrix κ ι ℝ) :
    matrixCLM (A + B) = matrixCLM A + matrixCLM B := by
  ext x i
  change ((A+B) *ᵥ x) i = (A *ᵥ x) i + (B *ᵥ x) i
  rw [Matrix.add_mulVec]
  rfl

@[simp] theorem matrixCLM_sub (A B : Matrix κ ι ℝ) :
    matrixCLM (A - B) = matrixCLM A - matrixCLM B := by
  ext x i
  change ((A-B) *ᵥ x) i = (A *ᵥ x) i - (B *ᵥ x) i
  rw [Matrix.sub_mulVec]
  rfl

@[simp] theorem matrixCLM_one :
    matrixCLM (1 : Matrix ι ι ℝ) = ContinuousLinearMap.id ℝ (EuclideanSpace ℝ ι) := by
  ext x i
  change ((1 : Matrix ι ι ℝ) *ᵥ x) i = x i
  rw [Matrix.one_mulVec]

@[simp] theorem matrixCLM_zero :
    matrixCLM (0 : Matrix κ ι ℝ) = 0 := by
  ext x i
  change ((0 : Matrix κ ι ℝ) *ᵥ x) i = 0
  rw [Matrix.zero_mulVec]
  rfl

end Komorebi.FiniteDimensionalGaussianKalman
