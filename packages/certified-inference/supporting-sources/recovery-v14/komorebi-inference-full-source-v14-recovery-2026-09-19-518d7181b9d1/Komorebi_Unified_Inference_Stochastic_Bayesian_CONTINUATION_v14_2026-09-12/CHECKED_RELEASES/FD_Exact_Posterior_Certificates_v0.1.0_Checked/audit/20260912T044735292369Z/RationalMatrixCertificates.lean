import Mathlib.Basic.Real.Basic
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Algebra.Algebra.Rat

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix

variable {ι κ ν τ : Type*}

/-- Exact rational entries, interpreted without a floating-point conversion. -/
noncomputable def realMatrix (A : Matrix ι κ ℚ) : Matrix ι κ ℝ :=
  fun i j => (A i j : ℝ)

def rationalEnergy [Fintype ι] [Fintype κ] (A : Matrix ι κ ℚ) : ℚ :=
  ∑ i, ∑ j, (A i j)^2

def rationalVectorEnergy [Fintype ι] (v : ι → ℚ) : ℚ := ∑ i, (v i)^2

@[simp] theorem realMatrix_apply (A : Matrix ι κ ℚ) (i : ι) (j : κ) :
    realMatrix A i j = (A i j : ℝ) := rfl

@[simp] theorem realMatrix_transpose (A : Matrix ι κ ℚ) :
    realMatrix A.transpose = (realMatrix A).transpose := rfl

@[simp] theorem realMatrix_zero : realMatrix (0 : Matrix ι κ ℚ) = 0 := by
  ext i j
  simp [realMatrix]

@[simp] theorem realMatrix_one [DecidableEq ι] :
    realMatrix (1 : Matrix ι ι ℚ) = 1 := by
  ext i j
  by_cases h : i = j <;> simp [realMatrix, Matrix.one_apply, h]

@[simp] theorem realMatrix_add (A B : Matrix ι κ ℚ) :
    realMatrix (A+B) = realMatrix A + realMatrix B := by
  ext i j
  simp [realMatrix]

@[simp] theorem realMatrix_sub (A B : Matrix ι κ ℚ) :
    realMatrix (A-B) = realMatrix A - realMatrix B := by
  ext i j
  simp [realMatrix]

@[simp] theorem realMatrix_smul (q : ℚ) (A : Matrix ι κ ℚ) :
    realMatrix (q • A) = (q : ℝ) • realMatrix A := by
  ext i j
  simp [realMatrix]

@[simp] theorem realMatrix_mul [Fintype κ] (A : Matrix ι κ ℚ) (B : Matrix κ ν ℚ) :
    realMatrix (A*B) = realMatrix A * realMatrix B := by
  ext i j
  simp [realMatrix, Matrix.mul_apply]

@[simp] theorem realMatrix_sum (s : Finset τ) (A : τ → Matrix ι κ ℚ) :
    realMatrix (∑ t ∈ s, A t) = ∑ t ∈ s, realMatrix (A t) := by
  ext i j
  simp [realMatrix]

@[simp] theorem rational_mulVec_cast [Fintype κ] (A : Matrix ι κ ℚ) (v : κ → ℚ) (i : ι) :
    ((A *ᵥ v) i : ℝ) = (realMatrix A *ᵥ fun j => (v j : ℝ)) i := by
  simp [Matrix.mulVec, dotProduct, realMatrix]

theorem rationalEnergy_nonneg [Fintype ι] [Fintype κ] (A : Matrix ι κ ℚ) :
    0 ≤ rationalEnergy A := by
  exact Finset.sum_nonneg fun i _ => Finset.sum_nonneg fun j _ => sq_nonneg (A i j)

theorem rationalVectorEnergy_nonneg [Fintype ι] (v : ι → ℚ) :
    0 ≤ rationalVectorEnergy v := by
  exact Finset.sum_nonneg fun i _ => sq_nonneg (v i)

end Komorebi.ExactPosterior
