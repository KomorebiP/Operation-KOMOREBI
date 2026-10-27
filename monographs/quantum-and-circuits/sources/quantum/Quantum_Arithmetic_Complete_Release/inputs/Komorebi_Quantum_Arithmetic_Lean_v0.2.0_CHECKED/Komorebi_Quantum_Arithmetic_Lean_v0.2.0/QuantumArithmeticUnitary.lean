module
public import QuantumArithmeticComplex
public import QuantumArithmeticSpecification
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Algebra.BigOperators.Field

@[expose] public section

set_option autoImplicit false
set_option maxRecDepth 16384
set_option maxHeartbeats 0

namespace Komorebi.QuantumArithmetic
open scoped BigOperators Matrix

/-- Exact character orthogonality, computed entirely in rational coordinates. -/
theorem cyclo12_character_orthogonality :
    ∀ k l : Fin 12,
      cSum (List.ofFn (fun n : Fin 12 =>
        cMul (cConj (cPow zeta12 (n.val * k.val)))
          (cPow zeta12 (n.val * l.val)))) =
        cRat (if k = l then 12 else 0) := by
  decide +kernel

/-- The same orthogonality identity in the actual complex numbers. -/
theorem complex12_character_orthogonality (k l : Fin 12) :
    (∑ n : Fin 12,
      star (toComplex zeta12 ^ (n.val * k.val)) *
        toComplex zeta12 ^ (n.val * l.val)) =
      if k = l then 12 else 0 := by
  have h := congrArg toComplex (cyclo12_character_orthogonality k l)
  simp only [toComplex_sum, List.map_ofFn, List.sum_ofFn, Function.comp_def,
    toComplex_mul, toComplex_conj, toComplex_pow, toComplex_rat] at h
  by_cases hkl : k = l <;> simpa only [hkl, ite_true, ite_false, Rat.cast_ofNat, Rat.cast_zero] using h

/-- The positive-sign Fourier matrix in dimension twelve. -/
noncomputable def fourier12 : Matrix (Fin 12) (Fin 12) ℂ :=
  fun n k => toComplex zeta12 ^ (n.val * k.val) / (Real.sqrt 12 : ℂ)

theorem sqrt12_complex_square : (Real.sqrt 12 : ℂ) * (Real.sqrt 12 : ℂ) = 12 := by
  norm_cast
  nlinarith [Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 12)]

theorem fourier12_symmetric (i j : Fin 12) : fourier12 i j = fourier12 j i := by
  simp [fourier12, Nat.mul_comm]

/-- The normalization really produces a unitary matrix, not an unnormalized DFT. -/
theorem fourier12_adjoint_mul_self : fourier12ᴴ * fourier12 = 1 := by
  ext k l
  simp only [Matrix.mul_apply, Matrix.conjTranspose_apply]
  have he (n : Fin 12) : star (fourier12 n k) * fourier12 n l =
      (star (toComplex zeta12 ^ (n.val * k.val)) *
       toComplex zeta12 ^ (n.val * l.val)) / 12 := by
    simp only [fourier12, star_div₀, Complex.star_def, Complex.conj_ofReal]
    rw [div_mul_div_comm, sqrt12_complex_square]
  simp_rw [he]
  rw [← Finset.sum_div, complex12_character_orthogonality]
  by_cases h : k = l <;> simp [h, Matrix.one_apply]

/-- The reverse product is the identity as well. -/
theorem fourier12_mul_adjoint : fourier12 * fourier12ᴴ = 1 := by
  ext k l
  have h := congrArg (fun M : Matrix (Fin 12) (Fin 12) ℂ => M l k)
    fourier12_adjoint_mul_self
  simp only [Matrix.mul_apply, Matrix.conjTranspose_apply] at h ⊢
  simpa only [fourier12_symmetric, mul_comm, Matrix.one_apply, eq_comm] using h

end Komorebi.QuantumArithmetic
