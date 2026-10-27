module
public import PolynomialGeneralChart

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.PolynomialGeneralChartContract
open MvPolynomial
variable {e q : ℕ}

/-- No chosen minor, unspecified equation, or assumed root function occurs in this contract. -/
theorem full_rectangular_chart (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ eval x (F i))
    (hJ : Function.Surjective (fun u : Fin (e + q) → ZMod p => fun i =>
      ∑ j, (eval x (pderiv j (F i)) : ZMod p) * u j)) :
    ∃ σ : Equiv.Perm (Fin (e + q)),
    ∃ h : {t : Fin q → ℤ_[p] //
          ∀ j, (p : ℤ_[p])^L ∣ t j - (x (σ (Fin.natAdd e j)) : ℤ_[p])} ≃ₜ
        {z : {a : Fin (e + q) → ℤ_[p] //
          ∀ j, (p : ℤ_[p])^L ∣ a j - (x j : ℤ_[p])} //
          (fun i => eval₂ (Int.castRingHom ℤ_[p]) z.val (F i)) = 0},
      (∀ z j, (h.symm z).val j = z.val.val (σ (Fin.natAdd e j))) ∧
      (∀ N t u,
        (∀ j, (p : ℤ_[p])^N ∣ t.val j - u.val j) ↔
        (∀ i, (p : ℤ_[p])^N ∣ (h t).val.val i - (h u).val.val i)) := by
  obtain ⟨σ, h, hproj, hcong⟩ :=
    PolynomialGeneralChart.exists_parameter_homeomorph p L hL F x hx hJ
  refine ⟨σ, h, ?_, hcong⟩
  intro z j
  exact congrFun (hproj z) j

end Komorebi.PolynomialGeneralChartContract
