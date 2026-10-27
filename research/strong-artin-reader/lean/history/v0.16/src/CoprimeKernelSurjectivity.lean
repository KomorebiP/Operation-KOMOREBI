import Mathlib.GroupTheory.Index
import Mathlib.GroupTheory.PGroup

namespace Komorebi.StrongArtin.CoprimeKernelSurjectivity

noncomputable section

variable {G Γ P : Type*} [Group G] [Group Γ] [Group P]

/-- If a residual quotient has order coprime to the order of an auxiliary label
group, then imposing trivial auxiliary label does not lose any residual class. -/
theorem map_ker_eq_top_of_coprime_card
    [Finite Γ] [Finite P]
    (q : G →* Γ) (a : G →* P)
    (hq : Function.Surjective q)
    (hcop : Nat.Coprime (Nat.card Γ) (Nat.card P)) :
    a.ker.map q = ⊤ := by
  apply Subgroup.index_eq_one.mp
  apply Nat.eq_one_of_dvd_coprimes hcop
  · exact (a.ker.map q).index_dvd_card
  · exact (Subgroup.index_map_dvd (H := a.ker) hq).trans (by
      rw [Subgroup.index_ker]
      exact a.range.card_subgroup_dvd_card)

/-- Every residual element has a lift satisfying the auxiliary splitting label. -/
theorem exists_lift_in_ker_of_coprime_card
    [Finite Γ] [Finite P]
    (q : G →* Γ) (a : G →* P)
    (hq : Function.Surjective q)
    (hcop : Nat.Coprime (Nat.card Γ) (Nat.card P))
    (γ : Γ) :
    ∃ g : G, q g = γ ∧ a g = 1 := by
  have htop := map_ker_eq_top_of_coprime_card q a hq hcop
  have hmem : γ ∈ a.ker.map q := by
    rw [htop]
    exact Subgroup.mem_top γ
  rcases hmem with ⟨g, hg, hqg⟩
  refine ⟨g, hqg, ?_⟩
  exact (MonoidHom.mem_ker.mp hg)

/-- Prime-power specialization: a `p`-group splitting/cyclotomic label can be
imposed without losing residual classes whenever the residual quotient has
order prime to `p`. -/
theorem map_ker_eq_top_of_pGroup_label
    {p : ℕ} [Fact p.Prime]
    [Finite Γ] [Finite P]
    (hP : IsPGroup p P)
    (q : G →* Γ) (a : G →* P)
    (hq : Function.Surjective q)
    (hpΓ : ¬ p ∣ Nat.card Γ) :
    a.ker.map q = ⊤ := by
  obtain ⟨m, hPm⟩ := hP.exists_card_dvd_pow
  have hcoppow : Nat.Coprime (Nat.card Γ) (p ^ m) :=
    (Fact.out : Nat.Prime p).coprime_pow_of_not_dvd hpΓ
  have hcop : Nat.Coprime (Nat.card Γ) (Nat.card P) :=
    hcoppow.coprime_dvd_right hPm
  exact map_ker_eq_top_of_coprime_card q a hq hcop

/-- Elementwise prime-power specialization. -/
theorem exists_lift_in_pGroup_kernel
    {p : ℕ} [Fact p.Prime]
    [Finite Γ] [Finite P]
    (hP : IsPGroup p P)
    (q : G →* Γ) (a : G →* P)
    (hq : Function.Surjective q)
    (hpΓ : ¬ p ∣ Nat.card Γ)
    (γ : Γ) :
    ∃ g : G, q g = γ ∧ a g = 1 := by
  have htop := map_ker_eq_top_of_pGroup_label hP q a hq hpΓ
  have hmem : γ ∈ a.ker.map q := by
    rw [htop]
    exact Subgroup.mem_top γ
  rcases hmem with ⟨g, hg, hqg⟩
  exact ⟨g, hqg, MonoidHom.mem_ker.mp hg⟩

end
end Komorebi.StrongArtin.CoprimeKernelSurjectivity

#print axioms Komorebi.StrongArtin.CoprimeKernelSurjectivity.map_ker_eq_top_of_coprime_card
#print axioms Komorebi.StrongArtin.CoprimeKernelSurjectivity.exists_lift_in_ker_of_coprime_card
#print axioms Komorebi.StrongArtin.CoprimeKernelSurjectivity.map_ker_eq_top_of_pGroup_label
#print axioms Komorebi.StrongArtin.CoprimeKernelSurjectivity.exists_lift_in_pGroup_kernel
