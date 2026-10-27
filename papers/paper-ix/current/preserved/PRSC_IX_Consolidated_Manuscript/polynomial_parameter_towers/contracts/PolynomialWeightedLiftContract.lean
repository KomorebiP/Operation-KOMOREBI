module
public import PolynomialWeightedLift

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialWeightedLiftContract
open MvPolynomial
variable {d : ℕ}

/-- An expanded contract using the actual evaluated derivative matrix and an
integral inverse certificate; no normalization or contraction is a hypothesis. -/
theorem actual_jacobian_integral_certificate (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * (Matrix.of fun i j => eval a (pderiv j (F i))) =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hJA : (Matrix.of fun i j => eval a (pderiv j (F i))) * A =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (F i)) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (r - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p], (∀ i, eval z (F i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) :=
  PolynomialWeightedLift.exists_weighted_root_certificate p s r hr F a A hAJ hJA hF

/-- The written rational inverse hypothesis is applied to the actual Jacobian.
Uniqueness is on the entire stated ball and the root has the sharper depth r-s. -/
theorem actual_jacobian_bounded_inverse (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p])
    (hJ : IsUnit ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
      (fun i j => eval a (pderiv j (F i)))))
    (hbound : ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      (algebraMap ℤ_[p] ℚ_[p]).mapMatrix A = (p : ℚ_[p]) ^ s •
        ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix (fun i j => eval a (pderiv j (F i))))⁻¹)
    (hF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (F i)) :
    (∃! b : Fin d → ℤ_[p], (∀ i, eval b (F i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i)) ∧
    (∀ b : Fin d → ℤ_[p], (∀ i, eval b (F i) = 0) →
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) →
      ∀ i, (p : ℤ_[p]) ^ (r - s) ∣ b i - a i) :=
  PolynomialWeightedLift.exists_unique_weighted_root p s r hr F a hJ hbound hF

end Komorebi.PolynomialWeightedLiftContract
