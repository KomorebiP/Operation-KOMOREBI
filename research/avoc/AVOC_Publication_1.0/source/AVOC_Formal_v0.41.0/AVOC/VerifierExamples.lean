import AVOC.VerifierEnsemble
import AVOC.BayesianExamples

namespace Komorebi.AVOC

/-- A deliberately lossy specification that erases a Boolean intended state. -/
def eraseBoolSpecification : Bool → Unit := fun _ => ()

/-- Erasing Bool cannot support exact recovery of the identity task. -/
theorem erased_bool_specification_cannot_recover_identity :
    ∀ downstream : Unit → Bool,
      ¬ RecoversThrough eraseBoolSpecification id downstream := by
  apply specification_collision_obstructs_every_downstream
    (formalize := eraseBoolSpecification) (target := id)
    (x := false) (y := true)
  · rfl
  · decide

/-- No finite verifier ensemble downstream of the erased Bool specification can
recover the Boolean identity task exactly. -/
theorem erased_bool_specification_cannot_be_repaired_by_ensemble
    {V : Type*}
    (verifier : V → Unit → Bool)
    (aggregate : (V → Bool) → Bool) :
    ¬ ∀ b : Bool,
      aggregate (fun v => verifier v (eraseBoolSpecification b)) = b := by
  exact specification_collision_obstructs_verifier_ensemble
    (formalize := eraseBoolSpecification) (target := id)
    (x := false) (y := true)
    rfl (by decide) verifier aggregate

/-- Both verifiers fail on exactly the same half of a uniform Bool sample. -/
def perfectlyCorrelatedFailure : Bool → Finset Bool :=
  fun _ => {true}

/-- Each perfectly correlated verifier has marginal failure probability one half. -/
theorem perfectlyCorrelatedFailure_marginal (v : Bool) :
    eventProb uniformBoolBelief (perfectlyCorrelatedFailure v) = 1 / 2 := by
  simp [eventProb, perfectlyCorrelatedFailure, uniformBoolBelief]

/-- The joint failure event of the two perfectly correlated verifiers is still
that same half-probability event. -/
theorem perfectlyCorrelatedFailure_joint_event :
    jointFailureEvent perfectlyCorrelatedFailure = ({true} : Finset Bool) := by
  classical
  ext ω
  simp [jointFailureEvent, perfectlyCorrelatedFailure]

/-- Hence their joint failure probability is one half, not one quarter. -/
theorem perfectlyCorrelatedFailure_joint_prob :
    eventProb uniformBoolBelief (jointFailureEvent perfectlyCorrelatedFailure) = 1 / 2 := by
  rw [perfectlyCorrelatedFailure_joint_event]
  exact perfectlyCorrelatedFailure_marginal false

/-- The product of the two marginal failure probabilities is one quarter. -/
theorem perfectlyCorrelatedFailure_product_marginals :
    (∏ v : Bool, eventProb uniformBoolBelief (perfectlyCorrelatedFailure v)) = 1 / 4 := by
  simp [perfectlyCorrelatedFailure_marginal]
  norm_num

/-- Perfectly correlated verifier errors do not satisfy joint-failure
factorization.  This is a checked counterexample to silently multiplying
marginal verifier error rates. -/
theorem perfectlyCorrelatedFailure_not_factorized :
    ¬ JointFailureFactorizes uniformBoolBelief perfectlyCorrelatedFailure := by
  intro h
  unfold JointFailureFactorizes at h
  rw [perfectlyCorrelatedFailure_joint_prob,
    perfectlyCorrelatedFailure_product_marginals] at h
  norm_num at h

/-- Uniform belief on two independent Boolean coordinates. -/
def uniformBoolPairBelief : RationalBelief (Bool × Bool) where
  prob _ := 1 / 4
  nonneg := by intro ω; norm_num
  sum_one := by
    norm_num [Fintype.sum_prod_type, Fintype.sum_bool]

/-- Verifier `false` fails on the first coordinate and verifier `true` on the
second coordinate. -/
def coordinateFailure : Bool → Finset (Bool × Bool)
  | false => {(true, false), (true, true)}
  | true => {(false, true), (true, true)}

/-- Each coordinate verifier fails with probability one half. -/
theorem coordinateFailure_marginal (v : Bool) :
    eventProb uniformBoolPairBelief (coordinateFailure v) = 1 / 2 := by
  cases v <;> simp [eventProb, coordinateFailure, uniformBoolPairBelief] <;> norm_num

/-- Both coordinate verifiers fail together exactly on `(true,true)`. -/
theorem coordinateFailure_joint_event :
    jointFailureEvent coordinateFailure = ({(true, true)} : Finset (Bool × Bool)) := by
  classical
  ext ω
  rcases ω with ⟨a, b⟩
  cases a <;> cases b <;> simp [jointFailureEvent, coordinateFailure]

/-- Both coordinate verifiers fail together with probability one quarter. -/
theorem coordinateFailure_joint_prob :
    eventProb uniformBoolPairBelief (jointFailureEvent coordinateFailure) = 1 / 4 := by
  rw [coordinateFailure_joint_event]
  simp [eventProb, uniformBoolPairBelief]

/-- The coordinate-failure model satisfies the joint factorization used by the
independent-verifier product bound. -/
theorem coordinateFailure_factorizes :
    JointFailureFactorizes uniformBoolPairBelief coordinateFailure := by
  unfold JointFailureFactorizes
  rw [coordinateFailure_joint_prob]
  rw [Fintype.prod_bool, coordinateFailure_marginal, coordinateFailure_marginal]
  norm_num

end Komorebi.AVOC
