module
public import PolynomialPadicUnique

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialPadicUniqueContract

/-- Uniqueness concerns arbitrary actual roots in the ball, without a selected
integer lifting sequence or a hypothesis identifying either root with its limit. -/
theorem explicit_arbitrary_root_uniqueness (p L : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) {d : ℕ} (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin d =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k))
    (a b : Fin d → ℤ_[p])
    (ha : ∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0)
    (hb : ∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) b (F i) = 0)
    (hax : ∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) : a = b := by
  exact PolynomialPadicUnique.padic_root_unique p L hL F x hJ a b ha hb hax hbx

/-- Starting from the original polynomial lower-root congruence and the actual
reduced square Jacobian, both existence and uniqueness are conclusions. -/
theorem explicit_unique_padic_root (p L : ℕ) [Fact (Nat.Prime p)]
    (hL : 1 ≤ L) {d : ℕ} (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ MvPolynomial.eval x (F i))
    (hJ : Function.Surjective (fun t : Fin d → ZMod p => fun i : Fin d =>
      ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod p) * t k)) :
    ∃! a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  exact PolynomialPadicUnique.exists_unique_padic_root p L hL F x hx hJ

end Komorebi.PolynomialPadicUniqueContract
