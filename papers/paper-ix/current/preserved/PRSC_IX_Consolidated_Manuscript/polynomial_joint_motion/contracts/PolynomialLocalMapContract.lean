module
public import PolynomialLocalSurjective
public import PolynomialInverseCongruence

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialLocalMapContract
open MvPolynomial
variable {d e : ℕ}

/-- Expanded actual derivative and evaluation contract for arbitrary p-adic output targets. -/
theorem arbitrary_padic_target (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (fun u : Fin d → ZMod p => fun i =>
      ∑ j, (eval x (pderiv j (F i)) : ZMod p) * u j))
    (t : Fin e → ℤ_[p])
    (ht : ∀ i, (p : ℤ_[p])^L ∣ t i - (eval x (F i) : ℤ_[p])) :
    ∃ a : Fin d → ℤ_[p],
      (∀ i, eval₂ (Int.castRingHom ℤ_[p]) a (F i) = t i) ∧
      ∀ j, (p : ℤ_[p])^L ∣ a j - (x j : ℤ_[p]) := by
  obtain ⟨a, ha, hax⟩ := PolynomialLocalSurjective.exists_padic_preimage p L hL F x hJ t ht
  exact ⟨a, fun i => congrFun ha i, hax⟩

/-- On one nonsingular square residue class every depth of precision is reflected. -/
theorem all_depths_reflected (p N : ℕ) [Fact (Nat.Prime p)]
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (fun u : Fin d → ZMod p => fun i =>
      ∑ j, (eval x (pderiv j (F i)) : ZMod p) * u j))
    (a b : Fin d → ℤ_[p])
    (ha : ∀ j, (p : ℤ_[p]) ∣ a j - (x j : ℤ_[p]))
    (hb : ∀ j, (p : ℤ_[p]) ∣ b j - (x j : ℤ_[p])) :
    (∀ i, (p : ℤ_[p])^N ∣
      eval₂ (Int.castRingHom ℤ_[p]) a (F i) - eval₂ (Int.castRingHom ℤ_[p]) b (F i)) ↔
    (∀ j, (p : ℤ_[p])^N ∣ a j - b j) :=
  PolynomialInverseCongruence.padic_congruence_iff p N F x hJ a b ha hb

end Komorebi.PolynomialLocalMapContract
