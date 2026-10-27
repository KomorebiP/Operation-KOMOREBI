module
public import PolynomialLocalInverse

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialHomeomorphContract
open MvPolynomial
variable {d : ℕ}

/-- The homeomorphism is the actual polynomial map, and its inverse solves every output. -/
theorem square_homeomorphism (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (fun u : Fin d → ZMod p => fun i =>
      ∑ j, (eval x (pderiv j (F i)) : ZMod p) * u j)) :
    ∃ h : {a : Fin d → ℤ_[p] // ∀ j, (p : ℤ_[p])^L ∣ a j - (x j : ℤ_[p])} ≃ₜ
      {t : Fin d → ℤ_[p] // ∀ i, (p : ℤ_[p])^L ∣ t i - (eval x (F i) : ℤ_[p])},
      (∀ a i, (h a).val i = eval₂ (Int.castRingHom ℤ_[p]) a.val (F i)) ∧
      (∀ t i, eval₂ (Int.castRingHom ℤ_[p]) (h.symm t).val (F i) = t.val i) ∧
      (∀ N t u, (∀ i, (p : ℤ_[p])^N ∣ t.val i - u.val i) →
        ∀ j, (p : ℤ_[p])^N ∣ (h.symm t).val j - (h.symm u).val j) := by
  refine ⟨PolynomialLocalInverse.localHomeomorph p L hL F x hJ, ?_, ?_, ?_⟩
  · intro a i
    rfl
  · intro t i
    exact congrFun (PolynomialLocalInverse.localHomeomorph_symm_eval p L hL F x hJ t) i
  · intro N t u htu
    exact PolynomialLocalInverse.localHomeomorph_symm_congruent p L N hL F x hJ t u htu

end Komorebi.PolynomialHomeomorphContract
