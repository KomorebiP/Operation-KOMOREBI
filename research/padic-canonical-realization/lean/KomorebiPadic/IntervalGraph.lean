import Mathlib.Data.Nat.Init
import Lean.Elab.Tactic.Omega

/-!
# Initial-interval theorem for correction targets

This file proves the graph-theoretic part of the Block 03 reduction.  The
arithmetic input is packaged as a predecessor property: every edge reaching a
target above `1` has an edge reaching the immediately preceding target.
No p-adic theorem is assumed globally; concrete arithmetic models must supply
that property.
-/

namespace KomorebiPadic

/-- A correction-edge system indexed by quotient state `q` and order `k`. -/
structure PredecessorEdgeSystem where
  edge : ℕ → ℕ → Prop
  predecessor :
    ∀ {q k : ℕ}, 1 ≤ q → edge q k → 1 < q + k →
      (0 < k ∧ edge q (k - 1)) ∨
      (1 < q ∧ edge (q - 1) k)

/-- `t` is produced from one of the quotient states `1, ..., Q`. -/
def IsTarget (G : PredecessorEdgeSystem) (Q t : ℕ) : Prop :=
  ∃ q k : ℕ, 1 ≤ q ∧ q ≤ Q ∧ G.edge q k ∧ t = q + k

/-- A target above `1` forces its immediate predecessor target. -/
theorem isTarget_pred
    (G : PredecessorEdgeSystem) {Q t : ℕ}
    (ht : IsTarget G Q t) (ht1 : 1 < t) :
    IsTarget G Q (t - 1) := by
  rcases ht with ⟨q, k, hq1, hqQ, hedge, rfl⟩
  rcases G.predecessor hq1 hedge ht1 with hleft | hright
  · rcases hleft with ⟨hk, hpred⟩
    refine ⟨q, k - 1, hq1, hqQ, hpred, ?_⟩
    omega
  · rcases hright with ⟨hq, hpred⟩
    refine ⟨q - 1, k, ?_, ?_, hpred, ?_⟩ <;> omega

/-- Repeated predecessor closure. -/
theorem isTarget_sub
    (G : PredecessorEdgeSystem) {Q t n : ℕ}
    (ht : IsTarget G Q t) (hn : n ≤ t - 1) :
    IsTarget G Q (t - n) := by
  induction n with
  | zero => simpa using ht
  | succ n ih =>
      have hn' : n ≤ t - 1 := by omega
      have htn : IsTarget G Q (t - n) := ih hn'
      have hpos : 1 < t - n := by omega
      have hpred := isTarget_pred G htn hpos
      have heq : t - (n + 1) = t - n - 1 := by omega
      rw [heq]
      exact hpred

/-- The target set over an initial quotient interval is downward closed above `1`. -/
theorem isTarget_of_between
    (G : PredecessorEdgeSystem) {Q s t : ℕ}
    (ht : IsTarget G Q t) (hs : 1 ≤ s) (hst : s ≤ t) :
    IsTarget G Q s := by
  have hsub := isTarget_sub G ht (n := t - s) (by omega)
  have heq : t - (t - s) = s := by omega
  rw [heq] at hsub
  exact hsub

/-- If `1` is produced, every nonempty finite target set is an initial interval. -/
theorem target_interval_property
    (G : PredecessorEdgeSystem) {Q M : ℕ}
    (hM : IsTarget G Q M) :
    ∀ s : ℕ, 1 ≤ s → s ≤ M → IsTarget G Q s := by
  intro s hs hsM
  exact isTarget_of_between G hM hs hsM

end KomorebiPadic
