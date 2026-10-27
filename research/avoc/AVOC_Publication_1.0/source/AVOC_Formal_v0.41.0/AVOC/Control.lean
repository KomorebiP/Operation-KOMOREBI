import AVOC.Core
import Mathlib.Basic.Real.Basic
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

/-- The epistemic operation selected by the controller. The constructors are
semantic labels; theorems below concern policies over arbitrary finite action sets. -/
inductive EpistemicAction where
  | answer
  | derive
  | test
  | retrieve
  | requestData
  | abstain
  | formalize
  | verify
  | searchCounterexample
  | decompose
  | generalize
  | compress
  | stop
  deriving DecidableEq, Repr

/-- A typed decomposition of one-step research value. All quantities are
marginal changes relative to the current state. -/
structure ActionMetrics where
  verifiedGain : ℝ
  falsificationGain : ℝ
  reuseGain : ℝ
  debtAdded : ℝ
  cost : ℝ
  falseAdmissionRisk : ℝ

/-- Scalarized one-step objective. Positive coefficients penalize debt, cost,
and false-admission risk while rewarding falsification and future reuse. -/
def actionScore
    (wF wReuse wDebt wCost wRisk : ℝ) (m : ActionMetrics) : ℝ :=
  m.verifiedGain
    + wF * m.falsificationGain
    + wReuse * m.reuseGain
    - wDebt * m.debtAdded
    - wCost * m.cost
    - wRisk * m.falseAdmissionRisk

/-- Componentwise dominance is respected by every nonnegative scalarization.
This justifies pruning actions that are weakly worse on every declared axis. -/
theorem score_mono_of_dominance
    (wF wReuse wDebt wCost wRisk : ℝ) (a b : ActionMetrics)
    (hwF : 0 ≤ wF) (hwReuse : 0 ≤ wReuse) (hwDebt : 0 ≤ wDebt) (hwCost : 0 ≤ wCost) (hwRisk : 0 ≤ wRisk)
    (hv : a.verifiedGain ≤ b.verifiedGain)
    (hf : a.falsificationGain ≤ b.falsificationGain)
    (hr : a.reuseGain ≤ b.reuseGain)
    (hd : b.debtAdded ≤ a.debtAdded)
    (hc : b.cost ≤ a.cost)
    (hR : b.falseAdmissionRisk ≤ a.falseAdmissionRisk) :
    actionScore wF wReuse wDebt wCost wRisk a ≤ actionScore wF wReuse wDebt wCost wRisk b := by
  have hF := mul_le_mul_of_nonneg_left hf hwF
  have hReuse := mul_le_mul_of_nonneg_left hr hwReuse
  have hDebt := mul_le_mul_of_nonneg_left hd hwDebt
  have hCost := mul_le_mul_of_nonneg_left hc hwCost
  have hRisk := mul_le_mul_of_nonneg_left hR hwRisk
  unfold actionScore
  linarith

/-- Optimality of an action relative to a finite feasible set. -/
def OptimalOn {A : Type*} {U : Type*} [Preorder U]
    (feasible : Finset A) (utility : A → U) (chosen : A) : Prop :=
  chosen ∈ feasible ∧ ∀ a ∈ feasible, utility a ≤ utility chosen

/-- Every nonempty finite feasible action set has a one-step maximizer under a
linear utility order. This is the existence theorem behind a finite epistemic router. -/
theorem finite_epistemic_scheduler_exists
    {A : Type*} {U : Type*} [DecidableEq A] [LinearOrder U]
    (feasible : Finset A) (utility : A → U) (hne : feasible.Nonempty) :
    ∃ chosen, OptimalOn feasible utility chosen := by
  obtain ⟨chosen, hmem, hmax⟩ := Finset.exists_max_image feasible utility hne
  exact ⟨chosen, hmem, hmax⟩


/-- Hard one-step admissibility constraints.  Utility optimization happens only
after cost and false-admission risk are inside their declared caps. -/
def FeasibleMetrics (budget riskCap : ℝ) (m : ActionMetrics) : Prop :=
  m.cost ≤ budget ∧ m.falseAdmissionRisk ≤ riskCap

/-- Filter a finite action set to the actions satisfying the hard constraints. -/
noncomputable def feasibleActions {A : Type*} [DecidableEq A]
    (actions : Finset A) (metrics : A → ActionMetrics)
    (budget riskCap : ℝ) : Finset A := by
  classical
  exact actions.filter (fun a => FeasibleMetrics budget riskCap (metrics a))

/-- Constrained epistemic scheduler. If at least one action satisfies the hard
budget and risk caps, then a utility-maximizing feasible action exists. -/
theorem constrained_scheduler_exists
    {A : Type*} [DecidableEq A]
    (actions : Finset A) (metrics : A → ActionMetrics)
    (budget riskCap wF wReuse wDebt wCost wRisk : ℝ)
    (hne : (feasibleActions actions metrics budget riskCap).Nonempty) :
    ∃ chosen,
      chosen ∈ actions ∧
      FeasibleMetrics budget riskCap (metrics chosen) ∧
      ∀ a ∈ actions,
        FeasibleMetrics budget riskCap (metrics a) →
        actionScore wF wReuse wDebt wCost wRisk (metrics a) ≤
          actionScore wF wReuse wDebt wCost wRisk (metrics chosen) := by
  classical
  obtain ⟨chosen, hchosen, hmax⟩ :=
    finite_epistemic_scheduler_exists
      (feasibleActions actions metrics budget riskCap)
      (fun a => actionScore wF wReuse wDebt wCost wRisk (metrics a)) hne
  have hc : chosen ∈ actions ∧ FeasibleMetrics budget riskCap (metrics chosen) := by
    simpa [feasibleActions] using hchosen
  refine ⟨chosen, hc.1, hc.2, ?_⟩
  intro a ha hfeas
  apply hmax a
  simpa [feasibleActions] using And.intro ha hfeas

/-- Extend any action family by an explicit stop action with zero marginal value. -/
inductive WithStop (A : Type*) where
  | act (a : A)
  | stop
  deriving DecidableEq, Repr

/-- Utility for the explicit-stop extension. -/
def withStopUtility {A : Type*} (u : A → ℝ) : WithStop A → ℝ
  | .act a => u a
  | .stop => 0

/-- Stop rule: if every available continuation has nonpositive marginal utility,
then stopping weakly dominates every continuation. -/
theorem stop_optimal_of_nonpositive
    {A : Type*} (u : A → ℝ) (h : ∀ a, u a ≤ 0) :
    ∀ a : WithStop A, withStopUtility u a ≤ withStopUtility u (.stop) := by
  intro a
  cases a with
  | act x => exact h x
  | stop => exact le_rfl

/-- Selective-answer risk under zero loss for a correct answer. -/
def answerRisk (errorCost confidence : ℝ) : ℝ :=
  errorCost * (1 - confidence)

/-- Decision-theoretic threshold: when error cost is positive, answering has no
more loss than abstaining exactly above the corresponding confidence threshold. -/
theorem answer_better_iff_threshold
    (errorCost abstainCost confidence : ℝ) (herror : 0 < errorCost) :
    answerRisk errorCost confidence ≤ abstainCost ↔
      1 - abstainCost / errorCost ≤ confidence := by
  constructor
  · intro h
    have h' : (1 - confidence) * errorCost ≤ abstainCost := by
      simpa [answerRisk, mul_comm] using h
    have hdiv : 1 - confidence ≤ abstainCost / errorCost :=
      (le_div_iff₀ herror).2 h'
    linarith
  · intro h
    have hdiv : 1 - confidence ≤ abstainCost / errorCost := by
      linarith
    have h' : (1 - confidence) * errorCost ≤ abstainCost :=
      (le_div_iff₀ herror).1 hdiv
    simpa [answerRisk, mul_comm] using h'


/-- Expected utility of one speculative weak link under perfect rejection of
unproductive proposals. -/
def weakLinkUtility (p value generationCost verificationCost : ℝ) : ℝ :=
  p * value - generationCost - verificationCost

/-- The weak-link search criterion from the original theory: speculative search
has positive expected one-step value exactly when expected productive value
exceeds generation plus verification cost. -/
theorem weakLinkUtility_positive_iff
    (p value generationCost verificationCost : ℝ) :
    0 < weakLinkUtility p value generationCost verificationCost ↔
      generationCost + verificationCost < p * value := by
  unfold weakLinkUtility
  constructor <;> intro h <;> nlinarith

/-- Expected weak-link utility with an explicit false-admission harm term. -/
def weakLinkUtilityWithRisk
    (p value generationCost verificationCost falseAdmissionRate harm : ℝ) : ℝ :=
  p * value - generationCost - verificationCost
    - (1 - p) * falseAdmissionRate * harm

/-- Raising only the false-admission rate cannot improve risk-adjusted utility
when harm is nonnegative and `p ≤ 1`. -/
theorem weakLinkUtilityWithRisk_antitone_in_falseAdmission
    (p value generationCost verificationCost harm δ₁ δ₂ : ℝ)
    (hp : p ≤ 1) (hh : 0 ≤ harm) (hδ : δ₁ ≤ δ₂) :
    weakLinkUtilityWithRisk p value generationCost verificationCost δ₂ harm ≤
      weakLinkUtilityWithRisk p value generationCost verificationCost δ₁ harm := by
  unfold weakLinkUtilityWithRisk
  have h1mp : 0 ≤ 1 - p := by linarith
  have hcoef : 0 ≤ (1 - p) * harm := mul_nonneg h1mp hh
  have hm := mul_le_mul_of_nonneg_left hδ hcoef
  nlinarith

/-- Exact queue recurrence in an integer-valued accounting model. -/
def nextQueue (q generated verified discarded : ℤ) : ℤ :=
  q + generated - verified - discarded

/-- If generation exceeds verification plus deliberate discard, the unresolved
queue strictly grows in the exact accounting model. -/
theorem queue_grows_when_generation_exceeds_absorption
    (q generated verified discarded : ℤ)
    (h : verified + discarded < generated) :
    q < nextQueue q generated verified discarded := by
  unfold nextQueue
  linarith

/-- Conversely, if generation is fully absorbed by verification plus discard,
the unresolved queue cannot increase in the exact accounting model. -/
theorem queue_nonincreasing_when_absorbed
    (q generated verified discarded : ℤ)
    (h : generated ≤ verified + discarded) :
    nextQueue q generated verified discarded ≤ q := by
  unfold nextQueue
  linarith

end Komorebi.AVOC
