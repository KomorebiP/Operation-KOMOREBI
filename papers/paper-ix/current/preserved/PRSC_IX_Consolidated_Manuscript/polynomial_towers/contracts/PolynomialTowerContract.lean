module
public import PolynomialIntegerTower

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialTowerContract

/-- One initial surjectivity hypothesis produces one sequence at all depths;
no preselected per-level roots, surjectivity assumptions, or compatibility are inputs. -/
theorem explicit_polynomial_tower (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    {d e : ℕ} (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hJ : Function.Surjective (PolynomialDigitBridge.digitJacobian q F x)) :
    ∃ z : ℕ → Fin d → ℤ,
      z 0 = x ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ MvPolynomial.eval (z n) (F i)) ∧
      (∀ n i, (q : ℤ)^(L+n) ∣ z (n+1) i - z n i) ∧
      (∀ m n, m ≤ n → ∀ i, (q : ℤ)^(L+m) ∣ z n i - z m i) ∧
      (∀ n, PolynomialDigitBridge.digitJacobian q F (z n) =
        PolynomialDigitBridge.digitJacobian q F x) ∧
      (∀ n, Function.Surjective (PolynomialDigitBridge.digitJacobian q F (z n))) := by
  exact PolynomialIntegerTower.exists_compatible_tower_strong q L hq hL F x hx hJ

/-- The actual Jacobian map is evaluated from formal polynomial derivatives. -/
theorem explicit_jacobian (q : ℕ) {d e : ℕ}
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (t : Fin d → ZMod q) (i : Fin e) :
    PolynomialDigitBridge.digitJacobian q F x t i =
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod q) * t k := rfl

end Komorebi.PolynomialTowerContract
