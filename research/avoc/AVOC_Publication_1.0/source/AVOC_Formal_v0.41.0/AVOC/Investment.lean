import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

/-- Immediate value of answering instead of building reusable infrastructure in
the canonical two-action example. -/
def immediateAnswerValue : ℝ := 0

/-- Building an artifact incurs an immediate cost. -/
def buildImmediateValue (cost : ℝ) : ℝ := -cost

/-- Two-step value of building an artifact now and receiving its future gain. -/
def buildTwoStepValue (cost futureGain : ℝ) : ℝ := -cost + futureGain

/-- A strictly positive build cost makes a myopic one-step controller prefer the
zero-value immediate answer over infrastructure construction. -/
theorem myopic_prefers_immediate_answer
    (cost : ℝ) (hcost : 0 < cost) :
    buildImmediateValue cost < immediateAnswerValue := by
  unfold buildImmediateValue immediateAnswerValue
  linarith

/-- If future reuse gain exceeds build cost, the two-step value of constructing
the artifact is positive. -/
theorem artifact_investment_positive_over_two_steps
    (cost futureGain : ℝ) (hgain : cost < futureGain) :
    immediateAnswerValue < buildTwoStepValue cost futureGain := by
  unfold immediateAnswerValue buildTwoStepValue
  linarith

/-- Horizon reversal theorem: under positive build cost but larger future reuse
gain, one-step optimization rejects infrastructure while two-step optimization
strictly prefers it. -/
theorem myopic_vs_artifact_investment_reversal
    (cost futureGain : ℝ) (hcost : 0 < cost) (hgain : cost < futureGain) :
    buildImmediateValue cost < immediateAnswerValue ∧
    immediateAnswerValue < buildTwoStepValue cost futureGain := by
  exact ⟨myopic_prefers_immediate_answer cost hcost,
    artifact_investment_positive_over_two_steps cost futureGain hgain⟩

/-- The future gain required to reverse the myopic choice is exactly any gain
strictly larger than construction cost. -/
theorem buildTwoStepValue_positive_iff
    (cost futureGain : ℝ) :
    0 < buildTwoStepValue cost futureGain ↔ cost < futureGain := by
  unfold buildTwoStepValue
  constructor <;> intro h <;> linarith

end Komorebi.AVOC
