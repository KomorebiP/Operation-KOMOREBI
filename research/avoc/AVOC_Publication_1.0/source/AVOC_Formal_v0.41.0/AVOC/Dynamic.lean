import AVOC.Control
import Mathlib.Data.Finset.Max

namespace Komorebi.AVOC

/-- A finite deterministic epistemic-control model.  `reward` is interpreted as
one-step verified net value; it may already include cost, debt, and risk penalties. -/
structure FiniteControlSystem (S A : Type*) [DecidableEq A] where
  actions : Finset A
  actions_nonempty : actions.Nonempty
  transition : S → A → S
  reward : S → A → ℝ

/-- Finite-horizon value function. At each step, maximize current reward plus
optimal continuation value. -/
noncomputable def horizonValue {S A : Type*} [DecidableEq A]
    (sys : FiniteControlSystem S A) : ℕ → S → ℝ
  | 0, _ => 0
  | n + 1, s =>
      let values := sys.actions.image
        (fun a => sys.reward s a + horizonValue sys n (sys.transition s a))
      values.max' (sys.actions_nonempty.image _)

/-- Bellman action value with `n` continuation steps remaining after this action. -/
noncomputable def qValue {S A : Type*} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) (a : A) : ℝ :=
  sys.reward s a + horizonValue sys n (sys.transition s a)

/-- The finite-horizon value satisfies the Bellman maximum equation by
construction. -/
theorem horizonValue_succ_eq_max
    {S A : Type*} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) :
    horizonValue sys (n + 1) s =
      (sys.actions.image (qValue sys n s)).max'
        (sys.actions_nonempty.image _) := by
  rfl

/-- At every state and finite horizon, at least one admissible epistemic action
maximizes current reward plus optimal continuation value. -/
theorem bellman_action_exists
    {S A : Type*} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) :
    ∃ a ∈ sys.actions, ∀ b ∈ sys.actions,
      qValue sys n s b ≤ qValue sys n s a := by
  exact Finset.exists_max_image sys.actions (qValue sys n s) sys.actions_nonempty

/-- A Bellman-maximizing action realizes the finite-horizon value. -/
theorem horizonValue_eq_qValue_of_optimal
    {S A : Type*} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions)
    (hmax : ∀ b ∈ sys.actions, qValue sys n s b ≤ qValue sys n s a) :
    horizonValue sys (n + 1) s = qValue sys n s a := by
  rw [horizonValue_succ_eq_max]
  apply (Finset.max'_eq_iff _ _ _).2
  constructor
  · exact Finset.mem_image.mpr ⟨a, ha, rfl⟩
  · intro y hy
    rcases Finset.mem_image.mp hy with ⟨b, hb, rfl⟩
    exact hmax b hb

/-- Therefore every finite-horizon state has an action whose Bellman value is
exactly the optimal horizon value. -/
theorem finite_horizon_optimal_action_exists
    {S A : Type*} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) :
    ∃ a ∈ sys.actions,
      horizonValue sys (n + 1) s = qValue sys n s a := by
  obtain ⟨a, ha, hmax⟩ := bellman_action_exists sys n s
  exact ⟨a, ha, horizonValue_eq_qValue_of_optimal sys n s a ha hmax⟩

end Komorebi.AVOC
