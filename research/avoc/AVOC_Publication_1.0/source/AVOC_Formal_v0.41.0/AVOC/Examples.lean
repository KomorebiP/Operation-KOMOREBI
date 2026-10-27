import AVOC

namespace Komorebi.AVOC.Examples

/-- Maximum compression of Bool to Unit loses the Bool identity target. -/
def eraseBool : Bool → Unit := fun _ => ()

def boolTarget : Bool → Bool := id

example : ¬ TaskSufficient eraseBool boolTarget := by
  apply collision_obstructs_sufficiency (x := false) (y := true)
  · rfl
  · decide

/-- Keeping the target itself is sufficient and task-minimal. -/
example : TaskMinimal boolTarget boolTarget := by
  exact target_is_taskMinimal boolTarget

/-- A two-query family: identity and negation.  The identity representation is
jointly sufficient because each requested answer factors through it. -/
def boolQueries : Bool → Bool → Bool
  | false, x => x
  | true, x => !x

example : TaskSufficient boolTarget (JointTarget boolQueries) := by
  apply each_sufficient_implies_joint
  intro q
  cases q with
  | false => exact target_is_sufficient boolTarget
  | true =>
      refine ⟨fun b => !b, ?_⟩
      intro x
      rfl

end Komorebi.AVOC.Examples

namespace Komorebi.AVOC.Examples.LowBlock

/-- The identity encoding has no collisions against the identity target. -/
example : collisionPairs boolTarget boolTarget = ∅ := by
  exact sufficient_collisionPairs_empty (target_is_sufficient boolTarget)

/-- Constant Bool context loses a target-relevant distinction. -/
def constantBool : Bool → Bool := fun _ => false

example : collisionPairs constantBool boolTarget ≠ ∅ := by
  intro h
  have hmem : (false, true) ∈ collisionPairs constantBool boolTarget :=
    (mem_collisionPairs_iff constantBool boolTarget false true).2 ⟨rfl, by decide⟩
  rw [h] at hmem
  simp at hmem

inductive BoolContext where
  | constant
  | keep
  deriving DecidableEq, Repr

def boolContextFamily : ContextFamily BoolContext Bool Bool where
  encode
    | .constant => constantBool
    | .keep => boolTarget
  cost
    | .constant => 0
    | .keep => 1

/-- A finite candidate context family with at least one sufficient design has a
minimum-cost sufficient member. -/
example :
    ∃ chosen,
      MinimumCostSufficientContext boolContextFamily
        ({BoolContext.constant, BoolContext.keep} : Finset BoolContext)
        boolQueries ({false} : Finset Bool) chosen := by
  apply minimumCostSufficientContext_exists
  refine ⟨BoolContext.keep, ?_⟩
  rw [mem_sufficientContexts_iff]
  constructor
  · simp
  · intro q hq
    simp at hq
    subst q
    exact target_is_sufficient boolTarget

/-- Proposal-only batches preserve a proposal status exactly. -/
def proposalLedger : EpistemicLedger Bool where
  candidates := ∅
  status := fun _ => .proposal

example :
    (proposeMany proposalLedger [{true}, {false}]).status true = .proposal := by
  exact proposeMany_status_eq proposalLedger [{true}, {false}] true

/-- A one-unit infrastructure cost with three units of future gain exhibits the
formal horizon reversal. -/
example :
    buildImmediateValue 1 < immediateAnswerValue ∧
    immediateAnswerValue < buildTwoStepValue 1 3 := by
  exact myopic_vs_artifact_investment_reversal 1 3 (by norm_num) (by norm_num)

end Komorebi.AVOC.Examples.LowBlock
