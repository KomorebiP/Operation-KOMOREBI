import Mathlib.Data.Nat.Init
import Lean.Elab.Tactic.Omega

/-!
# Generic descending first-true search

This module implements a right-to-left Boolean search with exact accounting.
If the lowest tested point is certified true, the result is the greatest true
index in the interval and `tested` is exactly the number of predicates evaluated.
No monotonicity hypothesis is required: every larger index is inspected before
termination.
-/

namespace KomorebiPadic

/-- Result of a bounded descending first-true search. -/
structure FirstTrueDescendingResult where
  value : ℕ
  tested : ℕ
  deriving Repr, DecidableEq

/-- Search `fuel` consecutive indices downward, beginning at `upper`.
If no true value occurs, the total fallback is the predecessor of the final
inspected index.  The correctness theorem rules this fallback out by requiring
the lowest inspected point to be true. -/
def firstTrueDescendingAux (pred : ℕ → Bool) : ℕ → ℕ → FirstTrueDescendingResult
  | upper, 0 => ⟨upper, 0⟩
  | upper, fuel + 1 =>
      if pred upper then
        ⟨upper, 1⟩
      else
        let out := firstTrueDescendingAux pred (upper - 1) fuel
        ⟨out.value, out.tested + 1⟩

/-- Exact specification of a successful descending first-true search. -/
def FirstTrueDescendingSpec
    (pred : ℕ → Bool) (lower upper : ℕ)
    (out : FirstTrueDescendingResult) : Prop :=
  lower ≤ out.value ∧
  out.value ≤ upper ∧
  pred out.value = true ∧
  (∀ i : ℕ, out.value < i → i ≤ upper → pred i = false) ∧
  out.tested = upper - out.value + 1

/-- A true lowest point makes the bounded descending search exact. -/
theorem firstTrueDescendingAux_spec
    (pred : ℕ → Bool) {upper fuel : ℕ}
    (hfuel : 0 < fuel)
    (hfit : fuel ≤ upper + 1)
    (hterminal : pred (upper + 1 - fuel) = true) :
    FirstTrueDescendingSpec pred (upper + 1 - fuel) upper
      (firstTrueDescendingAux pred upper fuel) := by
  induction fuel generalizing upper with
  | zero => omega
  | succ fuel ih =>
      cases hpred : pred upper with
      | true =>
          simp [firstTrueDescendingAux, hpred, FirstTrueDescendingSpec]
          omega
      | false =>
          cases fuel with
          | zero =>
              have hterminal' : pred upper = true := by
                simpa using hterminal
              rw [hpred] at hterminal'
              contradiction
          | succ fuel =>
              have hupper : 0 < upper := by omega
              have hlowerEq :
                  upper + 1 - (fuel + 1 + 1) =
                    (upper - 1) + 1 - (fuel + 1) := by
                omega
              have hterminal' :
                  pred ((upper - 1) + 1 - (fuel + 1)) = true := by
                rw [← hlowerEq]
                exact hterminal
              let out := firstTrueDescendingAux pred (upper - 1) (fuel + 1)
              have hspec :
                  FirstTrueDescendingSpec pred
                    ((upper - 1) + 1 - (fuel + 1)) (upper - 1) out :=
                ih (upper := upper - 1) (by omega) (by omega) hterminal'
              unfold FirstTrueDescendingSpec at hspec
              rcases hspec with
                ⟨hlo, hhi, htrue, habove, htested⟩
              have hout :
                  firstTrueDescendingAux pred upper (fuel + 1 + 1) =
                    ⟨out.value, out.tested + 1⟩ := by
                rw [firstTrueDescendingAux]
                simp only [hpred]
                rfl
              rw [hout]
              unfold FirstTrueDescendingSpec
              dsimp
              refine ⟨?_, ?_, htrue, ?_, ?_⟩
              · rw [hlowerEq]
                exact hlo
              · omega
              · intro i hi hile
                by_cases hiup : i = upper
                · subst i
                  exact hpred
                · exact habove i hi (by omega)
              · omega

/-- The successful descending result lies in the tested interval. -/
theorem firstTrueDescendingAux_bounds
    (pred : ℕ → Bool) {upper fuel : ℕ}
    (hfuel : 0 < fuel)
    (hfit : fuel ≤ upper + 1)
    (hterminal : pred (upper + 1 - fuel) = true) :
    upper + 1 - fuel ≤ (firstTrueDescendingAux pred upper fuel).value ∧
      (firstTrueDescendingAux pred upper fuel).value ≤ upper := by
  have hspec := firstTrueDescendingAux_spec pred hfuel hfit hterminal
  exact ⟨hspec.1, hspec.2.1⟩

/-- The reported test count is the exact distance from the upper endpoint. -/
theorem firstTrueDescendingAux_tested
    (pred : ℕ → Bool) {upper fuel : ℕ}
    (hfuel : 0 < fuel)
    (hfit : fuel ≤ upper + 1)
    (hterminal : pred (upper + 1 - fuel) = true) :
    (firstTrueDescendingAux pred upper fuel).tested =
      upper - (firstTrueDescendingAux pred upper fuel).value + 1 := by
  exact (firstTrueDescendingAux_spec pred hfuel hfit hterminal).2.2.2.2

end KomorebiPadic
