import AVOC.Bayesian
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Finset.Max
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace Komorebi.AVOC

universe u v w z

/-- Finite rational Bayesian epistemic-control system.  The hidden world is
fixed; actions choose experiments, observations update the belief, and reward is
allowed to depend on the current belief and epistemic action. -/
structure FiniteBayesianControlSystem
    (Ω : Type u) (A : Type v) (O : Type w)
    [Fintype Ω] [Fintype O] [DecidableEq A] where
  actions : Finset A
  actions_nonempty : actions.Nonempty
  experiment : A → RationalChannel Ω O
  reward : RationalBelief Ω → A → ℚ

/-- Expected continuation value after an epistemic action and Bayes update. -/
noncomputable def bayesianExpectedContinuation
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (V : RationalBelief Ω → ℚ)
    (b : RationalBelief Ω) (a : A) : ℚ :=
  ∑ o, predictiveProb b (sys.experiment a) o *
    V (bayesUpdateTotal b (sys.experiment a) o)

/-- Finite-horizon Bellman value on Bayesian belief states. -/
noncomputable def bayesianHorizonValue
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O) : ℕ → RationalBelief Ω → ℚ
  | 0, _ => 0
  | n + 1, b =>
      let vals := sys.actions.image (fun a =>
        sys.reward b a + bayesianExpectedContinuation sys (bayesianHorizonValue sys n) b a)
      vals.max' (sys.actions_nonempty.image _)

/-- Bayesian Bellman action value. -/
noncomputable def bayesianQValue
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (n : ℕ) (b : RationalBelief Ω) (a : A) : ℚ :=
  sys.reward b a + bayesianExpectedContinuation sys (bayesianHorizonValue sys n) b a

/-- Bellman maximum equation on beliefs. -/
theorem bayesianHorizonValue_succ_eq_max
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (n : ℕ) (b : RationalBelief Ω) :
    bayesianHorizonValue sys (n + 1) b =
      (sys.actions.image (bayesianQValue sys n b)).max'
        (sys.actions_nonempty.image _) := by
  rfl

/-- Every finite Bayesian belief state/horizon has a maximizing epistemic action. -/
theorem bayesian_bellman_action_exists
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (n : ℕ) (b : RationalBelief Ω) :
    ∃ a ∈ sys.actions, ∀ c ∈ sys.actions,
      bayesianQValue sys n b c ≤ bayesianQValue sys n b a := by
  exact Finset.exists_max_image sys.actions (bayesianQValue sys n b)
    sys.actions_nonempty

/-- A maximizing epistemic action realizes the Bayesian horizon value. -/
theorem bayesianHorizonValue_eq_qValue_of_optimal
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (n : ℕ) (b : RationalBelief Ω) (a : A)
    (ha : a ∈ sys.actions)
    (hmax : ∀ c ∈ sys.actions,
      bayesianQValue sys n b c ≤ bayesianQValue sys n b a) :
    bayesianHorizonValue sys (n + 1) b = bayesianQValue sys n b a := by
  rw [bayesianHorizonValue_succ_eq_max]
  apply (Finset.max'_eq_iff _ _ _).2
  constructor
  · exact Finset.mem_image.mpr ⟨a, ha, rfl⟩
  · intro y hy
    rcases Finset.mem_image.mp hy with ⟨c, hc, rfl⟩
    exact hmax c hc

/-- Hence a finite-horizon optimal Bayesian epistemic action exists. -/
theorem bayesian_finite_horizon_optimal_action_exists
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (n : ℕ) (b : RationalBelief Ω) :
    ∃ a ∈ sys.actions,
      bayesianHorizonValue sys (n + 1) b = bayesianQValue sys n b a := by
  obtain ⟨a, ha, hmax⟩ := bayesian_bellman_action_exists sys n b
  exact ⟨a, ha, bayesianHorizonValue_eq_qValue_of_optimal sys n b a ha hmax⟩

/-- Bayesian expectation is monotone in continuation value. -/
theorem bayesianExpectedContinuation_mono
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    {V W : RationalBelief Ω → ℚ}
    (hVW : ∀ b, V b ≤ W b)
    (b : RationalBelief Ω) (a : A) :
    bayesianExpectedContinuation sys V b a ≤
      bayesianExpectedContinuation sys W b a := by
  unfold bayesianExpectedContinuation
  apply Finset.sum_le_sum
  intro o ho
  exact mul_le_mul_of_nonneg_left
    (hVW (bayesUpdateTotal b (sys.experiment a) o))
    (predictiveProb_nonneg b (sys.experiment a) o)

/-- Expectation of a constant continuation value is that constant. -/
theorem bayesianExpectedContinuation_const
    {Ω : Type u} {A : Type v} {O : Type w}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : FiniteBayesianControlSystem Ω A O)
    (c : ℚ) (b : RationalBelief Ω) (a : A) :
    bayesianExpectedContinuation sys (fun _ => c) b a = c := by
  unfold bayesianExpectedContinuation
  rw [← Finset.sum_mul]
  rw [predictiveProb_sum_one]
  simp

/-- Posterior belief is a martingale coordinatewise: averaging posterior mass
over observations recovers the prior mass. -/
theorem posterior_martingale_coordinate
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (ω : Ω) :
    ∑ o, predictiveProb b E o * (bayesUpdateTotal b E o).prob ω = b.prob ω := by
  calc
    (∑ o, predictiveProb b E o * (bayesUpdateTotal b E o).prob ω)
        = ∑ o, b.prob ω * E.prob ω o := by
          apply Finset.sum_congr rfl
          intro o ho
          by_cases hpos : 0 < predictiveProb b E o
          · rw [bayesUpdateTotal_eq_of_pos b E o hpos]
            have hb := bayesUpdate_mul_predictive b E o hpos ω
            nlinarith
          · have hzero := predictiveProb_eq_zero_of_not_pos b E o hpos
            have hn := bayesNumerator_eq_zero_of_predictive_eq_zero b E o hzero ω
            unfold bayesNumerator at hn
            rw [hzero, hn]
            simp
    _ = b.prob ω := by
      rw [← Finset.mul_sum, E.sum_one]
      simp

/-- Law of total expectation under Bayes updating. -/
theorem bayesian_law_of_total_expectation
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (f : Ω → ℚ) :
    ∑ o, predictiveProb b E o *
        (∑ ω, (bayesUpdateTotal b E o).prob ω * f ω) =
      ∑ ω, b.prob ω * f ω := by
  let utility : Ω → Unit → ℚ := fun ω _ => f ω
  let policy : O → Unit := fun _ => ()
  calc
    (∑ o, predictiveProb b E o *
        (∑ ω, (bayesUpdateTotal b E o).prob ω * f ω))
        = bayesianPolicyValue b utility E policy := by rfl
    _ = stochasticDecisionValue b.prob utility E policy :=
      bayesianPolicyValue_eq_stochasticDecisionValue b utility E policy
    _ = ∑ ω, b.prob ω * f ω := by
      unfold stochasticDecisionValue signalActionScore
      calc
        (∑ o, ∑ ω, b.prob ω * E.prob ω o * f ω)
            = ∑ ω, ∑ o, b.prob ω * E.prob ω o * f ω := by rw [Finset.sum_comm]
        _ = ∑ ω, b.prob ω * f ω := by
          apply Finset.sum_congr rfl
          intro ω hω
          calc
            (∑ o, b.prob ω * E.prob ω o * f ω)
                = b.prob ω * (∑ o, E.prob ω o) * f ω := by
                    rw [Finset.mul_sum]
                    rw [Finset.sum_mul]
            _ = b.prob ω * f ω := by rw [E.sum_one]; simp

/-- Best Bayesian posterior-policy value.  The inherited Blackwell maximum
is used as the canonical finite maximum; `bayesianPolicyValue_eq_stochasticDecisionValue`
proves this is exactly the maximum of explicit posterior-policy values. -/
noncomputable def bestBayesianDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {D : Type z} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω O) : ℚ :=
  bestStochasticDecisionValue b.prob utility E

/-- Bayesian and Blackwell best decision values coincide definitionally. -/
theorem bestBayesianDecisionValue_eq_bestStochasticDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {D : Type z} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω O) :
    bestBayesianDecisionValue b utility E =
      bestStochasticDecisionValue b.prob utility E := by
  rfl

/-- A posterior policy attaining the best Bayesian decision value exists. -/
theorem best_bayesian_policy_exists
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {D : Type z} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω O) :
    ∃ policy : O → D,
      bayesianPolicyValue b utility E policy =
        bestBayesianDecisionValue b utility E := by
  obtain ⟨policy, hp⟩ := best_stochastic_policy_exists b.prob utility E
  refine ⟨policy, ?_⟩
  rw [bayesianPolicyValue_eq_stochasticDecisionValue]
  exact hp

/-- Bayesian Blackwell monotonicity: stochastic garbling cannot improve the
best posterior-expected decision value. -/
theorem bayesian_blackwell_monotonicity
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {D : Type z} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse) :
    bestBayesianDecisionValue b utility (composeChannel E K) ≤
      bestBayesianDecisionValue b utility E := by
  rw [bestBayesianDecisionValue_eq_bestStochasticDecisionValue]
  rw [bestBayesianDecisionValue_eq_bestStochasticDecisionValue]
  exact stochastic_blackwell_monotonicity b.prob utility E K

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v w z

/-- Decision-theoretic value of information under a certified Bayesian prior. -/
noncomputable def bayesianValueOfInformation
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {D : Type w} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω O) : ℚ :=
  valueOfInformation b.prob utility E

/-- Free Bayesian information has nonnegative decision value. -/
theorem bayesianValueOfInformation_nonneg
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {D : Type w} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω O) :
    0 ≤ bayesianValueOfInformation b utility E := by
  exact valueOfInformation_nonneg b.prob utility E

/-- Bayesian value of information is monotone under Blackwell garbling. -/
theorem bayesianValueOfInformation_mono_under_garbling
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {D : Type z} [Fintype D] [Nonempty D]
    (b : RationalBelief Ω) (utility : Ω → D → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse) :
    bayesianValueOfInformation b utility (composeChannel E K) ≤
      bayesianValueOfInformation b utility E := by
  exact valueOfInformation_mono_under_garbling b.prob utility E K

end Komorebi.AVOC
