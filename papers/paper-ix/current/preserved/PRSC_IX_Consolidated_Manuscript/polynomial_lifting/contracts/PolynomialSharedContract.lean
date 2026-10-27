module
public import PolynomialShared

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialSharedContract

/-- A common integer representative, both polynomial blocks, and the explicit
sum-of-kernels quotient are exposed without an assumed compatibility premise. -/
theorem explicit_shared_polynomial_contract (d e f q L : ℕ)
    (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hxF : ∀ i, (q : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hxG : ∀ i, (q : ℤ)^L ∣ MvPolynomial.eval x (G i)) :
    Finite ((Fin d → ℤ) ⧸
      (LinearMap.ker (NativeAffine.digitMap q (PolynomialObstruction.jacobian F x)) ⊔
        LinearMap.ker (NativeAffine.digitMap q (PolynomialObstruction.jacobian G x)))) ∧
      ((∃ y : Fin d → ℤ,
        (∀ i, (q : ℤ)^L ∣ y i - x i) ∧
        (∀ i, (q : ℤ)^(L+1) ∣ MvPolynomial.eval y (F i)) ∧
        (∀ i, (q : ℤ)^(L+1) ∣ MvPolynomial.eval y (G i))) ↔
        ∃ u v : Fin d → ℤ,
          (∀ i, (q : ℤ)^(L+1) ∣
            MvPolynomial.eval (fun k => x k + (q : ℤ)^L * u k) (F i)) ∧
          (∀ i, (q : ℤ)^(L+1) ∣
            MvPolynomial.eval (fun k => x k + (q : ℤ)^L * v k) (G i)) ∧
          (Submodule.Quotient.mk u : (Fin d → ℤ) ⧸
            (LinearMap.ker (NativeAffine.digitMap q (PolynomialObstruction.jacobian F x)) ⊔
              LinearMap.ker (NativeAffine.digitMap q (PolynomialObstruction.jacobian G x)))) =
            Submodule.Quotient.mk v) :=
  PolynomialShared.finite_polynomial_pair_compatibility q L hq hL F G x hxF hxG

end Komorebi.PolynomialSharedContract
