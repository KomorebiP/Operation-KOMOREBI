import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

/-- Squared real Hilbert--Schmidt energy. No matrix operator norm is used. -/
def matrixEnergy (A : Matrix ι κ ℝ) : ℝ := ∑ i, ∑ j, (A i j)^2

theorem matrixEnergy_nonneg (A : Matrix ι κ ℝ) : 0 ≤ matrixEnergy A := by
  exact Finset.sum_nonneg (fun i _ => Finset.sum_nonneg (fun j _ => sq_nonneg (A i j)))

@[simp] theorem matrixEnergy_zero : matrixEnergy (0 : Matrix ι κ ℝ) = 0 := by
  simp [matrixEnergy]

@[simp] theorem matrixEnergy_transpose (A : Matrix ι κ ℝ) :
    matrixEnergy A.transpose = matrixEnergy A := by
  exact Finset.sum_comm

/-- Trace of the column Gram matrix is squared Hilbert--Schmidt energy. -/
theorem trace_gram_eq_energy (A : Matrix ι κ ℝ) :
    (A.transpose * A).trace = matrixEnergy A := by
  simp only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply,
    Matrix.transpose_apply, pow_two, matrixEnergy]
  exact Finset.sum_comm

theorem matrixEnergy_eq_zero_iff (A : Matrix ι κ ℝ) : matrixEnergy A = 0 ↔ A = 0 := by
  constructor
  · intro h
    have hr := (Finset.sum_eq_zero_iff_of_nonneg
      (fun i _ => Finset.sum_nonneg (fun j _ => sq_nonneg (A i j)))).mp h
    ext i j
    have hc := (Finset.sum_eq_zero_iff_of_nonneg
      (fun j _ => sq_nonneg (A i j))).mp (hr i (Finset.mem_univ i))
    exact sq_eq_zero_iff.mp (hc j (Finset.mem_univ j))
  · intro h
    rw [h, matrixEnergy_zero]

/-- Self-adjointness and idempotence remove the repeated left projection in the Gram trace. -/
theorem matrixEnergy_left_projector (P : Matrix ι ι ℝ) (A : Matrix ι κ ℝ)
    (hT : P.transpose = P) (hI : P * P = P) :
    matrixEnergy (P*A) = (A.transpose * P * A).trace := by
  rw [← trace_gram_eq_energy]
  calc
    ((P*A).transpose*(P*A)).trace = (A.transpose * (P*P) * A).trace := by
      simp only [Matrix.transpose_mul, hT, Matrix.mul_assoc]
    _ = _ := by rw [hI]

end Komorebi.PacketEnergy
