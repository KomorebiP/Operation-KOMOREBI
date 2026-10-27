import Komorebi.Foundation.ResidualClassification

/-!
# A uniform obstruction at every infinite successor cardinal

Use one variable for every element of mu^+ and require distinct variables to receive
distinct values in a fixed set of size mu. Every fewer-than-mu^+ collection of binary
constraints is satisfiable, while a global solution would be an impossible injection.
-/

universe u

namespace Komorebi.CompactnessClassification

open Set Filter
open FineUltrafilterCompactness

/-- Fixed-domain compactness fails at every successor of an infinite cardinal.
This is an explicit infinite-family counterexample, not a test over finite instances. -/
theorem not_fixedDomain_successor (μ : Cardinal.{u}) (hμ : Cardinal.aleph0 ≤ μ) :
    ¬ FixedDomainCompactness (Order.succ μ) := by
  classical
  intro hc
  let V := (Order.succ μ).out
  let A := μ.out
  let I := V × V
  let scope : I → Set V := fun i => {i.1, i.2}
  let satisfies : I → (V → A) → Prop := fun i a => i.1 ≠ i.2 → a i.1 ≠ a i.2
  have hreg : (Order.succ μ).IsRegular := Cardinal.isRegular_succ hμ
  have hA : Cardinal.mk A < Order.succ μ := by
    simp [A]
  have hscope : ∀ i, Cardinal.mk (scope i) < Order.succ μ := by
    intro i
    exact ((Set.finite_singleton i.2).insert i.1).lt_aleph0.trans_le hreg.aleph0_le
  have hlocal : ∀ J : SmallPieces (Order.succ μ) I,
      ∃ a : V → A, ∀ i ∈ J.val, satisfies i a := by
    intro J
    let S : Set V := ⋃ j : J.val, scope j.val
    have hS : Cardinal.mk S < Order.succ μ :=
      (Cardinal.card_iUnion_lt_iff_forall_of_isRegular hreg J.property).mpr
        (fun j => hscope j.val)
    have hSA : Cardinal.mk S ≤ Cardinal.mk A := by
      simpa [A] using (Order.lt_succ_iff.mp hS)
    obtain ⟨e⟩ := (Cardinal.le_def S A).mp hSA
    have hne : Nonempty A := Cardinal.nonempty_out (ne_of_gt (Cardinal.aleph0_pos.trans_le hμ))
    let a0 : A := Classical.choice hne
    let a : V → A := fun v => if hv : v ∈ S then e ⟨v, hv⟩ else a0
    refine ⟨a, ?_⟩
    intro i hi hne heq
    have hv : i.1 ∈ S := Set.mem_iUnion.mpr ⟨⟨i, hi⟩, by simp [scope]⟩
    have hw : i.2 ∈ S := Set.mem_iUnion.mpr ⟨⟨i, hi⟩, by simp [scope]⟩
    have he : e ⟨i.1, hv⟩ = e ⟨i.2, hw⟩ := by simpa [a, hv, hw] using heq
    exact hne (congrArg Subtype.val (e.injective he))
  obtain ⟨a, ha⟩ := hc I V A hA scope hscope satisfies
    (by
      intro i a b hagree hi hne heq
      apply hi hne
      rw [hagree i.1 (by simp [scope]), hagree i.2 (by simp [scope])]
      exact heq)
    hlocal
  have hinj : Function.Injective a := by
    intro v w heq
    by_contra hne
    exact ha (v, w) hne heq
  have hle : Order.succ μ ≤ μ := by
    simpa [V, A] using Cardinal.mk_le_of_injective hinj
  exact (Order.lt_succ μ).not_ge hle

/-- The classified residual principle likewise fails at every infinite successor. -/
theorem not_krr_successor (μ : Cardinal.{u}) (hμ : Cardinal.aleph0 ≤ μ) :
    ¬ FixedDomainKRR (Order.succ μ) := by
  intro hk
  exact not_fixedDomain_successor μ hμ
    ((krr0_iff_fixedDomain _).mp ((krr_iff_krr0 _).mp hk))

/-- Independent filter-language consequence of the explicit constraint obstruction. -/
theorem not_extension_successor (μ : Cardinal.{u}) (hμ : Cardinal.aleph0 ≤ μ) :
    ¬ CompleteFilterExtension (Order.succ μ) := by
  intro he
  exact not_fixedDomain_successor μ hμ
    ((fixedDomain_iff_extension _ (Cardinal.isRegular_succ hμ)).mpr he)

end Komorebi.CompactnessClassification
