import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Choose

/-! One common correction for a family of powers of an endomorphism.
The pivot formula is valid without nilpotence or finite dimension. -/
noncomputable section
namespace Komorebi.StrongArtin.SimultaneousNorm
variable {k V I : Type*} [Field k] [AddCommGroup V] [Module k V]

/-- The sign of the independent local variables is immaterial. -/
def PowerFamilySolvable (N : Module.End k V) (r : I → ℕ) (e : I → V) : Prop :=
  ∃ x : V, ∃ z : I → V, ∀ i, e i = (N ^ r i) (x + N (z i))

theorem pow_difference_apply (N : Module.End k V) {a b : ℕ} (hab : a ≤ b)
    (x : V) : (N ^ (b-a)) ((N^a) x) = (N^b) x := by
  rw [← Module.End.mul_apply, ← pow_add, Nat.sub_add_cancel hab]

theorem pow_succ_apply (N : Module.End k V) (n : ℕ) (x : V) :
    (N^n) (N x) = (N^(n+1)) x := by
  rw [pow_succ, Module.End.mul_apply]

/-- Exact simultaneous criterion. Individual roots alone do not suffice. -/
theorem powerFamily_iff_pivot (N : Module.End k V) (r : I → ℕ) (e : I → V)
    (i₀ : I) (hmin : ∀ i, r i₀ ≤ r i) :
    PowerFamilySolvable N r e ↔
      e i₀ ∈ LinearMap.range (N ^ r i₀) ∧
      ∀ i, e i - (N ^ (r i - r i₀)) (e i₀) ∈
        LinearMap.range (N ^ (r i + 1)) := by
  constructor
  · rintro ⟨x, z, hz⟩
    refine ⟨⟨x + N (z i₀), (hz i₀).symm⟩, ?_⟩
    intro i
    refine ⟨z i - z i₀, ?_⟩
    rw [hz i, hz i₀, pow_difference_apply N (hmin i)]
    simp only [map_add, map_sub, pow_succ_apply]
    abel
  · rintro ⟨⟨x, hx⟩, he⟩
    choose z hz using he
    refine ⟨x, z, ?_⟩
    intro i
    have hi := hz i
    rw [← hx, pow_difference_apply N (hmin i)] at hi
    rw [map_add, pow_succ_apply]
    exact (eq_sub_iff_add_eq.mp hi).symm.trans (add_comm _ _)

/-- The pivot criterion already implies individual image membership. -/
theorem powerFamily_individually (N : Module.End k V) (r : I → ℕ) (e : I → V)
    (h : PowerFamilySolvable N r e) (i : I) :
    e i ∈ LinearMap.range (N ^ r i) := by
  obtain ⟨x, z, hz⟩ := h
  exact ⟨x + N (z i), (hz i).symm⟩

/-- Explicit obstruction certificate relative to any least-exponent pivot. -/
theorem not_powerFamily_of_pivot_difference (N : Module.End k V)
    (r : I → ℕ) (e : I → V) (i₀ i : I) (hmin : ∀ j, r i₀ ≤ r j)
    (hbad : e i - (N ^ (r i - r i₀)) (e i₀) ∉
      LinearMap.range (N ^ (r i + 1))) :
    ¬ PowerFamilySolvable N r e := by
  intro h
  exact hbad (((powerFamily_iff_pivot N r e i₀ hmin).mp h).2 i)

/-- Empty families are genuinely vacuous. -/
theorem powerFamily_empty (N : Module.End k V) (r : I → ℕ) (e : I → V)
    [IsEmpty I] : PowerFamilySolvable N r e := by
  exact ⟨0, fun _ => 0, fun i => isEmptyElim i⟩

/-- Natural-number exponents always admit a least pivot on a nonempty family. -/
theorem exists_least_exponent [Nonempty I] (r : I → ℕ) :
    ∃ i₀, ∀ i, r i₀ ≤ r i := by
  classical
  let j : I := Classical.choice inferInstance
  have hex : ∃ n : ℕ, ∃ i : I, r i = n := ⟨r j,j,rfl⟩
  obtain ⟨i₀,hi₀⟩ := Nat.find_spec hex
  refine ⟨i₀,fun i => ?_⟩
  rw [hi₀]
  exact Nat.find_min' hex ⟨i,rfl⟩

/-- Special nested-filtration Helly property: matching each pair with the pivot
suffices. This is not asserted for arbitrary global-to-local maps. -/
theorem powerFamily_iff_pivot_pairs (N : Module.End k V) (r : I → ℕ) (e : I → V)
    (i₀ : I) (hmin : ∀ i, r i₀ ≤ r i) :
    PowerFamilySolvable N r e ↔
      ∀ i, ∃ x z₀ zᵢ : V,
        e i₀ = (N^r i₀) (x+N z₀) ∧ e i = (N^r i) (x+N zᵢ) := by
  constructor
  · rintro ⟨x,z,hz⟩ i
    exact ⟨x,z i₀,z i,hz i₀,hz i⟩
  · intro h
    apply (powerFamily_iff_pivot N r e i₀ hmin).mpr
    constructor
    · obtain ⟨x,z₀,zᵢ,h₀,_⟩ := h i₀
      exact ⟨x+N z₀,h₀.symm⟩
    · intro i
      obtain ⟨x,z₀,zᵢ,h₀,hᵢ⟩ := h i
      refine ⟨zᵢ-z₀,?_⟩
      rw [hᵢ,h₀,pow_difference_apply N (hmin i)]
      simp only [map_add,map_sub,pow_succ_apply]
      abel

end Komorebi.StrongArtin.SimultaneousNorm
