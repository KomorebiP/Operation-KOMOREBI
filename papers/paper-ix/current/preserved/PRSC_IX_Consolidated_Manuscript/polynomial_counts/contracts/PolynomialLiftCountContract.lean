module
public import PolynomialLiftCounts

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped Classical
namespace Komorebi.PolynomialLiftCountContract

/-- Full polynomial count contract: the lower solution is explicit, the counted
objects are actual next-level residue classes, and the rank is the Jacobian's. -/
theorem explicit_actual_polynomial_count (p L : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) {d e : ℕ} (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ MvPolynomial.eval x (F i)) :
    ∃ r : Fin e → ℤ,
      (∀ i, MvPolynomial.eval x (F i) = (p : ℤ)^L * r i) ∧
      Nat.card {y : {y : Fin d → ZMod (p^(L+1)) //
        ∀ k, (p : ℤ)^L ∣ ((y k).val : ℤ) - x k} //
        ∀ i, (p : ℤ)^(L+1) ∣
          MvPolynomial.eval (fun k => ((y.val k).val : ℤ)) (F i)} =
        (if NativeAffine.obstruction p (PolynomialObstruction.jacobian F x) r = 0 then
          p ^ (d - Module.finrank (ZMod p)
            (PolynomialDigitBridge.digitJacobian p F x).range) else 0) ∧
      Nat.card (NativeAffine.Obstruction p (PolynomialObstruction.jacobian F x)) =
        p ^ (e - Module.finrank (ZMod p)
          (PolynomialDigitBridge.digitJacobian p F x).range) := by
  obtain ⟨r, hr, hc, ho⟩ :=
    PolynomialLiftCounts.finite_polynomial_lift_count p L hL F x hx
  exact ⟨r, fun i => congrFun hr i, hc, ho⟩

/-- The map whose range defines the rank is the evaluated formal Jacobian. -/
theorem explicit_jacobian_formula (p : ℕ) {d e : ℕ}
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (t : Fin d → ZMod p) (i : Fin e) :
    PolynomialDigitBridge.digitJacobian p F x t i =
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k := rfl

end Komorebi.PolynomialLiftCountContract
