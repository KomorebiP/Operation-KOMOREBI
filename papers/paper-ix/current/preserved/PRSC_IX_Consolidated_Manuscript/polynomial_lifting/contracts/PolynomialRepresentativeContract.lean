module
public import PolynomialRepresentative

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRepresentativeContract

/-- Both actual reduced Jacobians are identified with one map before comparing
the residual classes in its single quotient; no arbitrary presentation claim. -/
theorem explicit_representative_contract (d e q L : ℕ)
    (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x y : Fin d → ℤ)
    (hxy : ∀ i, (q : ℤ)^L ∣ y i - x i)
    (r r' : Fin e → ℤ)
    (hr : (fun i => MvPolynomial.eval x (F i)) = (q : ℤ)^L • r)
    (hr' : (fun i => MvPolynomial.eval y (F i)) = (q : ℤ)^L • r') :
    ∃ J : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ZMod q),
      NativeAffine.digitMap q (PolynomialObstruction.jacobian F x) = J ∧
      NativeAffine.digitMap q (PolynomialObstruction.jacobian F y) = J ∧
      (Submodule.Quotient.mk (fun i => (r' i : ZMod q)) :
        (Fin e → ZMod q) ⧸ LinearMap.range J) =
      Submodule.Quotient.mk (fun i => (r i : ZMod q)) :=
  PolynomialRepresentative.representative_independence q L hq hL F x y hxy r r' hr hr'

end Komorebi.PolynomialRepresentativeContract
