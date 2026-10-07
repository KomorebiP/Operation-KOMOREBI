import Mathlib.Data.Nat.Init
import Lean.Elab.Tactic.Omega

/-!
# Generic bounded sequential first-false search

This module implements a left-to-right Boolean search with exact accounting.
Under a certified false terminal point, it returns the first false index and
reports exactly the number of predicates evaluated.
-/

namespace KomorebiPadic

/-- Result of a bounded sequential first-false search. -/
structure FirstFalseResult where
  value : ℕ
  tested : ℕ
  deriving Repr, DecidableEq

/-- Search `fuel` consecutive indices starting at `q`.  If the interval
contains no false value, the total fallback is the first index after it. -/
def firstFalseResultAux (pred : ℕ → Bool) : ℕ → ℕ → FirstFalseResult
  | q, 0 => ⟨q, 0⟩
  | q, fuel + 1 =>
      if pred q then
        let out := firstFalseResultAux pred (q + 1) fuel
        ⟨out.value, out.tested + 1⟩
      else
        ⟨q, 1⟩

/-- Exact specification of a successful bounded first-false search. -/
def FirstFalseSpec
    (pred : ℕ → Bool) (q fuel : ℕ) (out : FirstFalseResult) : Prop :=
  q ≤ out.value ∧
  out.value < q + fuel ∧
  pred out.value = false ∧
  (∀ i : ℕ, q ≤ i → i < out.value → pred i = true) ∧
  out.tested = out.value - q + 1

/-- A false terminal point makes the bounded sequential search exact. -/
theorem firstFalseResultAux_spec
    (pred : ℕ → Bool) {q fuel : ℕ}
    (hfuel : 0 < fuel)
    (hterminal : pred (q + fuel - 1) = false) :
    FirstFalseSpec pred q fuel (firstFalseResultAux pred q fuel) := by
  induction fuel generalizing q with
  | zero => omega
  | succ fuel ih =>
      cases hpred : pred q with
      | false =>
          simp [firstFalseResultAux, hpred, FirstFalseSpec]
          omega
      | true =>
          cases fuel with
          | zero =>
              have hterminal' : pred q = false := by
                simpa using hterminal
              rw [hpred] at hterminal'
              contradiction
          | succ fuel =>
              have hidx :
                  (q + 1) + (fuel + 1) - 1 = q + (fuel + 1 + 1) - 1 := by
                omega
              have hterminal' :
                  pred ((q + 1) + (fuel + 1) - 1) = false := by
                rw [hidx]
                exact hterminal
              let out := firstFalseResultAux pred (q + 1) (fuel + 1)
              have hspec : FirstFalseSpec pred (q + 1) (fuel + 1) out :=
                ih (q := q + 1) (by omega) hterminal'
              unfold FirstFalseSpec at hspec
              rcases hspec with
                ⟨hlo, hhi, hfalse, hbefore, htested⟩
              have hout : firstFalseResultAux pred q (fuel + 1 + 1) =
                  ⟨out.value, out.tested + 1⟩ := by
                rw [firstFalseResultAux]
                simp only [hpred, ↓reduceIte]
                rfl
              rw [hout]
              unfold FirstFalseSpec
              dsimp
              refine ⟨?_, ?_, hfalse, ?_, ?_⟩
              · omega
              · omega
              · intro i hiq hil
                by_cases hi : i = q
                · subst i
                  exact hpred
                · exact hbefore i (by omega) hil
              · omega

/-- Successful search result lies inside its tested interval. -/
theorem firstFalseResultAux_bounds
    (pred : ℕ → Bool) {q fuel : ℕ}
    (hfuel : 0 < fuel)
    (hterminal : pred (q + fuel - 1) = false) :
    q ≤ (firstFalseResultAux pred q fuel).value ∧
      (firstFalseResultAux pred q fuel).value < q + fuel := by
  have hspec := firstFalseResultAux_spec pred hfuel hterminal
  exact ⟨hspec.1, hspec.2.1⟩

/-- The reported test count is the exact distance to the first false point. -/
theorem firstFalseResultAux_tested
    (pred : ℕ → Bool) {q fuel : ℕ}
    (hfuel : 0 < fuel)
    (hterminal : pred (q + fuel - 1) = false) :
    (firstFalseResultAux pred q fuel).tested =
      (firstFalseResultAux pred q fuel).value - q + 1 := by
  exact (firstFalseResultAux_spec pred hfuel hterminal).2.2.2.2

end KomorebiPadic
