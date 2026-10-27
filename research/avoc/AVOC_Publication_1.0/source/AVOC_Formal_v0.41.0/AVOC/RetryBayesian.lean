import AVOC.RetryControl
import AVOC.BayesianEvidence

namespace Komorebi.AVOC.RetryBayesian

/-- Persistent operational reliability types, not probabilities that the task is true.
Repeated attempts are conditionally independent given the type. No repairs, backoff,
changing providers, or state-dependent success gains are represented here. -/
structure Reliability (Ω : Type*) where
  rate : Ω → ℚ
  rate_nonneg : ∀ w, 0 ≤ rate w
  rate_le_one : ∀ w, rate w ≤ 1
  fee : Nat
  benefit : ℚ
  benefit_nonneg : 0 ≤ benefit

variable {Ω : Type*} [Fintype Ω]

def mean (q : Reliability Ω) (b : RationalBelief Ω) : ℚ :=
  ∑ w, b.prob w * q.rate w

theorem mean_nonneg (q : Reliability Ω) (b : RationalBelief Ω) : 0 ≤ mean q b := by
  exact Finset.sum_nonneg (fun w _ => mul_nonneg (b.nonneg w) (q.rate_nonneg w))

theorem mean_le_one (q : Reliability Ω) (b : RationalBelief Ω) : mean q b ≤ 1 := by
  calc
    mean q b ≤ ∑ w, b.prob w := by
      apply Finset.sum_le_sum; intro w _
      exact mul_le_of_le_one_right (b.nonneg w) (q.rate_le_one w)
    _ = 1 := b.sum_one

theorem fault_mass (q : Reliability Ω) (b : RationalBelief Ω) :
    evidenceMass b (fun w => 1 - q.rate w) = 1 - mean q b := by
  simp [evidenceMass,mean,mul_sub,Finset.sum_sub_distrib,b.sum_one]

/-- A total executable operational posterior. The prior fallback is used only for
an impossible fault. The runtime rejects a supplied zero-probability fault. -/
def afterFault (q : Reliability Ω) (b : RationalBelief Ω) : RationalBelief Ω :=
  if h : 0 < evidenceMass b (fun w => 1 - q.rate w) then
    conditionByWeight b (fun w => 1 - q.rate w)
      (fun w => sub_nonneg.mpr (q.rate_le_one w)) h
  else b

theorem afterFault_formula (q : Reliability Ω) (b : RationalBelief Ω)
    (h : 0 < 1 - mean q b) (w : Ω) :
    (afterFault q b).prob w = b.prob w * (1 - q.rate w) / (1 - mean q b) := by
  have hz : 0 < evidenceMass b (fun w => 1 - q.rate w) := by rw [fault_mass]; exact h
  simp only [afterFault, dite_eq_left hz, conditionByWeight]
  rw [fault_mass]

theorem impossible_fault_fallback (q : Reliability Ω) (b : RationalBelief Ω)
    (h : mean q b = 1) : afterFault q b = b := by
  simp [afterFault,fault_mass,h]

/-- A finite weighted variance argument; no posterior monotonicity is assumed. -/
theorem second_moment_ge_mean_square (q : Reliability Ω) (b : RationalBelief Ω) :
    (mean q b)^2 ≤ ∑ w, b.prob w * (q.rate w)^2 := by
  have hn : 0 ≤ ∑ w, b.prob w * (q.rate w - mean q b)^2 :=
    Finset.sum_nonneg (fun w _ => mul_nonneg (b.nonneg w) (sq_nonneg _))
  have he : (∑ w, b.prob w * (q.rate w - mean q b)^2) =
      (∑ w, b.prob w * (q.rate w)^2) - (mean q b)^2 := by
    calc
      (∑ w, b.prob w * (q.rate w - mean q b)^2) =
        ∑ w, (b.prob w * (q.rate w)^2 - (b.prob w * q.rate w) * (2 * mean q b) +
          b.prob w * (mean q b)^2) := by apply Finset.sum_congr rfl; intro w _; ring
      _ = _ := by
        rw [Finset.sum_add_distrib,Finset.sum_sub_distrib,← Finset.sum_mul,← Finset.sum_mul,b.sum_one]
        change (∑ w, b.prob w * (q.rate w)^2) - mean q b * (2 * mean q b) + 1 * (mean q b)^2 = _
        ring
  rw [he] at hn; linarith

/-- A fault lowers the predictive chance of completing another identical attempt
in this fixed latent-type model. It does not assert this for arbitrary services. -/
theorem mean_afterFault_le (q : Reliability Ω) (b : RationalBelief Ω) :
    mean q (afterFault q b) ≤ mean q b := by
  by_cases hz : 0 < evidenceMass b (fun w => 1 - q.rate w)
  · have hpos : 0 < 1 - mean q b := by rw [← fault_mass]; exact hz
    have he : mean q (afterFault q b) =
        (mean q b - ∑ w, b.prob w * (q.rate w)^2) / (1 - mean q b) := by
      unfold mean at ⊢
      simp_rw [afterFault_formula q b hpos]
      calc
        (∑ w, (b.prob w * (1 - q.rate w) / (1 - mean q b)) * q.rate w) =
            (∑ w, (b.prob w * q.rate w - b.prob w * (q.rate w)^2)) / (1 - mean q b) := by
          conv_rhs => rw [div_eq_mul_inv, Finset.sum_mul]
          apply Finset.sum_congr rfl; intro w _; ring
        _ = _ := by rw [Finset.sum_sub_distrib]; rfl
    rw [he,div_le_iff₀ hpos]
    have hv := second_moment_ge_mean_square q b
    nlinarith
  · simp only [afterFault,hz,↓reduceDIte]; exact le_rfl

structure State (Ω : Type*) [Fintype Ω] where
  belief : RationalBelief Ω
  credits : Nat
  slots : Nat

def enabled (q : Reliability Ω) (s : State Ω) : Bool :=
  decide (q.fee ≤ s.credits ∧ 0 < s.slots)

def next (q : Reliability Ω) (s : State Ω) : State Ω :=
  ⟨afterFault q s.belief,s.credits - q.fee,s.slots - 1⟩

def model (q : Reliability Ω) : Retry.Model (State Ω) where
  enabled := enabled q
  resolve s := mean q s.belief
  resolve_nonneg s := mean_nonneg q s.belief
  resolve_le_one s := mean_le_one q s.belief
  cost _ := q.fee
  gain _ := q.benefit
  afterFault := next q

theorem immediate_nonincreasing (q : Reliability Ω) (s : State Ω) :
    Retry.immediate (model q) (next q s) ≤ Retry.immediate (model q) s := by
  change mean q (afterFault q s.belief) * q.benefit - (q.fee : ℚ) ≤
    mean q s.belief * q.benefit - (q.fee : ℚ)
  exact sub_le_sub_right (mul_le_mul_of_nonneg_right (mean_afterFault_le q s.belief)
    q.benefit_nonneg) _

theorem no_revival (q : Reliability Ω) : Retry.NoRevival (model q) := by
  intro s hs
  exact (immediate_nonincreasing q s).trans hs

/-- Exact optimal retry threshold for every positive horizon in this model.
Past sunk charges affect feasibility, but are not subtracted again from future gain. -/
theorem exact_retry_threshold (q : Reliability Ω) (n : Nat) (s : State Ω) :
    Retry.choose (model q) (n + 1) s =
      (enabled q s && decide ((q.fee : ℚ) < mean q s.belief * q.benefit)) := by
  rw [Retry.choose_threshold (model q) (no_revival q)]
  simp only [Retry.immediate,model,sub_pos]

def recommend (q : Reliability Ω) (s : State Ω) : Bool :=
  enabled q s && decide ((q.fee : ℚ) < mean q s.belief * q.benefit)

theorem recommend_is_optimal_choice (q : Reliability Ω) (n : Nat) (s : State Ω) :
    recommend q s = Retry.choose (model q) (n + 1) s :=
  (exact_retry_threshold q n s).symm

theorem insufficient_credit_abandons (q : Reliability Ω) (s : State Ω)
    (h : s.credits < q.fee) : recommend q s = false := by
  have hn : ¬q.fee ≤ s.credits := Nat.not_le_of_gt h
  simp [recommend,enabled,hn]

theorem no_slots_abandons (q : Reliability Ω) (s : State Ω)
    (h : s.slots = 0) : recommend q s = false := by
  simp [recommend,enabled,h]

theorem fee_exceeds_expected_gain_zero (q : Reliability Ω) (n : Nat) (s : State Ω)
    (h : mean q s.belief * q.benefit ≤ (q.fee : ℚ)) :
    Retry.retryValue (model q) n s = 0 := by
  apply Retry.no_revival_value_zero (model q) (no_revival q)
  change mean q s.belief * q.benefit - (q.fee : ℚ) ≤ 0
  exact sub_nonpos.mpr h

theorem enabled_consumes_slot (q : Reliability Ω) (s : State Ω)
    (h : enabled q s = true) : (next q s).slots + 1 = s.slots := by
  have hc : q.fee ≤ s.credits ∧ 0 < s.slots := of_decide_eq_true h
  change s.slots - 1 + 1 = s.slots
  omega

theorem enabled_charges_fee (q : Reliability Ω) (s : State Ω)
    (h : enabled q s = true) : (next q s).credits + q.fee = s.credits := by
  have hc : q.fee ≤ s.credits ∧ 0 < s.slots := of_decide_eq_true h
  change s.credits - q.fee + q.fee = s.credits
  omega

end Komorebi.AVOC.RetryBayesian
