import AVOC.BayesianObservationTransport
import AVOC.GuardedModelError

namespace Komorebi.AVOC.Guarded

variable {Ω M S A O : Type*} [Fintype Ω] [Fintype O] [DecidableEq A]

/-- A model state retains exact discrete metadata alongside its approximate
belief. State-dependent experiments are permitted. Matching metadata on each
observation branch is an explicit condition, not a consequence of belief closeness. -/
structure BayesianStepLink (raw : System S A O)
    (model : System (RationalBelief Ω × M) A O)
    (phi : S → RationalBelief Ω × M) (belief : S → RationalBelief Ω) where
  rawExperiment : S → A → RationalChannel Ω O
  modelExperiment : (RationalBelief Ω × M) → A → RationalChannel Ω O
  raw_prob : ∀ s a o, raw.prob s a o = predictiveProb (belief s) (rawExperiment s a) o
  model_prob : ∀ s a o, model.prob (phi s) a o =
    predictiveProb (phi s).1 (modelExperiment (phi s) a) o
  model_posterior : ∀ s a o, (model.step (phi s) a o).1 =
    bayesUpdateTotal (phi s).1 (modelExperiment (phi s) a) o
  metadata_match : ∀ s a o, a ∈ raw.actions s →
    (phi (raw.step s a o)).2 = (model.step (phi s) a o).2

/-- Quantitative bridge from prior/channel/codec errors to continuation error.
The raw next-state belief may be re-quantized; chi controls its expected error.
No posterior-evidence floor and no total-variation continuity on belief-state
Dirac laws is used. -/
theorem bayesian_link_expectation_error (raw : System S A O)
    (model : System (RationalBelief Ω × M) A O)
    (phi : S → RationalBelief Ω × M) (belief : S → RationalBelief Ω)
    (link : BayesianStepLink raw model phi belief)
    (W : (RationalBelief Ω × M) → ℚ)
    (L R alpha beta chi : ℚ) (hL : 0 ≤ L) (hR : 0 ≤ R)
    (hLip : ∀ m b c, |W (b, m) - W (c, m)| ≤ L * beliefL1Distance b c)
    (hbound : ∀ z, |W z| ≤ R)
    (s : S) (a : A) (ha : a ∈ raw.actions s)
    (hb : beliefL1Distance (belief s) (phi s).1 ≤ alpha)
    (hE : ∀ w, (∑ o, |(link.rawExperiment s a).prob w o -
      (link.modelExperiment (phi s) a).prob w o|) ≤ beta)
    (hcodec : (∑ o, raw.prob s a o * beliefL1Distance
      (phi (raw.step s a o)).1 (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)) ≤ chi) :
    |expectation raw (fun t => W (phi t)) s a - expectation model W (phi s) a| ≤
      L * chi + (2 * L + R) * (alpha + beta) := by
  let f : O → RationalBelief Ω → ℚ := fun o b => W (b, (model.step (phi s) a o).2)
  let mid : ℚ := ∑ o, raw.prob s a o * f o (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)
  have hfirst : |expectation raw (fun t => W (phi t)) s a - mid| ≤ L * chi := by
    have hp (o : O) : |W (phi (raw.step s a o)) -
        f o (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)| ≤
        L * beliefL1Distance (phi (raw.step s a o)).1
          (bayesUpdateTotal (belief s) (link.rawExperiment s a) o) := by
      have hh := hLip (model.step (phi s) a o).2 (phi (raw.step s a o)).1
        (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)
      have hm := link.metadata_match s a o ha
      simpa only [f, ← hm, Prod.mk.eta] using hh
    calc
      _ ≤ ∑ o, |raw.prob s a o * W (phi (raw.step s a o)) -
          raw.prob s a o * f o (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)| :=
        abs_sum_sub_sum_le_sum_abs_sub _ _
      _ = ∑ o, raw.prob s a o * |W (phi (raw.step s a o)) -
          f o (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)| := by
        apply Finset.sum_congr rfl
        intro o _
        rw [← mul_sub, abs_mul, abs_of_nonneg (raw.prob_nonneg s a o)]
      _ ≤ ∑ o, raw.prob s a o * (L * beliefL1Distance (phi (raw.step s a o)).1
          (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)) :=
        Finset.sum_le_sum (fun o _ => mul_le_mul_of_nonneg_left (hp o) (raw.prob_nonneg s a o))
      _ = L * (∑ o, raw.prob s a o * beliefL1Distance (phi (raw.step s a o)).1
          (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)) := by
        rw [Finset.mul_sum]; apply Finset.sum_congr rfl; intro o _; ring
      _ ≤ L * chi := mul_le_mul_of_nonneg_left hcodec hL
  have hsecond : |mid - expectation model W (phi s) a| ≤
      (2 * L + R) * (alpha + beta) := by
    have hh := bayesian_continuation_error_of_primitive_bounds (belief s) (phi s).1
      (link.rawExperiment s a) (link.modelExperiment (phi s) a) f L R alpha beta
      hL hR (fun o b c => hLip _ b c) (fun o b => hbound _) hb hE
    have hmodel (o : O) :
        f o (bayesUpdateTotal (phi s).1 (link.modelExperiment (phi s) a) o) =
        W (model.step (phi s) a o) := by
      dsimp [f]
      rw [← link.model_posterior s a o]
    simpa only [mid, expectation, link.raw_prob, link.model_prob, hmodel] using hh
  exact (abs_sub_le _ mid _).trans (add_le_add hfirst hsecond)

/-- A uniform belief-encoder error controls the expected next-code error when
the underlying raw update is Bayes. No full-state law L1 bound is asserted. -/
theorem codec_average_of_uniform_error (raw : System S A O)
    (phi : S → RationalBelief Ω × M) (belief : S → RationalBelief Ω)
    (E : S → A → RationalChannel Ω O) (chi : ℚ)
    (hcode : ∀ t, beliefL1Distance (belief t) (phi t).1 ≤ chi)
    (hstep : ∀ s a o, belief (raw.step s a o) = bayesUpdateTotal (belief s) (E s a) o)
    (s : S) (a : A) :
    (∑ o, raw.prob s a o * beliefL1Distance (phi (raw.step s a o)).1
      (bayesUpdateTotal (belief s) (E s a) o)) ≤ chi := by
  have hp (o : O) : beliefL1Distance (phi (raw.step s a o)).1
      (bayesUpdateTotal (belief s) (E s a) o) ≤ chi := by
    rw [← hstep]
    simpa only [beliefL1Distance, abs_sub_comm] using hcode (raw.step s a o)
  calc
    _ ≤ ∑ o, raw.prob s a o * chi :=
      Finset.sum_le_sum (fun o _ => mul_le_mul_of_nonneg_left (hp o) (raw.prob_nonneg s a o))
    _ = chi := by rw [← Finset.sum_mul, raw.prob_sum_one, one_mul]

/-- The per-stage transport contribution, in common utility units. -/
def bayesianTransportBudget (alpha beta : ℚ) (L R chi : ℕ → ℚ) (k : ℕ) : ℚ :=
  L k * chi k + (2 * L k + R k) * (alpha + beta)

/-- Primitive certificate for a compressed Bayesian model and approximate
continuation tables. All numerical assumptions concern priors, channel rows,
codec error, table regularity, rewards, or model backups -- not true Q errors. -/
structure BayesianModelCertificate (raw : System S A O)
    (model : System (RationalBelief Ω × M) A O)
    (phi : S → RationalBelief Ω × M) (belief : S → RationalBelief Ω)
    (W : ℕ → (RationalBelief Ω × M) → ℚ)
    (eps alpha beta : ℚ) (L R chi residual : ℕ → ℚ) where
  link : BayesianStepLink raw model phi belief
  actions_eq : ∀ s, raw.actions s = model.actions (phi s)
  initial : ∀ s, W 0 (phi s) = 0
  reward_error : ∀ s a, a ∈ raw.actions s → |raw.reward s a - model.reward (phi s) a| ≤ eps
  prior_error : ∀ s, beliefL1Distance (belief s) (phi s).1 ≤ alpha
  channel_error : ∀ s a, a ∈ raw.actions s → ∀ w,
    (∑ o, |(link.rawExperiment s a).prob w o - (link.modelExperiment (phi s) a).prob w o|) ≤ beta
  codec_error : ∀ k s a, a ∈ raw.actions s →
    (∑ o, raw.prob s a o * beliefL1Distance (phi (raw.step s a o)).1
      (bayesUpdateTotal (belief s) (link.rawExperiment s a) o)) ≤ chi k
  lip_nonneg : ∀ k, 0 ≤ L k
  bound_nonneg : ∀ k, 0 ≤ R k
  table_lipschitz : ∀ k m b c, |W k (b, m) - W k (c, m)| ≤ L k * beliefL1Distance b c
  table_bound : ∀ k z, |W k z| ≤ R k
  residual_error : ∀ k s, |backup model (W k) (phi s) - W (k + 1) (phi s)| ≤ residual k

theorem BayesianModelCertificate.toModelCertificate
    {raw : System S A O} {model : System (RationalBelief Ω × M) A O}
    {phi : S → RationalBelief Ω × M} {belief : S → RationalBelief Ω}
    {W : ℕ → (RationalBelief Ω × M) → ℚ} {eps alpha beta : ℚ}
    {L R chi residual : ℕ → ℚ}
    (hc : BayesianModelCertificate raw model phi belief W eps alpha beta L R chi residual) :
    ModelCertificate raw model phi W eps (bayesianTransportBudget alpha beta L R chi) residual := by
  refine ⟨hc.actions_eq, hc.initial, hc.reward_error, ?_, hc.residual_error⟩
  intro k s a ha
  exact bayesian_link_expectation_error raw model phi belief hc.link (W k)
    (L k) (R k) alpha beta (chi k) (hc.lip_nonneg k) (hc.bound_nonneg k)
    (hc.table_lipschitz k) (hc.table_bound k) s a ha (hc.prior_error s)
    (hc.channel_error s a ha) (hc.codec_error k s a ha)

/-- The formerly missing primitive Bayesian/model-to-true-feasible-Q bridge. -/
theorem bayesian_primitive_q_error
    {raw : System S A O} {model : System (RationalBelief Ω × M) A O}
    {phi : S → RationalBelief Ω × M} {belief : S → RationalBelief Ω}
    {W : ℕ → (RationalBelief Ω × M) → ℚ} {eps alpha beta : ℚ}
    {L R chi residual : ℕ → ℚ}
    (hc : BayesianModelCertificate raw model phi belief W eps alpha beta L R chi residual)
    (k : ℕ) (s : S) (a : A) (ha : a ∈ raw.actions s) :
    |qValue raw k s a - tableQ model (W k) (phi s) a| ≤
      modelQBudget eps (bayesianTransportBudget alpha beta L R chi) residual k :=
  model_q_error raw model phi W eps _ residual hc.toModelCertificate k s a ha

theorem bayesian_primitive_value_error
    {raw : System S A O} {model : System (RationalBelief Ω × M) A O}
    {phi : S → RationalBelief Ω × M} {belief : S → RationalBelief Ω}
    {W : ℕ → (RationalBelief Ω × M) → ℚ} {eps alpha beta : ℚ}
    {L R chi residual : ℕ → ℚ}
    (hc : BayesianModelCertificate raw model phi belief W eps alpha beta L R chi residual)
    (k : ℕ) (s : S) :
    |value raw k s - W k (phi s)| ≤
      modelValueBudget eps (bayesianTransportBudget alpha beta L R chi) residual k :=
  model_value_error raw model phi W eps _ residual hc.toModelCertificate k s

end Komorebi.AVOC.Guarded
