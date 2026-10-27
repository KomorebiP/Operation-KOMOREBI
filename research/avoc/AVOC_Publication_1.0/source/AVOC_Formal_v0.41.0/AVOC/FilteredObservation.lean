import AVOC.BayesianObservationTransport

namespace Komorebi.AVOC.Filtered

variable {Ω O D : Type*} [Fintype Ω] [Fintype O] [Fintype D] [DecidableEq D]

/-- The public report is a deterministic function of a raw observation.  Its
likelihood sums the whole fiber, including every rejected raw observation. -/
def reportChannel (E : RationalChannel Ω O) (f : O → D) : RationalChannel Ω D where
  prob w d := ∑ o, if f o = d then E.prob w o else 0
  nonneg w d := Finset.sum_nonneg (fun o _ => by split <;> simp_all [E.nonneg])
  sum_one w := by
    rw [Finset.sum_comm]
    simpa using E.sum_one w

omit [Fintype Ω] in
theorem report_expectation (E : RationalChannel Ω O) (f : O → D)
    (w : Ω) (g : D → ℚ) :
    (∑ d, (reportChannel E f).prob w d * g d) = ∑ o, E.prob w o * g (f o) := by
  simp only [reportChannel, Finset.sum_mul, ite_mul, zero_mul]
  rw [Finset.sum_comm]
  simp

theorem predictive_report (b : RationalBelief Ω) (E : RationalChannel Ω O)
    (f : O → D) (d : D) :
    predictiveProb b (reportChannel E f) d =
      ∑ o, if f o = d then predictiveProb b E o else 0 := by
  unfold predictiveProb
  simp only [reportChannel, Finset.mul_sum, mul_ite, mul_zero]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro o _
  by_cases h : f o = d <;> simp [h]

theorem predictive_report_expectation (b : RationalBelief Ω)
    (E : RationalChannel Ω O) (f : O → D) (g : D → ℚ) :
    (∑ d, predictiveProb b (reportChannel E f) d * g d) =
      ∑ o, predictiveProb b E o * g (f o) := by
  simp_rw [predictive_report]
  simp only [Finset.sum_mul, ite_mul, zero_mul]
  rw [Finset.sum_comm]
  simp

/-- Total, division-free posterior identity. A report posterior averages the raw
posteriors in its fiber, not the posterior of an arbitrarily chosen raw event. -/
theorem posterior_report_scaled (b : RationalBelief Ω) (E : RationalChannel Ω O)
    (f : O → D) (d : D) (w : Ω) :
    predictiveProb b (reportChannel E f) d *
        (bayesUpdateTotal b (reportChannel E f) d).prob w =
      ∑ o, if f o = d then predictiveProb b E o * (bayesUpdateTotal b E o).prob w else 0 := by
  simp_rw [total_posterior_scaled]
  simp only [reportChannel, Finset.mul_sum, mul_ite, mul_zero]

theorem posterior_report_mixture (b : RationalBelief Ω) (E : RationalChannel Ω O)
    (f : O → D) (d : D) (w : Ω)
    (h : 0 < predictiveProb b (reportChannel E f) d) :
    (bayesUpdateTotal b (reportChannel E f) d).prob w =
      (∑ o, if f o = d then predictiveProb b E o *
        (bayesUpdateTotal b E o).prob w else 0) / predictiveProb b (reportChannel E f) d := by
  apply (eq_div_iff (ne_of_gt h)).2
  rw [mul_comm]
  exact posterior_report_scaled b E f d w

omit [Fintype Ω] in
/-- Rejection is an ordinary public report with all of its preimage mass. -/
theorem rejection_likelihood (E : RationalChannel Ω O) (f : O → Bool) (w : Ω) :
    (reportChannel E f).prob w false = ∑ o, if f o = false then E.prob w o else 0 := rfl

/-- A finite one-point observation law, used for the deterministic workflow stages. -/
def silentChannel (d : D) : RationalChannel Ω D where
  prob _ e := if d = e then 1 else 0
  nonneg _ _ := by split <;> norm_num
  sum_one _ := by simp

theorem silent_predictive (b : RationalBelief Ω) (d e : D) :
    predictiveProb b (silentChannel (Ω := Ω) d) e = if d = e then 1 else 0 := by
  unfold predictiveProb silentChannel
  by_cases h : d = e <;> simp [h, b.sum_one]

theorem silent_posterior (b : RationalBelief Ω) (d e : D) :
    bayesUpdateTotal b (silentChannel (Ω := Ω) d) e = b := by
  by_cases h : d = e
  · subst e
    apply RationalBelief.ext
    intro w
    have hs := total_posterior_scaled b (silentChannel (Ω := Ω) d) d w
    rw [silent_predictive] at hs
    simpa [silentChannel] using hs
  · simp [bayesUpdateTotal, silent_predictive, h]

end Komorebi.AVOC.Filtered
