import Mathlib.Order.Preorder.Finite
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Data.Fintype.Pi
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-!
# Finite Pareto reduction

Only nondominated profiles are retained. The lower cofinality theorem, rather
than independent minimization of coordinates, is the preservation invariant.
-/
namespace Komorebi.MachineTheory.HardPareto

variable {P : Type*} [PartialOrder P]

noncomputable def frontier (s : Finset P) : Finset P := by
  classical
  exact s.filter (fun p => ∀ q ∈ s, q ≤ p → p ≤ q)

@[simp] theorem mem_frontier (s : Finset P) (p : P) :
    p ∈ frontier s ↔ p ∈ s ∧ ∀ q ∈ s, q ≤ p → p ≤ q := by
  classical
  simp [frontier]

theorem frontier_subset (s : Finset P) : frontier s ⊆ s :=
  fun p hp => ((mem_frontier s p).mp hp).1

/-- Every discarded profile is weakly dominated by a retained one. -/
theorem exists_frontier_le (s : Finset P) {p : P} (hp : p ∈ s) :
    ∃ q ∈ frontier s, q ≤ p := by
  obtain ⟨q, hqp, hq, hmin⟩ := s.exists_le_minimal hp
  exact ⟨q, (mem_frontier s q).mpr ⟨hq, hmin⟩, hqp⟩

theorem budget_iff (s : Finset P) (b : P) :
    (∃ p ∈ s, p ≤ b) ↔ ∃ p ∈ frontier s, p ≤ b := by
  constructor
  · rintro ⟨p, hp, hb⟩
    obtain ⟨q, hq, hqp⟩ := exists_frontier_le s hp
    exact ⟨q, hq, hqp.trans hb⟩
  · rintro ⟨p, hp, hb⟩
    exact ⟨p, frontier_subset s hp, hb⟩

/-- A finite sound lower-cofinal subset has exactly the same minimal profiles. -/
theorem frontier_characterization (s : Finset P) (T : Set P)
    (sound : ∀ p ∈ s, p ∈ T)
    (complete : ∀ p ∈ T, ∃ q ∈ s, q ≤ p) (p : P) :
    p ∈ frontier s ↔ p ∈ T ∧ ∀ q ∈ T, q ≤ p → p ≤ q := by
  constructor
  · intro hp
    obtain ⟨hs, hm⟩ := (mem_frontier s p).mp hp
    refine ⟨sound p hs, ?_⟩
    intro q hq hqp
    obtain ⟨r, hr, hrq⟩ := complete q hq
    exact (hm r hr (hrq.trans hqp)).trans hrq
  · rintro ⟨hp, hm⟩
    obtain ⟨q, hq, hqp⟩ := complete p hp
    have he : p = q := le_antisymm (hm q (sound q hq) hqp) hqp
    refine (mem_frontier s p).mpr ⟨he ▸ hq, ?_⟩
    intro r hr hrp
    exact hm r (sound r hr) hrp

end Komorebi.MachineTheory.HardPareto
