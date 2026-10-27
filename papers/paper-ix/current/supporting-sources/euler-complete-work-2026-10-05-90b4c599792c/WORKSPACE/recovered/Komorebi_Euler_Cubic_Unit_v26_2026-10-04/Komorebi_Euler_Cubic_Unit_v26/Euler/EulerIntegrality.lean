module
public import Euler.EulerSequence
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Every even Euler coefficient is an ordinary integer, proved by the recurrence. -/
theorem signedEulerRat_even_integer (N : ℕ) :
    ∃ z : ℤ, signedEulerRat (2*N)=(z:ℚ) := by
  induction N using Nat.strong_induction_on with
  | h N ih =>
    cases N with
    | zero => exact ⟨1, by simp⟩
    | succ n =>
      have hex : ∀ m : Fin (n+1), ∃ z:ℤ, signedEulerRat (2*(m:ℕ))=(z:ℚ) := by
        intro m
        exact ih m (by simpa using m.isLt)
      choose z hz using hex
      refine ⟨-(∑ m : Fin (n+1), ((2*(n+1)).choose (2*(m:ℕ)):ℤ)*z m), ?_⟩
      rw [signedEulerRat_even_succ]
      push_cast
      congr 1
      rw [← Fin.sum_univ_eq_sum_range]
      apply Finset.sum_congr rfl
      intro m _
      rw [hz m]

/-- Integrality of the independent signed Euler sequence at every index, including odd zeros. -/
theorem signedEulerRat_integer (n : ℕ) : ∃ z:ℤ, signedEulerRat n=(z:ℚ) := by
  rcases Nat.even_or_odd n with hn | hn
  · obtain ⟨m,hm⟩ := hn
    rw [show n=2*m by omega]
    exact signedEulerRat_even_integer m
  · obtain ⟨m,hm⟩ := hn
    rw [hm]
    exact ⟨0,by simp⟩

end Komorebi.Euler
