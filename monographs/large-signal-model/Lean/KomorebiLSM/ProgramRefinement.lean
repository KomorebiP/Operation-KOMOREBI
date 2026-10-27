import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Tactic.NormNum


set_option autoImplicit false

/-!
# Prior-preserving program refinement

A child is selected once for the whole record. The likelihood mixture assumed
below is the whole-record likelihood, and for prediction the joint likelihood
of that record and the predicted event. No product-of-one-step-mixtures identity
is assumed. The index sets may be infinite.
-/

namespace Komorebi.LSM.ProgramRefinement

noncomputable section

variable {J G : Type*}

/-- The prior of a child after splitting the parent's prior mass. -/
def childPrior (parentPrior : ℝ) (weight : J → ℝ) (j : J) : ℝ :=
  parentPrior * weight j

/-- The unnormalized evidence contributed by all children. -/
def childEvidence (parentPrior : ℝ) (weight likelihood : J → ℝ) : ℝ :=
  ∑' j, childPrior parentPrior weight j * likelihood j

/-- The original normalizer, with the parent distinguished from other programs. -/
def originalEvidence (otherPrior otherLikelihood : G → ℝ)
    (parentPrior parentLikelihood : ℝ) : ℝ :=
  (∑' g, otherPrior g * otherLikelihood g) + parentPrior * parentLikelihood

/-- The refined normalizer, leaving every other program unchanged. -/
def refinedEvidence (otherPrior otherLikelihood : G → ℝ)
    (parentPrior : ℝ) (weight likelihood : J → ℝ) : ℝ :=
  (∑' g, otherPrior g * otherLikelihood g) + childEvidence parentPrior weight likelihood

/-- Child prior masses remain nonnegative. -/
theorem childPrior_nonneg (parentPrior : ℝ) (weight : J → ℝ)
    (hparent : 0 ≤ parentPrior) (hweight : ∀ j, 0 ≤ weight j) (j : J) :
    0 ≤ childPrior parentPrior weight j :=
  mul_nonneg hparent (hweight j)

/-- The sum of all child prior masses is exactly the former parent mass. -/
theorem childPrior_sum (parentPrior : ℝ) (weight : J → ℝ)
    (hweight : ∑' j, weight j = 1) :
    (∑' j, childPrior parentPrior weight j) = parentPrior := by
  simp only [childPrior, tsum_mul_left, hweight, mul_one]

/-- Factoring out the original prior is legitimate for the entire infinite sum. -/
theorem childEvidence_factor (parentPrior : ℝ) (weight likelihood : J → ℝ) :
    childEvidence parentPrior weight likelihood =
      parentPrior * ∑' j, weight j * likelihood j := by
  simp only [childEvidence, childPrior, mul_assoc, tsum_mul_left]

/-- The whole-record mixture identity preserves the parent's evidence exactly. -/
theorem childEvidence_eq (parentPrior parentLikelihood : ℝ)
    (weight likelihood : J → ℝ)
    (hmixture : parentLikelihood = ∑' j, weight j * likelihood j) :
    childEvidence parentPrior weight likelihood = parentPrior * parentLikelihood := by
  rw [childEvidence_factor, ← hmixture]

/-- Splitting a parent into mixture children leaves the total evidence unchanged. -/
theorem total_evidence_unchanged (otherPrior otherLikelihood : G → ℝ)
    (parentPrior parentLikelihood : ℝ) (weight likelihood : J → ℝ)
    (hmixture : parentLikelihood = ∑' j, weight j * likelihood j) :
    refinedEvidence otherPrior otherLikelihood parentPrior weight likelihood =
      originalEvidence otherPrior otherLikelihood parentPrior parentLikelihood := by
  rw [refinedEvidence, originalEvidence, childEvidence_eq _ _ _ _ hmixture]

/-- The child posterior masses sum to the former parent's posterior mass. -/
theorem child_posterior_sum (otherPrior otherLikelihood : G → ℝ)
    (parentPrior parentLikelihood : ℝ) (weight likelihood : J → ℝ)
    (hmixture : parentLikelihood = ∑' j, weight j * likelihood j) :
    (∑' j, (childPrior parentPrior weight j * likelihood j) /
      refinedEvidence otherPrior otherLikelihood parentPrior weight likelihood) =
    (parentPrior * parentLikelihood) /
      originalEvidence otherPrior otherLikelihood parentPrior parentLikelihood := by
  rw [tsum_div_const]
  change childEvidence parentPrior weight likelihood / _ = _
  rw [childEvidence_eq _ _ _ _ hmixture,
    total_evidence_unchanged _ _ _ _ _ _ hmixture]

/-- Every other program has the same posterior mass after the split. -/
theorem other_posterior_unchanged (otherPrior otherLikelihood : G → ℝ)
    (parentPrior parentLikelihood : ℝ) (weight likelihood : J → ℝ)
    (hmixture : parentLikelihood = ∑' j, weight j * likelihood j) (g : G) :
    (otherPrior g * otherLikelihood g) /
        refinedEvidence otherPrior otherLikelihood parentPrior weight likelihood =
      (otherPrior g * otherLikelihood g) /
        originalEvidence otherPrior otherLikelihood parentPrior parentLikelihood := by
  rw [total_evidence_unchanged _ _ _ _ _ _ hmixture]

/-- Joint-likelihood mixture consistency also preserves every predictive event. -/
theorem predictive_event_unchanged (otherPrior otherLikelihood otherJoint : G → ℝ)
    (parentPrior parentLikelihood parentJoint : ℝ)
    (weight likelihood jointLikelihood : J → ℝ)
    (hmixture : parentLikelihood = ∑' j, weight j * likelihood j)
    (hjoint : parentJoint = ∑' j, weight j * jointLikelihood j) :
    refinedEvidence otherPrior otherJoint parentPrior weight jointLikelihood /
        refinedEvidence otherPrior otherLikelihood parentPrior weight likelihood =
      originalEvidence otherPrior otherJoint parentPrior parentJoint /
        originalEvidence otherPrior otherLikelihood parentPrior parentLikelihood := by
  rw [total_evidence_unchanged _ _ _ _ _ _ hjoint,
    total_evidence_unchanged _ _ _ _ _ _ hmixture]

/-- Atlas recodings with identical likelihood conserve the original evidence. -/
theorem identical_likelihood_evidence (parentPrior parentLikelihood : ℝ)
    (weight : J → ℝ) (hweight : ∑' j, weight j = 1) :
    childEvidence parentPrior weight (fun _ => parentLikelihood) =
      parentPrior * parentLikelihood := by
  rw [childEvidence_factor, tsum_mul_right, hweight, one_mul]

/-- Selecting a fixed child for the whole record differs from switching at each step. -/
theorem fixed_child_ne_stepwise_switching :
    (1 / 2 : ℝ) * (1 * 1) + (1 / 2 : ℝ) * (0 * 0) ≠
      ((1 / 2 : ℝ) * 1 + (1 / 2 : ℝ) * 0) ^ 2 := by
  norm_num

/-- The declared hypotheses of Proposition 24, including a genuine positive normalizer. -/
structure RefinementContract (G J : Type*) where
  otherPrior : G → ℝ
  otherLikelihood : G → ℝ
  parentPrior : ℝ
  parentLikelihood : ℝ
  weight : J → ℝ
  likelihood : J → ℝ
  otherPrior_nonneg : ∀ g, 0 ≤ otherPrior g
  otherLikelihood_nonneg : ∀ g, 0 ≤ otherLikelihood g
  parentPrior_nonneg : 0 ≤ parentPrior
  weight_nonneg : ∀ j, 0 ≤ weight j
  likelihood_nonneg : ∀ j, 0 ≤ likelihood j
  weight_summable : Summable weight
  weight_sum : ∑' j, weight j = 1
  otherEvidence_summable : Summable (fun g => otherPrior g * otherLikelihood g)
  weightedLikelihood_summable : Summable (fun j => weight j * likelihood j)
  whole_record_mixture : parentLikelihood = ∑' j, weight j * likelihood j
  otherPrior_summable : Summable otherPrior
  prior_normalized : (∑' g, otherPrior g) + parentPrior = 1
  normalizer_pos : 0 < originalEvidence otherPrior otherLikelihood parentPrior parentLikelihood

/-- Refined priors conserve total probability mass. -/
theorem refined_prior_normalized (c : RefinementContract G J) :
    (∑' g, c.otherPrior g) + (∑' j, childPrior c.parentPrior c.weight j) = 1 := by
  rw [childPrior_sum _ _ c.weight_sum]
  exact c.prior_normalized

/-- The refined normalizer remains strictly positive. -/
theorem refined_normalizer_pos (c : RefinementContract G J) :
    0 < refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood := by
  rw [total_evidence_unchanged _ _ _ _ _ _ c.whole_record_mixture]
  exact c.normalizer_pos

/-- The children have summable unnormalized evidence under the contract. -/
theorem child_evidence_summable (c : RefinementContract G J) :
    Summable (fun j => childPrior c.parentPrior c.weight j * c.likelihood j) := by
  simpa only [childPrior, mul_assoc] using
    c.weightedLikelihood_summable.mul_left c.parentPrior

/-- The child posterior is an actual summable nonnegative mass family. -/
theorem child_posterior_summable (c : RefinementContract G J) :
    Summable (fun j => (childPrior c.parentPrior c.weight j * c.likelihood j) /
      refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood) :=
  (child_evidence_summable c).div_const _

/-- Child posterior masses are nonnegative. -/
theorem child_posterior_nonneg (c : RefinementContract G J) (j : J) :
    0 ≤ (childPrior c.parentPrior c.weight j * c.likelihood j) /
      refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood := by
  exact div_nonneg
    (mul_nonneg (childPrior_nonneg _ _ c.parentPrior_nonneg c.weight_nonneg j)
      (c.likelihood_nonneg j)) (le_of_lt (refined_normalizer_pos c))

/-- Refined posterior masses, including all unchanged programs, sum to one. -/
theorem refined_posterior_normalized (c : RefinementContract G J) :
    (∑' g, (c.otherPrior g * c.otherLikelihood g) /
      refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood) +
    (∑' j, (childPrior c.parentPrior c.weight j * c.likelihood j) /
      refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood) = 1 := by
  rw [tsum_div_const, tsum_div_const, ← add_div]
  exact div_self (ne_of_gt (refined_normalizer_pos c))

/-- Proposition 24: prior, evidence, child posterior and other posteriors are preserved. -/
theorem prior_preserving_refinement (c : RefinementContract G J) :
    ((∑' g, c.otherPrior g) + (∑' j, childPrior c.parentPrior c.weight j) = 1) ∧
    (refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood =
      originalEvidence c.otherPrior c.otherLikelihood c.parentPrior c.parentLikelihood) ∧
    ((∑' j, (childPrior c.parentPrior c.weight j * c.likelihood j) /
        refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood) =
      (c.parentPrior * c.parentLikelihood) /
        originalEvidence c.otherPrior c.otherLikelihood c.parentPrior c.parentLikelihood) ∧
    (∀ g, (c.otherPrior g * c.otherLikelihood g) /
        refinedEvidence c.otherPrior c.otherLikelihood c.parentPrior c.weight c.likelihood =
      (c.otherPrior g * c.otherLikelihood g) /
        originalEvidence c.otherPrior c.otherLikelihood c.parentPrior c.parentLikelihood) := by
  exact ⟨refined_prior_normalized c,
    total_evidence_unchanged _ _ _ _ _ _ c.whole_record_mixture,
    child_posterior_sum _ _ _ _ _ _ c.whole_record_mixture,
    other_posterior_unchanged _ _ _ _ _ _ c.whole_record_mixture⟩

end

end Komorebi.LSM.ProgramRefinement
