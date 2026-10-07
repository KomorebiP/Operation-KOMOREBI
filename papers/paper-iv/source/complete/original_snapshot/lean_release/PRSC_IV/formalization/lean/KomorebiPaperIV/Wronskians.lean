/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.EntireBridge
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Algebra.BigOperators.Intervals

/-!
# Analytic Wronskians of the cyclic bases

The determinant calculation factors the derivative matrix into a Vandermonde
matrix, a diagonal exponential matrix, and a constant weight matrix. It does
not assume Abel's identity or invertibility of the Vandermonde matrix.
-/

namespace Komorebi.PaperIV
noncomputable section

/-- Derivative matrix for N finite exponential sums. -/
def exponentialJetMatrix (N : ℕ) (w : ℕ → Fin N → ℂ) (a : ℕ → ℂ) (z : ℂ) :
    Matrix (Fin N) (Fin N) ℂ :=
  fun k j => exponentialSumJet N (fun l => w l j) a k.val z

theorem exponentialJetMatrix_factor (N : ℕ) (w : ℕ → Fin N → ℂ)
    (a : ℕ → ℂ) (z : ℂ) :
    exponentialJetMatrix N w a z =
      Matrix.of (fun k l : Fin N => a l.val ^ k.val) *
        Matrix.diagonal (fun l : Fin N => Complex.exp (a l.val * z)) *
        Matrix.of (fun l j : Fin N => w l.val j) := by
  ext k j
  change (∑ l ∈ Finset.range N, w l j * a l ^ k.val * Complex.exp (a l * z)) = _
  rw [Matrix.mul_apply]
  simp only [Matrix.mul_diagonal, Matrix.of_apply]
  rw [Finset.sum_range (fun l => w l j * a l ^ k.val * Complex.exp (a l * z))]
  apply Finset.sum_congr rfl
  intro l _
  ring

theorem det_exponentialJetMatrix (N : ℕ) (w : ℕ → Fin N → ℂ)
    (a : ℕ → ℂ) (z : ℂ) :
    (exponentialJetMatrix N w a z).det =
      Complex.exp ((∑ l ∈ Finset.range N, a l) * z) *
        (exponentialJetMatrix N w a 0).det := by
  rw [exponentialJetMatrix_factor, exponentialJetMatrix_factor]
  simp only [mul_zero, Complex.exp_zero, Matrix.diagonal_one,
    Matrix.mul_one, Matrix.det_mul, Matrix.det_diagonal]
  rw [← Complex.exp_sum, Finset.sum_range a, Finset.sum_mul]
  ring

theorem det_exponentialJetMatrix_constant (N : ℕ) (w : ℕ → Fin N → ℂ)
    (a : ℕ → ℂ) (ha : ∑ l ∈ Finset.range N, a l = 0) (z : ℂ) :
    (exponentialJetMatrix N w a z).det = (exponentialJetMatrix N w a 0).det := by
  rw [det_exponentialJetMatrix, ha]
  simp

/-- The ordinary analytic Wronskian, using actual iterated derivatives. -/
def analyticWronskian {N : ℕ} (f : Fin N → ℂ → ℂ) (z : ℂ) : ℂ :=
  Matrix.det (fun k j : Fin N => deriv^[k.val] (f j) z)

theorem transferWronskian_constant {N : ℕ} (hN : 1 < N) {omega : ℂ}
    (homega : IsPrimitiveRoot omega N) (lambda z : ℂ) :
    analyticWronskian (fun j : Fin N => entireTransfer N j.val omega lambda) z =
      analyticWronskian (fun j : Fin N => entireTransfer N j.val omega lambda) 0 := by
  simp only [analyticWronskian, entireTransfer_eq_exponentialSum,
    iteratedDeriv_exponentialSum]
  apply det_exponentialJetMatrix_constant N
    (fun l j => (N : ℂ)⁻¹ * ((omega ^ j.val)⁻¹) ^ l)
    (fun l => lambda * omega ^ l)
  rw [← Finset.mul_sum, homega.geom_sum_eq_zero hN, mul_zero]

/-- Corollary 4.3, including its exact exponent and ordered basis. -/
theorem transferWronskian_eq {N : ℕ} (hN : 1 < N) {omega : ℂ}
    (homega : IsPrimitiveRoot omega N) (lambda z : ℂ) :
    analyticWronskian (fun j : Fin N => entireTransfer N j.val omega lambda) z =
      lambda ^ (N * (N - 1) / 2) := by
  rw [transferWronskian_constant hN homega]
  have hm : (fun k j : Fin N => deriv^[k.val]
      (entireTransfer N j.val omega lambda) 0) =
      Matrix.diagonal (fun j : Fin N => lambda ^ j.val) := by
    ext k j
    rw [entireTransfer_initial_data (by omega) j.isLt k.isLt homega]
    by_cases h : k = j
    · subst k
      simp
    · simp [h, Fin.ext_iff.mpr.mt h]
  rw [analyticWronskian, hm, Matrix.det_diagonal, Finset.prod_pow_eq_pow_sum]
  rw [← Finset.sum_range (fun i => i), Finset.sum_range_id]

theorem signedWronskian_constant {N : ℕ} (hN : 1 < N) {omega : ℂ}
    (homega : IsPrimitiveRoot omega N) (rho z : ℂ) :
    analyticWronskian (fun j : Fin N => entireSigned N j.val omega rho) z =
      analyticWronskian (fun j : Fin N => entireSigned N j.val omega rho) 0 := by
  simp only [analyticWronskian, entireSigned_eq_exponentialSum,
    iteratedDeriv_exponentialSum]
  apply det_exponentialJetMatrix_constant N
    (fun l j => (rho ^ j.val)⁻¹ * (N : ℂ)⁻¹ * ((omega ^ j.val)⁻¹) ^ l)
    (fun l => rho * omega ^ l)
  rw [← Finset.mul_sum, homega.geom_sum_eq_zero hN, mul_zero]

/-- Corollary 5.4: the signed analytic Wronskian is identically one. -/
theorem signedWronskian_eq_one {N : ℕ} (hN : 1 < N) {omega rho : ℂ}
    (homega : IsPrimitiveRoot omega N) (hrho : rho ^ N = -1) (z : ℂ) :
    analyticWronskian (fun j : Fin N => entireSigned N j.val omega rho) z = 1 := by
  rw [signedWronskian_constant hN homega]
  have hm : (fun k j : Fin N => deriv^[k.val]
      (entireSigned N j.val omega rho) 0) = (1 : Matrix (Fin N) (Fin N) ℂ) := by
    ext k j
    rw [entireSigned_initial_data (by omega) j.isLt k.isLt homega hrho]
    simp [Matrix.one_apply, Fin.ext_iff]
  rw [analyticWronskian, hm, Matrix.det_one]

end
end Komorebi.PaperIV
