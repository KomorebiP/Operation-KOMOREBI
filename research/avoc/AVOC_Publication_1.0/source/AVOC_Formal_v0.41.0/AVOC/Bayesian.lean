import AVOC.StochasticBlackwell
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

universe u v w

/-- A finite rational Bayesian belief state. -/
structure RationalBelief (Ω : Type u) [Fintype Ω] where
  prob : Ω → ℚ
  nonneg : ∀ ω, 0 ≤ prob ω
  sum_one : ∑ ω, prob ω = 1

@[ext] theorem RationalBelief.ext
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω)
    (h : ∀ ω, b.prob ω = c.prob ω) : b = c := by
  cases b with
  | mk bp bn bs =>
    cases c with
    | mk cp cn cs =>
      have hp : bp = cp := by
        funext ω
        exact h ω
      cases hp
      rfl

/-- Prior predictive probability of observation `o`. -/
def predictiveProb
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O) : ℚ :=
  ∑ ω, b.prob ω * E.prob ω o

/-- Predictive probabilities are nonnegative. -/
theorem predictiveProb_nonneg
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O) :
    0 ≤ predictiveProb b E o := by
  unfold predictiveProb
  apply Finset.sum_nonneg
  intro ω hω
  exact mul_nonneg (b.nonneg ω) (E.nonneg ω o)

/-- The prior predictive distribution over observations is normalized. -/
theorem predictiveProb_sum_one
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) :
    ∑ o, predictiveProb b E o = 1 := by
  unfold predictiveProb
  calc
    (∑ o, ∑ ω, b.prob ω * E.prob ω o)
        = ∑ ω, ∑ o, b.prob ω * E.prob ω o := by rw [Finset.sum_comm]
    _ = ∑ ω, b.prob ω := by
      apply Finset.sum_congr rfl
      intro ω hω
      rw [← Finset.mul_sum, E.sum_one]
      simp
    _ = 1 := b.sum_one

/-- Bayes numerator for a world and observation. -/
def bayesNumerator
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O) (ω : Ω) : ℚ :=
  b.prob ω * E.prob ω o

/-- A positive-evidence Bayes update is again a certified rational belief. -/
def bayesUpdate
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O)
    (hpos : 0 < predictiveProb b E o) : RationalBelief Ω where
  prob ω := bayesNumerator b E o ω / predictiveProb b E o
  nonneg := by
    intro ω
    exact div_nonneg
      (mul_nonneg (b.nonneg ω) (E.nonneg ω o))
      (le_of_lt hpos)
  sum_one := by
    unfold bayesNumerator predictiveProb
    change (∑ ω, (b.prob ω * E.prob ω o) * (∑ ω, b.prob ω * E.prob ω o)⁻¹) = 1
    rw [← Finset.sum_mul]
    exact mul_inv_cancel₀ (ne_of_gt hpos)

/-- Pointwise Bayes formula. -/
theorem bayesUpdate_mul_predictive
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O)
    (hpos : 0 < predictiveProb b E o) (ω : Ω) :
    (bayesUpdate b E o hpos).prob ω * predictiveProb b E o =
      b.prob ω * E.prob ω o := by
  unfold bayesUpdate bayesNumerator
  change (b.prob ω * E.prob ω o / predictiveProb b E o) * predictiveProb b E o =
    b.prob ω * E.prob ω o
  exact div_mul_cancel₀ _ (ne_of_gt hpos)

/-- Posterior expected utility of an action. -/
def posteriorExpectedUtility
    {Ω : Type u} [Fintype Ω]
    {A : Type w}
    (b : RationalBelief Ω) (utility : Ω → A → ℚ) (a : A) : ℚ :=
  ∑ ω, b.prob ω * utility ω a

/-- Bayes conditioning exactly factors the unnormalized signal/action score. -/
theorem predictive_mul_posteriorExpectedUtility
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w}
    (b : RationalBelief Ω) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (o : O)
    (hpos : 0 < predictiveProb b E o) (a : A) :
    predictiveProb b E o *
        posteriorExpectedUtility (bayesUpdate b E o hpos) utility a =
      signalActionScore b.prob utility E o a := by
  unfold posteriorExpectedUtility signalActionScore
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro ω hω
  rw [mul_assoc]
  have hbayes := bayesUpdate_mul_predictive b E o hpos ω
  calc
    predictiveProb b E o * ((bayesUpdate b E o hpos).prob ω * utility ω a)
        = ((bayesUpdate b E o hpos).prob ω * predictiveProb b E o) * utility ω a := by ring
    _ = (b.prob ω * E.prob ω o) * utility ω a := by rw [hbayes]
    _ = b.prob ω * (E.prob ω o * utility ω a) := by rw [mul_assoc]

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v w

/-- A zero predictive mass forces every prior-likelihood numerator in that
observation fiber to vanish. -/
theorem bayesNumerator_eq_zero_of_predictive_eq_zero
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O)
    (hzero : predictiveProb b E o = 0) (ω : Ω) :
    bayesNumerator b E o ω = 0 := by
  unfold predictiveProb at hzero
  unfold bayesNumerator
  have hall := (Finset.sum_eq_zero_iff_of_nonneg
    (fun x (_ : x ∈ (Finset.univ : Finset Ω)) =>
      mul_nonneg (b.nonneg x) (E.nonneg x o))).1 hzero
  exact hall ω (Finset.mem_univ ω)

/-- Total Bayes update.  An impossible observation may be assigned arbitrarily;
we choose the prior itself.  Its predictive coefficient is zero, so this choice
cannot affect expected continuation value. -/
noncomputable def bayesUpdateTotal
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O) :
    RationalBelief Ω :=
  if h : 0 < predictiveProb b E o then bayesUpdate b E o h else b

/-- On a positive-probability observation the total update is ordinary Bayes. -/
theorem bayesUpdateTotal_eq_of_pos
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O)
    (hpos : 0 < predictiveProb b E o) :
    bayesUpdateTotal b E o = bayesUpdate b E o hpos := by
  unfold bayesUpdateTotal
  simp [hpos]

/-- If predictive mass is not positive, it is zero. -/
theorem predictiveProb_eq_zero_of_not_pos
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O)
    (h : ¬ 0 < predictiveProb b E o) :
    predictiveProb b E o = 0 := by
  have hn := predictiveProb_nonneg b E o
  exact le_antisymm (le_of_not_gt h) hn

/-- Impossible observations contribute zero signal/action score. -/
theorem signalActionScore_eq_zero_of_predictive_eq_zero
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w}
    (b : RationalBelief Ω) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (o : O)
    (hzero : predictiveProb b E o = 0) (a : A) :
    signalActionScore b.prob utility E o a = 0 := by
  unfold signalActionScore
  apply Finset.sum_eq_zero
  intro ω hω
  have hn := bayesNumerator_eq_zero_of_predictive_eq_zero b E o hzero ω
  unfold bayesNumerator at hn
  rw [hn]
  simp

/-- Bayesian policy value written explicitly as predictive probability times
posterior expected utility. -/
noncomputable def bayesianPolicyValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w}
    (b : RationalBelief Ω) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (policy : O → A) : ℚ :=
  ∑ o, predictiveProb b E o *
    posteriorExpectedUtility (bayesUpdateTotal b E o) utility (policy o)

/-- The explicit posterior-predictive evaluation is exactly the inherited
Blackwell decision-value formula. -/
theorem bayesianPolicyValue_eq_stochasticDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w}
    (b : RationalBelief Ω) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (policy : O → A) :
    bayesianPolicyValue b utility E policy =
      stochasticDecisionValue b.prob utility E policy := by
  unfold bayesianPolicyValue stochasticDecisionValue
  apply Finset.sum_congr rfl
  intro o ho
  by_cases hpos : 0 < predictiveProb b E o
  · rw [bayesUpdateTotal_eq_of_pos b E o hpos]
    exact predictive_mul_posteriorExpectedUtility b utility E o hpos (policy o)
  · have hzero := predictiveProb_eq_zero_of_not_pos b E o hpos
    rw [hzero]
    simp [signalActionScore_eq_zero_of_predictive_eq_zero b utility E o hzero (policy o)]

end Komorebi.AVOC
