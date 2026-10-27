module
public import Mathlib.NumberTheory.Padics.PadicIntegers
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.Algebra.MvPolynomial.PDeriv

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialWeightedInverse
open Matrix
variable {d e : ℕ}

/-- The actual Jacobian of a polynomial system at the specified base point. -/
def jacobian {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin d) R) (a : Fin d → R) : Matrix (Fin e) (Fin d) R :=
  fun i j => MvPolynomial.eval a (MvPolynomial.pderiv j (F i))

/-- Multiplication of a polynomial system by a constant coefficient matrix. -/
def precondition {R : Type*} [CommRing R] (A : Matrix (Fin e) (Fin e) R)
    (F : Fin e → MvPolynomial (Fin d) R) : Fin e → MvPolynomial (Fin d) R :=
  fun i => ∑ j, MvPolynomial.C (A i j) * F j

/-- Constant matrix multiplication commutes with actual polynomial evaluation. -/
theorem eval_precondition {R : Type*} [CommRing R] (A : Matrix (Fin e) (Fin e) R)
    (F : Fin e → MvPolynomial (Fin d) R) (a : Fin d → R) :
    (fun i => MvPolynomial.eval a (precondition A F i)) =
      A.mulVec (fun i => MvPolynomial.eval a (F i)) := by
  ext i
  simp [precondition, Matrix.mulVec, dotProduct]

/-- The Jacobian of the preconditioned system is the actual matrix product. -/
theorem jacobian_precondition {R : Type*} [CommRing R]
    (A : Matrix (Fin e) (Fin e) R) (F : Fin e → MvPolynomial (Fin d) R)
    (a : Fin d → R) : jacobian (precondition A F) a = A * jacobian F a := by
  ext i k
  simp [jacobian, precondition, Matrix.mul_apply]

/-- An integral matrix preserves every coordinatewise divisibility condition. -/
theorem mulVec_preserves_dvd {R : Type*} [CommRing R]
    (A : Matrix (Fin e) (Fin d) R) (c : R) (v : Fin d → R)
    (hv : ∀ j, c ∣ v j) : ∀ i, c ∣ A.mulVec v i := by
  intro i
  change c ∣ ∑ j, A i j * v j
  apply Finset.dvd_sum
  intro j _
  exact dvd_mul_of_dvd_right (hv j) (A i j)

/-- A nonzero scalar right inverse certificate makes the matrix action injective. -/
theorem mulVec_injective_of_scalar_certificate {R : Type*} [CommRing R]
    [IsDomain R] (A J : Matrix (Fin d) (Fin d) R) (c : R) (hc : c ≠ 0)
    (hJA : J * A = c • (1 : Matrix (Fin d) (Fin d) R)) :
    Function.Injective A.mulVec := by
  intro u v huv
  have h := congrArg J.mulVec huv
  simp only [Matrix.mulVec_mulVec, hJA, Matrix.smul_mulVec, Matrix.one_mulVec] at h
  funext i
  exact mul_left_cancel₀ hc (congrFun h i)

/-- The coefficient inclusion into the fraction field, applied entrywise. -/
def rationalMatrix (p : ℕ) [Fact (Nat.Prime p)]
    (A : Matrix (Fin d) (Fin d) ℤ_[p]) : Matrix (Fin d) (Fin d) ℚ_[p] :=
  (algebraMap ℤ_[p] ℚ_[p]).mapMatrix A

/-- Entrywise inclusion into the fraction field loses no matrix information. -/
theorem rationalMatrix_injective (p : ℕ) [Fact (Nat.Prime p)] :
    Function.Injective (rationalMatrix p (d := d)) := by
  intro A B h
  ext i j
  exact Subtype.coe_injective (congrFun (congrFun h i) j)

@[simp] theorem rationalMatrix_mul (p : ℕ) [Fact (Nat.Prime p)]
    (A J : Matrix (Fin d) (Fin d) ℤ_[p]) :
    rationalMatrix p (A * J) = rationalMatrix p A * rationalMatrix p J :=
  map_mul _ A J

@[simp] theorem rationalMatrix_scalar (p s : ℕ) [Fact (Nat.Prime p)] :
    rationalMatrix p ((p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) =
      (p : ℚ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℚ_[p]) := by
  ext i j
  by_cases h : i = j <;> simp [rationalMatrix, h]

/-- The written denominator bound on the inverse gives both integral matrix identities. -/
theorem certificate_of_integral_inverse (p s : ℕ) [Fact (Nat.Prime p)]
    (J A : Matrix (Fin d) (Fin d) ℤ_[p]) (hJ : IsUnit (rationalMatrix p J))
    (hA : rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹) :
    A * J = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]) ∧
    J * A = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]) := by
  have hdet := (Matrix.isUnit_iff_isUnit_det _).mp hJ
  constructor
  · apply rationalMatrix_injective p
    rw [rationalMatrix_mul, rationalMatrix_scalar, hA, Matrix.smul_mul,
      Matrix.nonsing_inv_mul _ hdet]
  · apply rationalMatrix_injective p
    rw [rationalMatrix_mul, rationalMatrix_scalar, hA, Matrix.mul_smul,
      Matrix.mul_nonsing_inv _ hdet]

/-- Conversely, under nonsingularity a scalar left inverse certificate is exactly the
integral representative of the bounded rational inverse. -/
theorem integral_inverse_of_certificate (p s : ℕ) [Fact (Nat.Prime p)]
    (J A : Matrix (Fin d) (Fin d) ℤ_[p]) (hJ : IsUnit (rationalMatrix p J))
    (hAJ : A * J = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) :
    rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹ := by
  have hdet := (Matrix.isUnit_iff_isUnit_det _).mp hJ
  have h := congrArg (rationalMatrix p) hAJ
  rw [rationalMatrix_mul, rationalMatrix_scalar] at h
  calc
    rationalMatrix p A = (rationalMatrix p A * rationalMatrix p J) *
        (rationalMatrix p J)⁻¹ := by
      rw [Matrix.mul_assoc, Matrix.mul_nonsing_inv _ hdet, Matrix.mul_one]
    _ = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹ := by
      rw [h, Matrix.smul_mul, Matrix.one_mul]

/-- At every exponent the inverse-denominator condition is equivalent to an integral certificate. -/
theorem integral_inverse_iff_certificate (p s : ℕ) [Fact (Nat.Prime p)]
    (J : Matrix (Fin d) (Fin d) ℤ_[p]) (hJ : IsUnit (rationalMatrix p J)) :
    (∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹) ↔
    (∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      A * J = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]) ∧
      J * A = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) := by
  constructor
  · rintro ⟨A, hA⟩
    exact ⟨A, certificate_of_integral_inverse p s J A hJ hA⟩
  · rintro ⟨A, hAJ, _⟩
    exact ⟨A, integral_inverse_of_certificate p s J A hJ hAJ⟩

/-- An integral scalar left inverse certificate itself proves nonsingularity over the fraction field. -/
theorem rationalMatrix_isUnit_of_certificate (p s : ℕ) [Fact (Nat.Prime p)]
    (J A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * J = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) :
    IsUnit (rationalMatrix p J) := by
  have h := congrArg (rationalMatrix p) hAJ
  rw [rationalMatrix_mul, rationalMatrix_scalar] at h
  apply Matrix.mulVec_injective_iff_isUnit.mp
  apply mulVec_injective_of_scalar_certificate (rationalMatrix p J)
    (rationalMatrix p A) ((p : ℚ_[p])^s) _ h
  exact pow_ne_zero s (Nat.cast_ne_zero.mpr (Fact.out : Nat.Prime p).ne_zero)

/-- The effective integral certificate is equivalent to precisely the written rational inverse
hypothesis, including nonsingularity and with the same denominator exponent. -/
theorem bounded_inverse_iff_certificate (p s : ℕ) [Fact (Nat.Prime p)]
    (J : Matrix (Fin d) (Fin d) ℤ_[p]) :
    (IsUnit (rationalMatrix p J) ∧
      ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
        rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p J)⁻¹) ↔
    (∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      A * J = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]) ∧
      J * A = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) := by
  constructor
  · rintro ⟨hJ, hA⟩
    exact (integral_inverse_iff_certificate p s J hJ).mp hA
  · rintro ⟨A, hAJ, hJA⟩
    have hJ := rationalMatrix_isUnit_of_certificate p s J A hAJ
    exact ⟨hJ, (integral_inverse_iff_certificate p s J hJ).mpr ⟨A, hAJ, hJA⟩⟩

/-- The integral inverse certificate yields injectivity even when the Jacobian is singular modulo p. -/
theorem padic_mulVec_injective (p s : ℕ) [Fact (Nat.Prime p)]
    (A J : Matrix (Fin d) (Fin d) ℤ_[p])
    (hJA : J * A = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) :
    Function.Injective A.mulVec := by
  apply mulVec_injective_of_scalar_certificate A J ((p : ℤ_[p])^s) _ hJA
  exact pow_ne_zero s (Nat.cast_ne_zero.mpr (Fact.out : Nat.Prime p).ne_zero)

/-- Preconditioning by the bounded inverse certificate preserves exactly the original roots. -/
theorem precondition_root_iff (p s : ℕ) [Fact (Nat.Prime p)]
    (A J : Matrix (Fin d) (Fin d) ℤ_[p])
    (hJA : J * A = (p : ℤ_[p])^s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (F : Fin d → MvPolynomial (Fin d) ℤ_[p]) (a : Fin d → ℤ_[p]) :
    (fun i => MvPolynomial.eval a (precondition A F i)) = 0 ↔
      (fun i => MvPolynomial.eval a (F i)) = 0 := by
  rw [eval_precondition]
  constructor
  · intro h
    apply padic_mulVec_injective p s A J hJA
    simpa only [Matrix.mulVec_zero] using h
  · intro h
    rw [h, Matrix.mulVec_zero]

end Komorebi.PolynomialWeightedInverse
