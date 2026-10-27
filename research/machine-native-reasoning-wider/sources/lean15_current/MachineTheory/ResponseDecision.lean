import MachineTheory.ApproximateDecision
import Mathlib.Topology.MetricSpace.Basic

/-!
Core 4.1: one probability record and one paired response approximation support
one bounded decision. A change in the loss function, model set or evidence record
is not silently included in either allowance. All risks are exact model risks.
-/
namespace Komorebi.MachineTheory.ResponseDecision
open scoped BigOperators
open Instrument Variation ApproximateDecision
noncomputable section
variable {X I V : Type*}

/-- The loss is evaluated at the actual response in each represented world. -/
def responseRisk [Fintype X] (p : X → ℝ) (v : X → V)
    (loss : I → V → ℝ) (i : I) : ℝ := risk p (fun x => loss i (v x))

/-- The exact expected loss discrepancy at a fixed probability record. -/
theorem loss_change_bound [Fintype X] (p f g : X → ℝ) (hp : ∀ x, 0 ≤ p x) :
    |risk p f - risk p g| ≤ ∑ x, |f x-g x| * p x := by
  calc
    |risk p f-risk p g| = |∑ x, (f x-g x)*p x| := by
      simp only [risk, Finset.sum_sub_distrib, sub_mul]
    _ ≤ ∑ x, |(f x-g x)*p x| := Finset.abs_sum_le_sum_abs _ _
    _ = _ := by simp only [abs_mul, abs_of_nonneg (hp _)]

theorem loss_change_uniform [Fintype X] (p f g : X → ℝ) (hp : IsDist p)
    (r : ℝ) (hr : ∀ x, |f x-g x| ≤ r) : |risk p f-risk p g| ≤ r := by
  calc
    _ ≤ ∑ x, |f x-g x| * p x := loss_change_bound p f g hp.1
    _ ≤ ∑ x, r*p x := Finset.sum_le_sum
      (fun x _ => mul_le_mul_of_nonneg_right (hr x) (hp.1 x))
    _ = r := by rw [← Finset.mul_sum]; change r * mass p = r; rw [hp.2, mul_one]

/-- Clipping a proved error allowance to the actual loss range does not weaken it. -/
def allowance (e K d : ℝ) : ℝ := min 1 (e+K*d)

theorem allowance_nonneg (e K d : ℝ) (he : 0 ≤ e) (hK : 0 ≤ K) (hd : 0 ≤ d) :
    0 ≤ allowance e K d := le_min (by norm_num) (add_nonneg he (mul_nonneg hK hd))

theorem response_risk_range [Fintype X] (p : X → ℝ) (v : X → V)
    (loss : I → V → ℝ) (i : I) (hp : IsDist p)
    (hl : ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1) :
    0 ≤ responseRisk p v loss i ∧ responseRisk p v loss i ≤ 1 :=
  risk_range p _ hp 1 hl

/-- The algebraic core allows a directly proved loss discrepancy without a metric. -/
theorem record_and_loss_error [Fintype X] (p q f g : X → ℝ)
    (hp : IsDist p) (hq : IsDist q) (e r : ℝ)
    (he : tv p q ≤ e) (hr : ∀ x, |f x-g x| ≤ r)
    (hf : ∀ x, 0 ≤ f x ∧ f x ≤ 1) (hg : ∀ x, 0 ≤ g x ∧ g x ≤ 1) :
    |risk p f-risk q g| ≤ min 1 (e+r) := by
  apply le_min
  · have h1 := risk_range p f hp 1 hf
    have h2 := risk_range q g hq 1 hg
    exact abs_le.mpr ⟨by linarith, by linarith⟩
  · calc
      _ ≤ |risk p f-risk p g| + |risk p g-risk q g| := abs_sub_le _ _ _
      _ ≤ r + 1*e := add_le_add (loss_change_uniform p f g hp r hr)
        (same_policy_error p q g hp hq 1 e (by norm_num) hg he)
      _ = e+r := by ring

/-- Core 4.1, uniform response form. Bounds on attained responses suffice. -/
theorem decision_error [Fintype X] [PseudoMetricSpace V]
    (p q : X → ℝ) (v w : X → V) (loss : I → V → ℝ) (i : I)
    (hp : IsDist p) (hq : IsDist q) (e K d : ℝ) (hK : 0 ≤ K)
    (he : tv p q ≤ e) (hd : ∀ x, dist (v x) (w x) ≤ d)
    (hlip : ∀ x, |loss i (v x)-loss i (w x)| ≤ K*dist (v x) (w x))
    (hv : ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (hw : ∀ x, 0 ≤ loss i (w x) ∧ loss i (w x) ≤ 1) :
    |responseRisk p v loss i-responseRisk q w loss i| ≤ allowance e K d := by
  exact record_and_loss_error p q _ _ hp hq e (K*d) he
    (fun x => (hlip x).trans (mul_le_mul_of_nonneg_left (hd x) hK)) hv hw

/-- Global bounded Lipschitz losses specialize to the exact source theorem. -/
theorem decision_error_global [Fintype X] [PseudoMetricSpace V]
    (p q : X → ℝ) (v w : X → V) (loss : I → V → ℝ)
    (hp : IsDist p) (hq : IsDist q) (e K d : ℝ) (hK : 0 ≤ K)
    (he : tv p q ≤ e) (hd : ∀ x, dist (v x) (w x) ≤ d)
    (hlip : ∀ i y z, |loss i y-loss i z| ≤ K*dist y z)
    (hl : ∀ i y, 0 ≤ loss i y ∧ loss i y ≤ 1) (i : I) :
    |responseRisk p v loss i-responseRisk q w loss i| ≤ allowance e K d :=
  decision_error p q v w loss i hp hq e K d hK he hd
    (fun x => hlip i (v x) (w x)) (fun x => hl i (v x)) (fun x => hl i (w x))

/-- A data-dependent allocation of response error can be charged by its expected value. -/
theorem expected_response_error [Fintype X] [PseudoMetricSpace V]
    (p q : X → ℝ) (v w : X → V) (loss : I → V → ℝ) (i : I)
    (hp : IsDist p) (hq : IsDist q) (e K d : ℝ) (hK : 0 ≤ K)
    (he : tv p q ≤ e) (hd : (∑ x, dist (v x) (w x)*p x) ≤ d)
    (hlip : ∀ x, |loss i (v x)-loss i (w x)| ≤ K*dist (v x) (w x))
    (hv : ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (hw : ∀ x, 0 ≤ loss i (w x) ∧ loss i (w x) ≤ 1) :
    |responseRisk p v loss i-responseRisk q w loss i| ≤ allowance e K d := by
  have hresponse : |responseRisk p v loss i-responseRisk p w loss i| ≤ K*d := by
    calc
      _ ≤ ∑ x, |loss i (v x)-loss i (w x)| * p x := loss_change_bound p _ _ hp.1
      _ ≤ ∑ x, (K*dist (v x) (w x))*p x := Finset.sum_le_sum
        (fun x _ => mul_le_mul_of_nonneg_right (hlip x) (hp.1 x))
      _ = K * ∑ x, dist (v x) (w x)*p x := by simp only [Finset.mul_sum, mul_assoc]
      _ ≤ K*d := mul_le_mul_of_nonneg_left hd hK
  apply le_min
  · have hv' := response_risk_range p v loss i hp hv
    have hw' := response_risk_range q w loss i hq hw
    exact abs_le.mpr ⟨by linarith, by linarith⟩
  · have hprob := same_policy_error p q (fun x => loss i (w x)) hp hq 1 e (by norm_num) hw he
    have htri := abs_sub_le (responseRisk p v loss i) (responseRisk p w loss i) (responseRisk q w loss i)
    change |responseRisk p w loss i-responseRisk q w loss i| ≤ 1*e at hprob
    linarith

/-- Core 4.1's regret claim, against any member of the same action catalogue. -/
theorem selected_regret [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (S : Finset I) (hp : IsDist p) (ξ : ℝ)
    (hv : ∀ i ∈ S, ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (herr : ∀ i ∈ S, |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ)
    (chosen best : I) (hc : chosen ∈ S) (hb : best ∈ S)
    (hopt : ∀ i ∈ S, responseRisk q w loss chosen ≤ responseRisk q w loss i) :
    responseRisk p v loss chosen-responseRisk p v loss best ≤ min 1 (2*ξ) :=
  regret_from_uniform_error _ _ S 1 ξ
    (fun i hi => response_risk_range p v loss i hp (hv i hi)) herr chosen best hc hb hopt

/-- Both minimizers exist over the actual finite nonempty catalogue. -/
theorem minimizing_decisions_exist [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (S : Finset I) (hS : S.Nonempty) (hp : IsDist p) (ξ : ℝ)
    (hv : ∀ i ∈ S, ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (herr : ∀ i ∈ S, |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ) :
    ∃ chosen ∈ S, ∃ best ∈ S,
      (∀ i ∈ S, responseRisk q w loss chosen ≤ responseRisk q w loss i) ∧
      (∀ i ∈ S, responseRisk p v loss best ≤ responseRisk p v loss i) ∧
      responseRisk p v loss chosen-responseRisk p v loss best ≤ min 1 (2*ξ) := by
  obtain ⟨c,hc,ec⟩ := Planning.finiteMin_attained S hS (responseRisk q w loss)
  obtain ⟨b,hb,eb⟩ := Planning.finiteMin_attained S hS (responseRisk p v loss)
  have hcmin : ∀ i ∈ S, responseRisk q w loss c ≤ responseRisk q w loss i := by
    intro i hi; rw [ec]; exact Planning.finiteMin_le S hS _ i hi
  refine ⟨c,hc,b,hb,hcmin,?_,selected_regret p q v w loss S hp ξ hv herr c b hc hb hcmin⟩
  intro i hi; rw [eb]; exact Planning.finiteMin_le S hS _ i hi

/-- Source-form regret against the actual finite minimum, not a supplied optimum value. -/
theorem regret_to_minimum [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (S : Finset I) (hS : S.Nonempty) (hp : IsDist p) (ξ : ℝ)
    (hv : ∀ i ∈ S, ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (herr : ∀ i ∈ S, |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ)
    (chosen : I) (hc : chosen ∈ S)
    (hopt : ∀ i ∈ S, responseRisk q w loss chosen ≤ responseRisk q w loss i) :
    responseRisk p v loss chosen-Planning.finiteMin S hS (responseRisk p v loss) ≤ min 1 (2*ξ) := by
  obtain ⟨b,hb,eb⟩ := Planning.finiteMin_attained S hS (responseRisk p v loss)
  rw [← eb]
  exact selected_regret p q v w loss S hp ξ hv herr chosen b hc hb hopt

/-- All parts of the source estimate supply actual minimizing decisions over a common catalogue. -/
theorem metric_minimizers_exist [Fintype X] [PseudoMetricSpace V]
    (p q : X → ℝ) (v w : X → V) (loss : I → V → ℝ) (S : Finset I) (hS : S.Nonempty)
    (hp : IsDist p) (hq : IsDist q) (e K d : ℝ) (hK : 0 ≤ K)
    (he : tv p q ≤ e) (hd : ∀ x, dist (v x) (w x) ≤ d)
    (hlip : ∀ i ∈ S, ∀ x, |loss i (v x)-loss i (w x)| ≤ K*dist (v x) (w x))
    (hv : ∀ i ∈ S, ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (hw : ∀ i ∈ S, ∀ x, 0 ≤ loss i (w x) ∧ loss i (w x) ≤ 1) :
    ∃ chosen ∈ S, ∃ best ∈ S,
      (∀ i ∈ S, responseRisk q w loss chosen ≤ responseRisk q w loss i) ∧
      (∀ i ∈ S, responseRisk p v loss best ≤ responseRisk p v loss i) ∧
      responseRisk p v loss chosen-responseRisk p v loss best ≤ min 1 (2*allowance e K d) :=
  minimizing_decisions_exist p q v w loss S hS hp (allowance e K d) hv
    (fun i hi => decision_error p q v w loss i hp hq e K d hK he hd (hlip i hi) (hv i hi) (hw i hi))

/-- The strict factor-two gap excludes every other true minimizer. -/
theorem unique_minimizer_transfer [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (S : Finset I) (ξ : ℝ) (chosen : I) (hc : chosen ∈ S)
    (herr : ∀ i ∈ S, |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ)
    (hgap : ∀ i ∈ S, i ≠ chosen → responseRisk q w loss chosen+2*ξ < responseRisk q w loss i) :
    (∀ i ∈ S, i ≠ chosen → responseRisk p v loss chosen < responseRisk p v loss i) ∧
    (∀ i ∈ S, (∀ j ∈ S, responseRisk p v loss i ≤ responseRisk p v loss j) → i=chosen) := by
  have hs : ∀ i ∈ S, i ≠ chosen → responseRisk p v loss chosen < responseRisk p v loss i := by
    intro i hi hne
    exact robust_gap _ _ chosen i ξ (herr chosen hc) (herr i hi) (hgap i hi hne)
  refine ⟨hs,?_⟩
  intro i hi hmin
  by_contra hne
  exact (not_le_of_gt (hs i hi hne)) (hmin chosen hc)

/-- A bounded risk interval, not a claim that a model covers the physical world. -/
theorem risk_interval [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (i : I) (hp : IsDist p) (ξ : ℝ)
    (hv : ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (herr : |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ) :
    max 0 (responseRisk q w loss i-ξ) ≤ responseRisk p v loss i ∧
    responseRisk p v loss i ≤ min 1 (responseRisk q w loss i+ξ) := by
  have hr := response_risk_range p v loss i hp hv
  have he := abs_le.mp herr
  exact ⟨max_le hr.1 (by linarith), le_min hr.2 (by linarith)⟩

theorem risk_threshold [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (i : I) (ξ τ : ℝ)
    (herr : |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ)
    (hpass : responseRisk q w loss i+ξ ≤ τ) : responseRisk p v loss i ≤ τ := by
  have h := (abs_le.mp herr).2
  linarith

/-- An optimizer with certified additive residual eta has its own additional charge. -/
theorem approximate_optimizer_regret [Fintype X] (p q : X → ℝ) (v w : X → V)
    (loss : I → V → ℝ) (S : Finset I) (hp : IsDist p) (ξ η : ℝ)
    (hv : ∀ i ∈ S, ∀ x, 0 ≤ loss i (v x) ∧ loss i (v x) ≤ 1)
    (herr : ∀ i ∈ S, |responseRisk p v loss i-responseRisk q w loss i| ≤ ξ)
    (chosen best : I) (hc : chosen ∈ S) (hb : best ∈ S)
    (hopt : ∀ i ∈ S, responseRisk q w loss chosen ≤ responseRisk q w loss i+η) :
    responseRisk p v loss chosen-responseRisk p v loss best ≤ min 1 (2*ξ+η) := by
  have h1 := (abs_le.mp (herr chosen hc)).2
  have h2 := (abs_le.mp (herr best hb)).1
  have h3 := hopt best hb
  have hc' := response_risk_range p v loss chosen hp (hv chosen hc)
  have hb' := response_risk_range p v loss best hp (hv best hb)
  exact le_min (by linarith) (by linarith)

end
end Komorebi.MachineTheory.ResponseDecision
