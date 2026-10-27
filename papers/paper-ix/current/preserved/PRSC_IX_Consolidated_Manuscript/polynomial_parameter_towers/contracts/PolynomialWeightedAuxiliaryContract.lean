module
public import PolynomialTaylorRing
public import PolynomialPadicContraction
public import PolynomialWeightedInverse

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialWeightedAuxiliaryContract
open MvPolynomial
variable {d : ℕ}

/-- The remainder is a single actual polynomial, uniform over every input. -/
theorem uniform_polynomial_taylor {R : Type*} [CommRing R]
    (P : MvPolynomial (Fin d) R) (a : Fin d → R) (c : R) :
    ∃ Q : MvPolynomial (Fin d) R,
      (∀ u : Fin d → R, eval (fun i => a i + c * u i) P =
        eval a P + c * (∑ i, eval a (pderiv i P) * u i) + c ^ 2 * eval u Q) ∧
      eval (0 : Fin d → R) Q = 0 :=
  PolynomialTaylorRing.exists_eval_scaled_remainder P a c

/-- Arbitrary integral p-adic coefficients require no assumed Lipschitz estimate. -/
theorem actual_polynomial_contraction (p : ℕ) [Fact p.Prime]
    (H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (c : Fin d → ℤ_[p]) :
    ∃! u : Fin d → ℤ_[p],
      (fun i => c i + (p : ℤ_[p]) * eval u (H i)) = u :=
  PolynomialPadicContraction.exists_unique_fixedPoint p H c

/-- The denominator exponent is preserved exactly in the integral translation. -/
theorem exact_inverse_denominator_certificate (p s : ℕ) [Fact p.Prime]
    (J : Matrix (Fin d) (Fin d) ℤ_[p]) :
    (IsUnit ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix J) ∧
      ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
        (algebraMap ℤ_[p] ℚ_[p]).mapMatrix A =
          (p : ℚ_[p]) ^ s • ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix J)⁻¹) ↔
    (∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      A * J = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]) ∧
      J * A = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p])) :=
  PolynomialWeightedInverse.bounded_inverse_iff_certificate p s J

end Komorebi.PolynomialWeightedAuxiliaryContract
