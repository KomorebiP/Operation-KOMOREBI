import AVOC.FiniteEvents
import AVOC.Specification

namespace Komorebi.AVOC

universe u v

/-- Event on which every verifier in a finite ensemble fails. -/
noncomputable def jointFailureEvent
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (fail : V → Finset Ω) : Finset Ω := by
  classical
  exact Finset.univ.filter (fun ω => ∀ v, ω ∈ fail v)

/-- Membership in the joint-failure event means every verifier fails. -/
theorem mem_jointFailureEvent
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (fail : V → Finset Ω) (ω : Ω) :
    ω ∈ jointFailureEvent fail ↔ ∀ v, ω ∈ fail v := by
  classical
  simp [jointFailureEvent]

/-- The joint failure event is contained in every individual verifier's failure
 event.  No independence assumption is needed. -/
theorem jointFailureEvent_subset
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (fail : V → Finset Ω) (v : V) :
    jointFailureEvent fail ⊆ fail v := by
  intro ω hω
  exact (mem_jointFailureEvent fail ω).1 hω v

/-- Without independence, the probability that all verifiers fail is bounded by
any single verifier's marginal failure probability, but not in general by a
product of marginals. -/
theorem jointFailure_prob_le_marginal
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω) (fail : V → Finset Ω) (v : V) :
    eventProb b (jointFailureEvent fail) ≤ eventProb b (fail v) := by
  exact eventProb_mono b (jointFailureEvent_subset fail v)

/-- The exact factorization property needed for the familiar independent
all-verifiers-fail product.  AVOC states this property explicitly rather than
silently assuming independent verifier errors. -/
def JointFailureFactorizes
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω) (fail : V → Finset Ω) : Prop :=
  eventProb b (jointFailureEvent fail) = ∏ v, eventProb b (fail v)

/-- If joint failure factorizes, its probability is exactly the product of the
individual verifier failure probabilities. -/
theorem jointFailure_prob_eq_product
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω) (fail : V → Finset Ω)
    (hfactor : JointFailureFactorizes b fail) :
    eventProb b (jointFailureEvent fail) = ∏ v, eventProb b (fail v) := by
  exact hfactor

/-- A wrong accepted result is covered by two conceptually distinct routes:
shared specification error, or simultaneous downstream verifier failure. -/
def WrongCoveredBySpecificationOrVerification
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω) : Prop :=
  wrong ⊆ specificationError ∪ jointFailureEvent fail

/-- General union-bound decomposition, requiring no independence. -/
theorem wrong_probability_le_specification_plus_joint_failure
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω)
    (hcover : WrongCoveredBySpecificationOrVerification wrong specificationError fail) :
    eventProb b wrong ≤
      eventProb b specificationError + eventProb b (jointFailureEvent fail) := by
  calc
    eventProb b wrong
        ≤ eventProb b (specificationError ∪ jointFailureEvent fail) :=
          eventProb_mono b hcover
    _ ≤ eventProb b specificationError + eventProb b (jointFailureEvent fail) :=
      eventProb_union_le_add b specificationError (jointFailureEvent fail)

/-- Under explicit joint-failure factorization, wrong-result probability is at
most the shared-specification probability plus the product of verifier failure
probabilities. -/
theorem wrong_probability_le_specification_plus_product
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω)
    (hcover : WrongCoveredBySpecificationOrVerification wrong specificationError fail)
    (hfactor : JointFailureFactorizes b fail) :
    eventProb b wrong ≤
      eventProb b specificationError + ∏ v, eventProb b (fail v) := by
  rw [← hfactor]
  exact wrong_probability_le_specification_plus_joint_failure
    b wrong specificationError fail hcover

/-- If every verifier has the same marginal failure probability `δ` and the
joint event factorizes, the verifier term is `δ^(number of verifiers)`. -/
theorem wrong_probability_le_specification_plus_power
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω) (δ : ℚ)
    (hcover : WrongCoveredBySpecificationOrVerification wrong specificationError fail)
    (hfactor : JointFailureFactorizes b fail)
    (hmarginal : ∀ v, eventProb b (fail v) = δ) :
    eventProb b wrong ≤
      eventProb b specificationError + δ ^ Fintype.card V := by
  have hbase := wrong_probability_le_specification_plus_product
    b wrong specificationError fail hcover hfactor
  have hprod : (∏ v, eventProb b (fail v)) = δ ^ Fintype.card V := by
    have h := Finset.prod_eq_pow_card
      (s := (Finset.univ : Finset V))
      (f := fun v => eventProb b (fail v))
      (b := δ)
      (by
        intro v hv
        exact hmarginal v)
    simpa using h
  rw [hprod] at hbase
  exact hbase

/-- If every shared specification error is itself a wrong-result outcome, then
its probability is a lower bound on total wrong-result probability.  This is
the irreducible shared-specification floor: downstream verifier multiplicity
cannot lower it. -/
theorem shared_specification_error_is_lower_bound
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    {specificationError wrong : Finset Ω}
    (hfloor : specificationError ⊆ wrong) :
    eventProb b specificationError ≤ eventProb b wrong := by
  exact eventProb_mono b hfloor

/-- Sandwich theorem: under a shared-specification floor, a cover by
specification-or-joint-verifier error, and factorized verifier failures, total
wrong-result probability lies between the specification term and specification
plus the product verifier term. -/
theorem verifier_ensemble_error_sandwich
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω)
    (hfloor : specificationError ⊆ wrong)
    (hcover : WrongCoveredBySpecificationOrVerification wrong specificationError fail)
    (hfactor : JointFailureFactorizes b fail) :
    eventProb b specificationError ≤ eventProb b wrong ∧
      eventProb b wrong ≤
        eventProb b specificationError + ∏ v, eventProb b (fail v) := by
  exact ⟨shared_specification_error_is_lower_bound b hfloor,
    wrong_probability_le_specification_plus_product
      b wrong specificationError fail hcover hfactor⟩

/-- When specification-error and pure joint-verifier-failure modes are disjoint
and together exactly constitute the wrong-result event, their probabilities add
exactly. -/
theorem exact_specification_verification_error_decomposition
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω)
    (hexact : wrong = specificationError ∪ jointFailureEvent fail)
    (hdisj : Disjoint specificationError (jointFailureEvent fail)) :
    eventProb b wrong =
      eventProb b specificationError + eventProb b (jointFailureEvent fail) := by
  rw [hexact]
  exact eventProb_union_of_disjoint b hdisj

/-- With exact disjoint error decomposition plus factorized verifier failures,
total wrong-result probability is exactly specification error plus the product
of verifier failure probabilities. -/
theorem exact_error_decomposition_with_factorized_verifiers
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω)
    (hexact : wrong = specificationError ∪ jointFailureEvent fail)
    (hdisj : Disjoint specificationError (jointFailureEvent fail))
    (hfactor : JointFailureFactorizes b fail) :
    eventProb b wrong =
      eventProb b specificationError + ∏ v, eventProb b (fail v) := by
  rw [exact_specification_verification_error_decomposition
    b wrong specificationError fail hexact hdisj]
  rw [hfactor]

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v

/-- No verifier ensemble can drive total wrong-result probability strictly below
a shared-specification event that is itself always wrong. -/
theorem cannot_beat_shared_specification_floor
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    {specificationError wrong : Finset Ω}
    (hfloor : specificationError ⊆ wrong) :
    ¬ eventProb b wrong < eventProb b specificationError := by
  exact not_lt_of_ge (shared_specification_error_is_lower_bound b hfloor)

/-- Constant-marginal factorized ensemble: the total error is sandwiched between
the shared specification rate and that rate plus `δ^n`. -/
theorem constant_rate_verifier_ensemble_sandwich
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω) (δ : ℚ)
    (hfloor : specificationError ⊆ wrong)
    (hcover : WrongCoveredBySpecificationOrVerification wrong specificationError fail)
    (hfactor : JointFailureFactorizes b fail)
    (hmarginal : ∀ v, eventProb b (fail v) = δ) :
    eventProb b specificationError ≤ eventProb b wrong ∧
      eventProb b wrong ≤
        eventProb b specificationError + δ ^ Fintype.card V := by
  constructor
  · exact shared_specification_error_is_lower_bound b hfloor
  · exact wrong_probability_le_specification_plus_power
      b wrong specificationError fail δ hcover hfactor hmarginal

/-- Under exact disjoint error decomposition and constant factorized verifier
failure rate, total error is exactly specification error plus `δ^n`. -/
theorem exact_constant_rate_error_decomposition
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    {V : Type v} [Fintype V]
    (b : RationalBelief Ω)
    (wrong specificationError : Finset Ω)
    (fail : V → Finset Ω) (δ : ℚ)
    (hexact : wrong = specificationError ∪ jointFailureEvent fail)
    (hdisj : Disjoint specificationError (jointFailureEvent fail))
    (hfactor : JointFailureFactorizes b fail)
    (hmarginal : ∀ v, eventProb b (fail v) = δ) :
    eventProb b wrong =
      eventProb b specificationError + δ ^ Fintype.card V := by
  rw [exact_error_decomposition_with_factorized_verifiers
    b wrong specificationError fail hexact hdisj hfactor]
  have hprod := Finset.prod_eq_pow_card
    (s := (Finset.univ : Finset V))
    (f := fun v => eventProb b (fail v))
    (b := δ)
    (by
      intro v hv
      exact hmarginal v)
  simpa using hprod

end Komorebi.AVOC
