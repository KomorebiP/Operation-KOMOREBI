module
public import PolynomialPadicLift

@[expose] public section
noncomputable section
set_option autoImplicit false
open Filter Topology
namespace Komorebi.PolynomialPadicLiftContract

/-- The root theorem with original polynomial evaluation and the full formal
Jacobian formula expanded. There is exactly one initial surjectivity hypothesis. -/
theorem explicit_padic_root (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    {d e : ℕ} (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin e =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k)) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  exact PolynomialPadicLift.exists_padic_root p L hL F x hx hJ

/-- The same initial data give an actual convergent sequence, every retained
precision, the exact root, the fixed reduced Jacobian, and all finite lift counts. -/
theorem explicit_padic_root_with_tower (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    {d e : ℕ} (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin e =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k)) :
    ∃ z : ℕ → Fin d → ℤ, ∃ a : Fin d → ℤ_[p],
      z 0 = x ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ MvPolynomial.eval (z n) (F i)) ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ z (n+1) i - z n i) ∧
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 a) ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ a i - (z n i : ℤ_[p])) ∧
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0) ∧
      (∀ n, PolynomialDigitBridge.digitJacobian p F (z n) =
        PolynomialDigitBridge.digitJacobian p F x) ∧
      (∀ n, Nat.card (PolynomialLiftCounts.ActualLifts p (L+n) F (z n)) = p^(d-e)) := by
  exact PolynomialPadicLift.exists_padic_root_with_tower p L hL F x hx hJ

end Komorebi.PolynomialPadicLiftContract
