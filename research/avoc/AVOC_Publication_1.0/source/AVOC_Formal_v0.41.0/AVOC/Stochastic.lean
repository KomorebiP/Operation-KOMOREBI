import AVOC.Blackwell
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Finset.Max
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset

namespace Komorebi.AVOC

universe u v

/-- Finite rational stochastic epistemic-control system.  The transition rows
are certified probability distributions. -/
structure FiniteStochasticControlSystem
    (S : Type u) (A : Type v) [Fintype S] [DecidableEq A] where
  actions : Finset A
  actions_nonempty : actions.Nonempty
  transitionProb : S → A → S → ℚ
  transition_nonneg : ∀ s a s', 0 ≤ transitionProb s a s'
  transition_sum_one : ∀ s a, ∑ s', transitionProb s a s' = 1
  reward : S → A → ℚ

/-- Expected continuation value under one stochastic transition. -/
def expectedContinuation
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (V : S → ℚ) (s : S) (a : A) : ℚ :=
  ∑ s', sys.transitionProb s a s' * V s'

/-- Finite-horizon stochastic Bellman value. -/
noncomputable def stochasticHorizonValue
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) : ℕ → S → ℚ
  | 0, _ => 0
  | n + 1, s =>
      let vals := sys.actions.image (fun a =>
        sys.reward s a + expectedContinuation sys (stochasticHorizonValue sys n) s a)
      vals.max' (sys.actions_nonempty.image _)

/-- Stochastic Bellman action value. -/
noncomputable def stochasticQValue
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    (n : ℕ) (s : S) (a : A) : ℚ :=
  sys.reward s a + expectedContinuation sys (stochasticHorizonValue sys n) s a

/-- Bellman maximum equation for finite rational stochastic control. -/
theorem stochasticHorizonValue_succ_eq_max
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ) (s : S) :
    stochasticHorizonValue sys (n + 1) s =
      (sys.actions.image (stochasticQValue sys n s)).max'
        (sys.actions_nonempty.image _) := by
  rfl

/-- Every finite stochastic state/horizon has a Bellman-maximizing action. -/
theorem stochastic_bellman_action_exists
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ) (s : S) :
    ∃ a ∈ sys.actions, ∀ b ∈ sys.actions,
      stochasticQValue sys n s b ≤ stochasticQValue sys n s a := by
  exact Finset.exists_max_image sys.actions (stochasticQValue sys n s)
    sys.actions_nonempty

/-- A Bellman-maximizing stochastic action realizes the horizon value. -/
theorem stochasticHorizonValue_eq_qValue_of_optimal
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions)
    (hmax : ∀ b ∈ sys.actions,
      stochasticQValue sys n s b ≤ stochasticQValue sys n s a) :
    stochasticHorizonValue sys (n + 1) s = stochasticQValue sys n s a := by
  rw [stochasticHorizonValue_succ_eq_max]
  apply (Finset.max'_eq_iff _ _ _).2
  constructor
  · exact Finset.mem_image.mpr ⟨a, ha, rfl⟩
  · intro y hy
    rcases Finset.mem_image.mp hy with ⟨b, hb, rfl⟩
    exact hmax b hb

/-- Consequently an optimal finite-horizon stochastic action exists. -/
theorem stochastic_finite_horizon_optimal_action_exists
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ) (s : S) :
    ∃ a ∈ sys.actions,
      stochasticHorizonValue sys (n + 1) s = stochasticQValue sys n s a := by
  obtain ⟨a, ha, hmax⟩ := stochastic_bellman_action_exists sys n s
  exact ⟨a, ha, stochasticHorizonValue_eq_qValue_of_optimal sys n s a ha hmax⟩

/-- Transition expectation preserves pointwise order because probabilities are
nonnegative. -/
theorem expectedContinuation_mono
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A)
    {V W : S → ℚ} (hVW : ∀ s, V s ≤ W s) (s : S) (a : A) :
    expectedContinuation sys V s a ≤ expectedContinuation sys W s a := by
  unfold expectedContinuation
  apply Finset.sum_le_sum
  intro s' hs'
  exact mul_le_mul_of_nonneg_left (hVW s') (sys.transition_nonneg s a s')

/-- Expectation of a constant equals that constant under a certified stochastic
row. -/
theorem expectedContinuation_const
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (c : ℚ) (s : S) (a : A) :
    expectedContinuation sys (fun _ => c) s a = c := by
  unfold expectedContinuation
  rw [← Finset.sum_mul]
  rw [sys.transition_sum_one]
  simp

end Komorebi.AVOC
