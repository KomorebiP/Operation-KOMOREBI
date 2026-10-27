import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Card

/-! Finite fixed-point bounds used by the source-facing Core 8.3 development.
Every strict increasing step adds a state; every strict decreasing step removes one.
No stabilization hypothesis is supplied by the caller. -/
namespace Komorebi.MachineTheory.FiniteFixedPoints

variable {X : Type*}

def sequence (f : Finset X → Finset X) (s : Finset X) : ℕ → Finset X
  | 0 => s
  | n + 1 => f (sequence f s n)

@[simp] theorem sequence_zero (f : Finset X → Finset X) (s : Finset X) :
    sequence f s 0 = s := rfl

@[simp] theorem sequence_succ (f : Finset X → Finset X) (s : Finset X) (n : ℕ) :
    sequence f s (n + 1) = f (sequence f s n) := rfl

/-- A genuinely computed inflationary sequence reaches a fixed point within the
number of states absent from the starting set. -/
theorem increasing_stabilization [Fintype X] (f : Finset X → Finset X)
    (s : Finset X) (hf : ∀ U, U ⊆ f U) :
    ∃ n ≤ Fintype.card X - s.card, f (sequence f s n) = sequence f s n := by
  classical
  by_contra h
  have hn : ∀ n, n ≤ Fintype.card X - s.card →
      f (sequence f s n) ≠ sequence f s n := by
    intro n hn he
    exact h ⟨n, hn, he⟩
  have growth : ∀ n, n ≤ Fintype.card X - s.card + 1 →
      s.card + n ≤ (sequence f s n).card := by
    intro n
    induction n with
    | zero => intro _; simp
    | succ n ih =>
      intro hbound
      have hnBound : n ≤ Fintype.card X - s.card := by omega
      have strict : sequence f s n ⊂ f (sequence f s n) :=
        Finset.ssubset_iff_subset_ne.mpr ⟨hf _, Ne.symm (hn n hnBound)⟩
      have hc := Finset.card_lt_card strict
      have hi := ih (by omega)
      simp only [sequence_succ]
      omega
  have final := growth (Fintype.card X - s.card + 1) (by omega)
  have upper := Finset.card_le_univ (sequence f s (Fintype.card X - s.card + 1))
  have initial := Finset.card_le_univ s
  omega

/-- A deflationary sequence reaches a fixed point in at most the initial number
of states. The ambient type need not be finite for this statement. -/
theorem decreasing_stabilization (f : Finset X → Finset X)
    (s : Finset X) (hf : ∀ U, f U ⊆ U) :
    ∃ n ≤ s.card, f (sequence f s n) = sequence f s n := by
  classical
  by_contra h
  have hn : ∀ n, n ≤ s.card → f (sequence f s n) ≠ sequence f s n := by
    intro n hn he
    exact h ⟨n, hn, he⟩
  have descent : ∀ n, n ≤ s.card + 1 →
      n + (sequence f s n).card ≤ s.card := by
    intro n
    induction n with
    | zero => intro _; simp
    | succ n ih =>
      intro hbound
      have hnBound : n ≤ s.card := by omega
      have strict : f (sequence f s n) ⊂ sequence f s n :=
        Finset.ssubset_iff_subset_ne.mpr ⟨hf _, hn n hnBound⟩
      have hc := Finset.card_lt_card strict
      have hi := ih (by omega)
      simp only [sequence_succ]
      omega
  have final := descent (s.card + 1) (by omega)
  omega

/-- Once the sequence is fixed it remains fixed, without a monotonicity premise. -/
theorem fixed_tail (f : Finset X → Finset X) (s : Finset X) (n : ℕ)
    (hn : f (sequence f s n) = sequence f s n) (k : ℕ) :
    sequence f s (n + k) = sequence f s n := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [Nat.add_succ, sequence_succ, ih, hn]

end Komorebi.MachineTheory.FiniteFixedPoints
