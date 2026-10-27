import AVOC.RetryLedger

namespace Komorebi.AVOC.RetryExamples

open RetryBayesian

def prior : RationalBelief Bool where
  prob _ := 1/2
  nonneg _ := by norm_num
  sum_one := by norm_num

def persistent : Reliability Bool where
  rate w := if w then 9/10 else 1/10
  rate_nonneg w := by cases w <;> norm_num
  rate_le_one w := by cases w <;> norm_num
  fee := 1
  benefit := 4
  benefit_nonneg := by norm_num

def initial : State Bool := ⟨prior,3,3⟩

theorem initial_resolve_probability : mean persistent prior = 1/2 := by
  norm_num [mean,persistent,prior]

theorem posterior_fast_after_fault : (afterFault persistent prior).prob true = 1/10 := by
  rw [afterFault_formula persistent prior (by rw [initial_resolve_probability]; norm_num)]
  norm_num [prior,persistent,mean]

theorem posterior_slow_after_fault : (afterFault persistent prior).prob false = 9/10 := by
  rw [afterFault_formula persistent prior (by rw [initial_resolve_probability]; norm_num)]
  norm_num [prior,persistent,mean]

theorem fault_resolve_probability : mean persistent (afterFault persistent prior) = 9/50 := by
  unfold mean
  simp only [Fintype.sum_bool]
  rw [posterior_fast_after_fault,posterior_slow_after_fault]
  norm_num [persistent]

theorem initially_retry : recommend persistent initial = true := by
  norm_num [recommend,enabled,initial,mean,persistent,prior]

theorem after_fault_abandon : recommend persistent (next persistent initial) = false := by
  norm_num [recommend,enabled,next,initial,mean,afterFault,conditionByWeight,evidenceMass,persistent,prior]

theorem fault_future_value_zero (n : Nat) :
    Retry.retryValue (model persistent) n (next persistent initial) = 0 := by
  apply fee_exceeds_expected_gain_zero
  change mean persistent (afterFault persistent prior) * 4 ≤ (1 : ℚ)
  rw [fault_resolve_probability]; norm_num

theorem persistent_all_positive_horizons (n : Nat) :
    Retry.retryValue (model persistent) (n + 1) initial = 1 := by
  change (if enabled persistent initial then
    max 0 (Retry.immediate (model persistent) initial +
      (1 - mean persistent prior) * Retry.retryValue (model persistent) n (next persistent initial)) else 0) = 1
  rw [fault_future_value_zero]
  norm_num [enabled,Retry.immediate,model,initial,mean,persistent,prior]

/-- Same current marginal, but independent fresh reliability every attempt. -/
def iid : Reliability Bool where
  rate _ := 1/2
  rate_nonneg _ := by norm_num
  rate_le_one _ := by norm_num
  fee := 1
  benefit := 4
  benefit_nonneg := by norm_num

theorem iid_fault_does_not_change_prior : afterFault iid prior = prior := by
  apply RationalBelief.ext
  intro w
  rw [afterFault_formula iid prior (by norm_num [mean,iid,prior])]
  norm_num [mean,iid,prior]

theorem iid_three_attempt_value : Retry.retryValue (model iid) 3 initial = 7/4 := by
  norm_num [Retry.retryValue,Retry.immediate,model,enabled,next,initial,
    afterFault,conditionByWeight,evidenceMass,mean,iid,prior]

theorem same_first_probability_different_value :
    mean persistent prior = mean iid prior ∧
    Retry.retryValue (model persistent) 3 initial ≠ Retry.retryValue (model iid) 3 initial := by
  constructor
  · norm_num [mean,persistent,iid,prior]
  · rw [persistent_all_positive_horizons, iid_three_attempt_value]; norm_num

/-- Counterexample to applying the threshold outside its no-revival hypotheses:
the service improves after an initial fault, and another attempt can be valuable. -/
def improving : Retry.Model Bool where
  enabled _ := true
  resolve s := if s then 1 else 0
  resolve_nonneg s := by cases s <;> norm_num
  resolve_le_one s := by cases s <;> norm_num
  cost _ := 1
  gain _ := 10
  afterFault _ := true

theorem improving_one_step_bad : Retry.immediate improving false = -1 := by norm_num [Retry.immediate,improving]

theorem improving_two_steps_worthwhile : Retry.retryValue improving 2 false = 8 := by
  norm_num [Retry.retryValue,Retry.immediate,improving]

theorem improving_not_no_revival : ¬ Retry.NoRevival improving := by
  intro h
  have hh := h false (by norm_num [Retry.immediate,improving])
  norm_num [Retry.immediate,improving] at hh

theorem improving_retry_despite_negative_immediate : Retry.choose improving 2 false = true := by
  norm_num [Retry.choose,Retry.trialValue,Retry.retryValue,Retry.immediate,improving]

def lim : Attempts.Limits := ⟨4,4⟩
def old : Attempts.Ticket := ⟨1,1,1⟩
def pending : Attempts.Ledger := ⟨2,1,2,some old,false,false⟩

theorem example_ledger_safe : Attempts.Safe lim pending := by
  norm_num [Attempts.Safe,Attempts.held,lim,pending,old]

theorem example_retry_charges_fresh :
    RetryLedger.authorize persistent lim pending prior old =
      .ok (⟨3,1,3,some ⟨1,2,1⟩,false,false⟩ : Attempts.Ledger) := by
  norm_num [RetryLedger.authorize,RetryLedger.state,recommend,enabled,mean,persistent,prior,
    Attempts.renew,Attempts.room,lim,pending,old]

theorem example_after_fault_abandons_without_refund :
    RetryLedger.authorize persistent lim pending (afterFault persistent prior) old =
      .ok (⟨2,1,2,none,false,true⟩ : Attempts.Ledger) := by
  norm_num [RetryLedger.authorize,RetryLedger.state,recommend,enabled,mean,afterFault,
    conditionByWeight,evidenceMass,persistent,prior,Attempts.abandon,lim,pending,old]

end Komorebi.AVOC.RetryExamples
