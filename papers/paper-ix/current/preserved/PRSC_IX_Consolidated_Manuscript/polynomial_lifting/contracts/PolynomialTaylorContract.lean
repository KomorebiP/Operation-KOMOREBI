module
public import PolynomialTaylor

@[expose] public section
set_option autoImplicit false

namespace Komorebi.PolynomialTaylorContract

/-- The source polynomial, actual partial derivatives, all integer shifts,
and a divisible quadratic remainder appear explicitly in the contract. -/
theorem explicit_integral_taylor_contract (d : ℕ)
    (P : MvPolynomial (Fin d) ℤ) (x t : Fin d → ℤ) (a : ℤ) :
    a ^ 2 ∣ MvPolynomial.eval (fun i => x i + a * t i) P -
      MvPolynomial.eval x P -
      a * ∑ i, MvPolynomial.eval x (MvPolynomial.pderiv i P) * t i :=
  PolynomialTaylor.taylor_dvd P x t a

end Komorebi.PolynomialTaylorContract
