module
public import PolynomialObstruction

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialObstructionContract

/-- Actual integer representatives and polynomial evaluations, including the
finite quotient and its zero residual class, appear in the external contract. -/
theorem explicit_finite_polynomial_contract (d e q L : ℕ)
    (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ MvPolynomial.eval x (F i)) :
    ∃ r : Fin e → ℤ,
      (fun i => MvPolynomial.eval x (F i)) = (q : ℤ)^L • r ∧
      Finite ((Fin e → ZMod q) ⧸
        LinearMap.range (NativeAffine.digitMap q (PolynomialObstruction.jacobian F x))) ∧
      ((∃ y : Fin d → ℤ,
        (∀ i, (q : ℤ)^L ∣ y i - x i) ∧
        (∀ i, (q : ℤ)^(L+1) ∣ MvPolynomial.eval y (F i))) ↔
          (Submodule.Quotient.mk (fun i => (r i : ZMod q)) :
            (Fin e → ZMod q) ⧸ LinearMap.range
              (NativeAffine.digitMap q (PolynomialObstruction.jacobian F x))) = 0) :=
  PolynomialObstruction.finite_polynomial_obstruction q L hq hL F x hx

end Komorebi.PolynomialObstructionContract
