import AVOC.ApproximateBayesian

set_option maxHeartbeats 400000

namespace Komorebi.AVOC

variable {Ω O : Type*} [Fintype Ω] [Fintype O]

/-- Distance between the two joint world/observation laws. This is full L1,
not half-scaled total variation and not L1 on the space of posterior states. -/
def jointObservationL1 (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) : ℚ :=
  ∑ o, ∑ w, |b.prob w * E.prob w o - c.prob w * F.prob w o|

theorem jointObservationL1_nonneg (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) : 0 ≤ jointObservationL1 b c E F := by
  exact Finset.sum_nonneg (fun _ _ => Finset.sum_nonneg (fun _ _ => abs_nonneg _))

/-- Bayes' scaled identity remains valid with the total zero-evidence fallback. -/
theorem total_posterior_scaled (b : RationalBelief Ω) (E : RationalChannel Ω O)
    (o : O) (w : Ω) :
    predictiveProb b E o * (bayesUpdateTotal b E o).prob w = b.prob w * E.prob w o := by
  by_cases hp : 0 < predictiveProb b E o
  · rw [bayesUpdateTotal_eq_of_pos b E o hp, mul_comm]
    exact bayesUpdate_mul_predictive b E o hp w
  · have hz := predictiveProb_eq_zero_of_not_pos b E o hp
    have hn := bayesNumerator_eq_zero_of_predictive_eq_zero b E o hz w
    change b.prob w * E.prob w o = 0 at hn
    rw [hz, zero_mul, hn]

/-- A division-free normalization estimate. Weighting the distance by the first
mass eliminates the reciprocal evidence denominator, including zero masses. -/
theorem mass_weighted_belief_l1 (b c : RationalBelief Ω) (p q : ℚ) (hp : 0 ≤ p) :
    p * beliefL1Distance b c ≤
      (∑ w, |p * b.prob w - q * c.prob w|) + |p - q| := by
  have hpoint (w : Ω) : p * |b.prob w - c.prob w| ≤
      |p * b.prob w - q * c.prob w| + |p - q| * c.prob w := by
    calc
      p * |b.prob w - c.prob w| = |p * (b.prob w - c.prob w)| := by
        rw [abs_mul, abs_of_nonneg hp]
      _ = |(p * b.prob w - q * c.prob w) + (q - p) * c.prob w| := by
        congr 1; ring
      _ ≤ |p * b.prob w - q * c.prob w| + |(q - p) * c.prob w| := abs_add_le _ _
      _ = |p * b.prob w - q * c.prob w| + |p - q| * c.prob w := by
        rw [abs_mul, abs_of_nonneg (c.nonneg w), abs_sub_comm q p]
  calc
    p * beliefL1Distance b c = ∑ w, p * |b.prob w - c.prob w| := by
      simp only [beliefL1Distance, Finset.mul_sum]
    _ ≤ ∑ w, (|p * b.prob w - q * c.prob w| + |p - q| * c.prob w) :=
      Finset.sum_le_sum (fun w _ => hpoint w)
    _ = _ := by rw [Finset.sum_add_distrib, ← Finset.mul_sum, c.sum_one, mul_one]

theorem predictive_l1_le_joint (b c : RationalBelief Ω) (E F : RationalChannel Ω O) :
    (∑ o, |predictiveProb b E o - predictiveProb c F o|) ≤
      jointObservationL1 b c E F := by
  apply Finset.sum_le_sum
  intro o _
  exact abs_sum_sub_sum_le_sum_abs_sub (fun w => b.prob w * E.prob w o)
    (fun w => c.prob w * F.prob w o)

/-- Average posterior error, under the true predictive law. No positive-evidence
floor is assumed. This does not bound the posterior error of each rare branch. -/
theorem expected_posterior_l1_le_two_joint (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) :
    (∑ o, predictiveProb b E o *
      beliefL1Distance (bayesUpdateTotal b E o) (bayesUpdateTotal c F o)) ≤
      2 * jointObservationL1 b c E F := by
  have hpoint (o : O) := mass_weighted_belief_l1
    (bayesUpdateTotal b E o) (bayesUpdateTotal c F o)
    (predictiveProb b E o) (predictiveProb c F o) (predictiveProb_nonneg b E o)
  have hsum := Finset.sum_le_sum (s := Finset.univ) (fun o _ => hpoint o)
  simp_rw [total_posterior_scaled] at hsum
  rw [Finset.sum_add_distrib] at hsum
  have hm := predictive_l1_le_joint b c E F
  change _ ≤ jointObservationL1 b c E F + _ at hsum
  linarith

/-- Primitive prior and channel-row errors bound the joint observation error. -/
theorem joint_l1_le_prior_add_channel (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) (alpha beta : ℚ)
    (hb : beliefL1Distance b c ≤ alpha)
    (hE : ∀ w, (∑ o, |E.prob w o - F.prob w o|) ≤ beta) :
    jointObservationL1 b c E F ≤ alpha + beta := by
  have hpoint (w : Ω) (o : O) :
      |b.prob w * E.prob w o - c.prob w * F.prob w o| ≤
      |b.prob w - c.prob w| * E.prob w o +
        c.prob w * |E.prob w o - F.prob w o| := by
    calc
      _ = |(b.prob w - c.prob w) * E.prob w o +
            c.prob w * (E.prob w o - F.prob w o)| := by congr 1; ring
      _ ≤ |(b.prob w - c.prob w) * E.prob w o| +
          |c.prob w * (E.prob w o - F.prob w o)| := abs_add_le _ _
      _ = _ := by rw [abs_mul, abs_mul, abs_of_nonneg (E.nonneg w o),
        abs_of_nonneg (c.nonneg w)]
  calc
    jointObservationL1 b c E F = ∑ w, ∑ o,
        |b.prob w * E.prob w o - c.prob w * F.prob w o| := by
      unfold jointObservationL1; rw [Finset.sum_comm]
    _ ≤ ∑ w, ∑ o, (|b.prob w - c.prob w| * E.prob w o +
        c.prob w * |E.prob w o - F.prob w o|) := by
      exact Finset.sum_le_sum (fun w _ => Finset.sum_le_sum (fun o _ => hpoint w o))
    _ = beliefL1Distance b c +
        ∑ w, c.prob w * (∑ o, |E.prob w o - F.prob w o|) := by
      simp_rw [Finset.sum_add_distrib, ← Finset.mul_sum, E.sum_one, mul_one]
      rfl
    _ ≤ alpha + beta := by
      apply add_le_add hb
      calc
        _ ≤ ∑ w, c.prob w * beta :=
          Finset.sum_le_sum (fun w _ => mul_le_mul_of_nonneg_left (hE w) (c.nonneg w))
        _ = beta := by rw [← Finset.sum_mul, c.sum_one, one_mul]

/-- Separate paired-value distortion and observation-law distortion. -/
theorem observation_expectation_transport (p q f g : O → ℚ) (R : ℚ)
    (hp : ∀ o, 0 ≤ p o) (hg : ∀ o, |g o| ≤ R) :
    |(∑ o, p o * f o) - ∑ o, q o * g o| ≤
      (∑ o, p o * |f o - g o|) + R * (∑ o, |p o - q o|) := by
  have hpoint (o : O) : |p o * f o - q o * g o| ≤
      p o * |f o - g o| + |p o - q o| * R := by
    calc
      _ = |p o * (f o - g o) + (p o - q o) * g o| := by congr 1; ring
      _ ≤ |p o * (f o - g o)| + |(p o - q o) * g o| := abs_add_le _ _
      _ = p o * |f o - g o| + |p o - q o| * |g o| := by
        rw [abs_mul, abs_mul, abs_of_nonneg (hp o)]
      _ ≤ p o * |f o - g o| + |p o - q o| * R := by
        exact add_le_add le_rfl (mul_le_mul_of_nonneg_left (hg o)
          (abs_nonneg (p o - q o)))
  calc
    _ ≤ ∑ o, |p o * f o - q o * g o| :=
      abs_sum_sub_sum_le_sum_abs_sub (fun o => p o * f o) (fun o => q o * g o)
    _ ≤ ∑ o, (p o * |f o - g o| + |p o - q o| * R) :=
      Finset.sum_le_sum (fun o _ => hpoint o)
    _ = _ := by rw [Finset.sum_add_distrib, ← Finset.sum_mul]; ring

/-- The needed bridge is a bound on expected continuation value, not a claim
that nearby beliefs induce nearby atomic laws in total variation. -/
theorem bayesian_continuation_error (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) (f : O → RationalBelief Ω → ℚ)
    (L R : ℚ) (hL : 0 ≤ L) (hR : 0 ≤ R)
    (hLip : ∀ o x y, |f o x - f o y| ≤ L * beliefL1Distance x y)
    (hbound : ∀ o x, |f o x| ≤ R) :
    |(∑ o, predictiveProb b E o * f o (bayesUpdateTotal b E o)) -
      ∑ o, predictiveProb c F o * f o (bayesUpdateTotal c F o)| ≤
      (2 * L + R) * jointObservationL1 b c E F := by
  have he := observation_expectation_transport
    (fun o => predictiveProb b E o) (fun o => predictiveProb c F o)
    (fun o => f o (bayesUpdateTotal b E o))
    (fun o => f o (bayesUpdateTotal c F o)) R
    (predictiveProb_nonneg b E) (fun o => hbound o _)
  have hp := expected_posterior_l1_le_two_joint b c E F
  have hm := predictive_l1_le_joint b c E F
  have hs : (∑ o, predictiveProb b E o *
      |f o (bayesUpdateTotal b E o) - f o (bayesUpdateTotal c F o)|) ≤
      L * (2 * jointObservationL1 b c E F) := by
    calc
      _ ≤ ∑ o, predictiveProb b E o *
          (L * beliefL1Distance (bayesUpdateTotal b E o) (bayesUpdateTotal c F o)) :=
        Finset.sum_le_sum (fun o _ => mul_le_mul_of_nonneg_left
          (hLip o _ _) (predictiveProb_nonneg b E o))
      _ = L * (∑ o, predictiveProb b E o *
          beliefL1Distance (bayesUpdateTotal b E o) (bayesUpdateTotal c F o)) := by
        rw [Finset.mul_sum]; apply Finset.sum_congr rfl; intro o _; ring
      _ ≤ _ := mul_le_mul_of_nonneg_left hp hL
  have hh := mul_le_mul_of_nonneg_left hm hR
  linarith

theorem bayesian_continuation_error_of_primitive_bounds (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) (f : O → RationalBelief Ω → ℚ)
    (L R alpha beta : ℚ) (hL : 0 ≤ L) (hR : 0 ≤ R)
    (hLip : ∀ o x y, |f o x - f o y| ≤ L * beliefL1Distance x y)
    (hbound : ∀ o x, |f o x| ≤ R)
    (hb : beliefL1Distance b c ≤ alpha)
    (hE : ∀ w, (∑ o, |E.prob w o - F.prob w o|) ≤ beta) :
    |(∑ o, predictiveProb b E o * f o (bayesUpdateTotal b E o)) -
      ∑ o, predictiveProb c F o * f o (bayesUpdateTotal c F o)| ≤
      (2 * L + R) * (alpha + beta) := by
  apply (bayesian_continuation_error b c E F f L R hL hR hLip hbound).trans
  exact mul_le_mul_of_nonneg_left (joint_l1_le_prior_add_channel b c E F alpha beta hb hE)
    (by linarith)

/-- Primitive error corollary for the predictive observation law. -/
theorem predictive_l1_of_primitive_bounds (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) (alpha beta : ℚ)
    (hb : beliefL1Distance b c ≤ alpha)
    (hE : ∀ w, (∑ o, |E.prob w o - F.prob w o|) ≤ beta) :
    (∑ o, |predictiveProb b E o - predictiveProb c F o|) ≤ alpha + beta :=
  (predictive_l1_le_joint b c E F).trans
    (joint_l1_le_prior_add_channel b c E F alpha beta hb hE)

/-- Probability-weighted posterior error is controlled without reciprocal
predictive probabilities. The observation laws may have different supports. -/
theorem expected_posterior_l1_of_primitive_bounds (b c : RationalBelief Ω)
    (E F : RationalChannel Ω O) (alpha beta : ℚ)
    (hb : beliefL1Distance b c ≤ alpha)
    (hE : ∀ w, (∑ o, |E.prob w o - F.prob w o|) ≤ beta) :
    (∑ o, predictiveProb b E o *
      beliefL1Distance (bayesUpdateTotal b E o) (bayesUpdateTotal c F o)) ≤ 2 * (alpha + beta) := by
  apply (expected_posterior_l1_le_two_joint b c E F).trans
  exact mul_le_mul_of_nonneg_left (joint_l1_le_prior_add_channel b c E F alpha beta hb hE)
    (by norm_num)

end Komorebi.AVOC
