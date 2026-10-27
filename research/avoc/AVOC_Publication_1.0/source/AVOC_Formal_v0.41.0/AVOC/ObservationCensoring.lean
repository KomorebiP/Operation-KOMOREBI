import AVOC.CalibrationSchedule

namespace Komorebi.AVOC.ObservationCensoring

open Finset CalibrationSchedule

/-- One attempt records the underlying binary outcome and whether it is reported.
`a` and `b` are the retention probabilities for success and rejection respectively.
An unreported attempt is an infrastructure fault, not a checked rejection. -/
def attemptLaw (p a b : ℚ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (ha0 : 0 ≤ a) (ha1 : a ≤ 1) (hb0 : 0 ≤ b) (hb1 : b ≤ 1) :
    Law (Bool × Bool) where
  weight := fun ω => if ω.1 then
      if ω.2 then p * a else p * (1 - a)
    else if ω.2 then (1 - p) * b else (1 - p) * (1 - b)
  nonneg := by
    rintro ⟨x, keep⟩
    cases x <;> cases keep <;> simp only [Bool.false_eq_true, ↓reduceIte]
    · exact mul_nonneg (sub_nonneg.mpr hp1) (sub_nonneg.mpr hb1)
    · exact mul_nonneg (sub_nonneg.mpr hp1) hb0
    · exact mul_nonneg hp0 (sub_nonneg.mpr ha1)
    · exact mul_nonneg hp0 ha0
  sum_one := by
    simp only [Fintype.sum_prod_type, Fintype.sum_bool, Bool.false_eq_true,
      ↓reduceIte]
    ring

/-- A checked success/rejection is retained; `none` is a fault without a sample. -/
def report (ω : Bool × Bool) : Option Bool := if ω.2 then some ω.1 else none

variable (p a b : ℚ) (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
  (ha0 : 0 ≤ a) (ha1 : a ≤ 1) (hb0 : 0 ≤ b) (hb1 : b ≤ 1)

theorem latent_success_mass :
    eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => ω.1 = true) = p := by
  simp [eventMass, attemptLaw, Fintype.sum_prod_type]
  ring

theorem reported_success_mass :
    eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => report ω = some true) = p * a := by
  simp [eventMass, attemptLaw, report, Fintype.sum_prod_type]

theorem reported_rejection_mass :
    eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => report ω = some false) = (1 - p) * b := by
  simp [eventMass, attemptLaw, report, Fintype.sum_prod_type]

theorem retained_mass :
    eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => ω.2 = true) = p * a + (1 - p) * b := by
  simp [eventMass, attemptLaw, Fintype.sum_prod_type]

theorem fault_mass :
    eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => report ω = none) = 1 - (p * a + (1 - p) * b) := by
  simp [eventMass, attemptLaw, report, Fintype.sum_prod_type]
  ring

/-- Exact conditional success probability, meaningful as a conditional law only
when the denominator (the probability of receiving a report) is positive. -/
noncomputable def conditionalSuccess : ℚ :=
  eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => report ω = some true) /
    eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
      (fun ω => ω.2 = true)

theorem conditional_success_formula :
    conditionalSuccess p a b hp0 hp1 ha0 ha1 hb0 hb1 =
      p * a / (p * a + (1 - p) * b) := by
  simp only [conditionalSuccess, reported_success_mass, retained_mass]

/-- The actual conditional law of retained reports. Its normalization requires
positive report probability, independently of whether the two retention rates agree. -/
def retainedLaw (hret : 0 < p * a + (1 - p) * b) : Law Bool where
  weight := fun x => (if x then p * a else (1 - p) * b) /
    (p * a + (1 - p) * b)
  nonneg := by
    intro x
    apply div_nonneg _ (le_of_lt hret)
    cases x
    · exact mul_nonneg (sub_nonneg.mpr hp1) hb0
    · exact mul_nonneg hp0 ha0
  sum_one := by
    simp only [Fintype.sum_bool, Bool.false_eq_true, ↓reduceIte]
    rw [← add_div]
    exact div_self (ne_of_gt hret)

/-- All events under the retained-report law are the corresponding attempted
report events conditioned on retention. This establishes a law, not only a mean. -/
theorem retained_event_conditioning (hret : 0 < p * a + (1 - p) * b)
    (event : Bool → Prop) :
    eventMass (retainedLaw p a b hp0 hp1 ha0 hb0 hret) event =
      eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
        (fun ω => ∃ x, report ω = some x ∧ event x) /
      eventMass (attemptLaw p a b hp0 hp1 ha0 ha1 hb0 hb1)
        (fun ω => ω.2 = true) := by
  classical
  by_cases ht : event true <;> by_cases hf : event false <;>
    simp [eventMass, retainedLaw, attemptLaw, report,
      Fintype.sum_prod_type, ht, hf, add_div]

/-- Equal success/rejection retention preserves the underlying success parameter.
The positive-rate premise excludes conditioning on a zero-probability report. -/
theorem equal_retention_preserves_parameter (r : ℚ) (hr0 : 0 < r) (hr1 : r ≤ 1) :
    conditionalSuccess p r r hp0 hp1 (le_of_lt hr0) hr1 (le_of_lt hr0) hr1 = p := by
  rw [conditional_success_formula]
  have hden : p * r + (1 - p) * r = r := by ring
  rw [hden]
  exact mul_div_cancel_right₀ p (ne_of_gt hr0)

theorem equal_retention_mass (r : ℚ) (hr0 : 0 ≤ r) (hr1 : r ≤ 1) :
    eventMass (attemptLaw p r r hp0 hp1 hr0 hr1 hr0 hr1)
      (fun ω => ω.2 = true) = r := by
  rw [retained_mass]
  ring

/-- For a nondegenerate source, equality of the two retention rates is also
necessary for a single reported outcome to retain its original parameter. -/
theorem conditional_parameter_preserved_iff (hp_pos : 0 < p) (hp_lt : p < 1)
    (hret : 0 < p * a + (1 - p) * b) :
    conditionalSuccess p a b hp0 hp1 ha0 ha1 hb0 hb1 = p ↔ a = b := by
  rw [conditional_success_formula, div_eq_iff (ne_of_gt hret)]
  constructor
  · intro h
    have heq : p * (1 - p) * (a - b) = 0 := by nlinarith [h]
    have hpos : 0 < p * (1 - p) := mul_pos hp_pos (sub_pos.mpr hp_lt)
    exact sub_eq_zero.mp ((mul_eq_zero.mp heq).resolve_left (ne_of_gt hpos))
  · intro h
    rw [h]
    ring

/-- Selectively losing every rejection turns a fair source into apparently
certain success among its reports. Logging faults separately cannot repair this. -/
theorem outcome_dependent_censoring_counterexample :
    conditionalSuccess (1 / 2) 1 0 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num) (by norm_num) = 1 := by
  rw [conditional_success_formula]
  norm_num

theorem outcome_dependent_censoring_changes_parameter :
    conditionalSuccess (1 / 2) 1 0 (by norm_num) (by norm_num)
      (by norm_num) (by norm_num) (by norm_num) (by norm_num) ≠ (1 / 2 : ℚ) := by
  rw [outcome_dependent_censoring_counterexample]
  norm_num

/-- Two independent fair latent outcomes; the deadline experiment below reveals
the first, then reveals the second exactly when the first was successful. -/
def deadlineLaw : Law (Bool × Bool) where
  weight := fun _ => 1 / 4
  nonneg := fun _ => by norm_num
  sum_one := by norm_num [Fintype.sum_prod_type, Fintype.sum_bool]

def deadlineSecondReport (ω : Bool × Bool) : Option Bool :=
  if ω.1 then some ω.2 else none

def deadlineComplete (ω : Bool × Bool) : Prop := ω.1 = true

instance : DecidablePred deadlineComplete := fun _ => inferInstanceAs (Decidable (_ = true))

def deadlineCount (ω : Bool × Bool) : Nat :=
  (if ω.1 then 1 else 0) + if ω.2 then 1 else 0

/-- The second report's availability depends only on the past, never on its
current outcome. Thus the stopping counterexample does not exploit current-bit
dependent censoring. -/
theorem deadline_second_retention_predictable (past current : Bool) :
    deadlineSecondReport (past, current) ≠ none ↔ past = true := by
  cases past <;> simp [deadlineSecondReport]

theorem deadline_current_bit_fair_given_past (past current : Bool) :
    eventMass deadlineLaw (fun ω => ω.1 = past ∧ ω.2 = current) /
      eventMass deadlineLaw (fun ω => ω.1 = past) = 1 / 2 := by
  cases past <;> cases current <;>
    norm_num [eventMass, deadlineLaw, Fintype.sum_prod_type, Fintype.sum_bool]

theorem deadline_completion_mass :
    eventMass deadlineLaw deadlineComplete = 1 / 2 := by
  norm_num [eventMass, deadlineLaw, deadlineComplete,
    Fintype.sum_prod_type, Fintype.sum_bool]

theorem deadline_unconditional_first_success :
    eventMass deadlineLaw (fun ω => ω.1 = true) = 1 / 2 := by
  exact deadline_completion_mass

/-- Conditioning on having completed two reports by this finite deadline biases
the first reported outcome, despite predictable second-report availability. -/
theorem deadline_conditioned_first_success :
    eventMass deadlineLaw (fun ω => deadlineComplete ω ∧ ω.1 = true) /
      eventMass deadlineLaw deadlineComplete = 1 := by
  norm_num [eventMass, deadlineLaw, deadlineComplete,
    Fintype.sum_prod_type, Fintype.sum_bool]

theorem deadline_conditioned_zero_count :
    eventMass deadlineLaw (fun ω => deadlineComplete ω ∧ deadlineCount ω = 0) /
      eventMass deadlineLaw deadlineComplete = 0 := by
  norm_num [eventMass, deadlineLaw, deadlineComplete, deadlineCount,
    Fintype.sum_prod_type, Fintype.sum_bool]

theorem deadline_conditioned_count_not_binomial :
    eventMass deadlineLaw (fun ω => deadlineComplete ω ∧ deadlineCount ω = 0) /
      eventMass deadlineLaw deadlineComplete ≠ FiniteCalibration.mass 2 0 (1 / 2) := by
  rw [deadline_conditioned_zero_count]
  norm_num [FiniteCalibration.mass]

variable {Ω : Type*} [Fintype Ω]

/-- Fail-closed publication of a completed prefix preserves the unconditional
bad-output bound. It does not promise the same bound after conditioning on output. -/
theorem completed_bad_le (law : Law Ω) (complete bad : Ω → Prop) :
    eventMass law (fun ω => complete ω ∧ bad ω) ≤ eventMass law bad := by
  exact eventMass_mono law (fun _ h => h.2)

theorem completed_bad_bound (law : Law Ω) (complete bad : Ω → Prop) (alpha : ℚ)
    (hbad : eventMass law bad ≤ alpha) :
    eventMass law (fun ω => complete ω ∧ bad ω) ≤ alpha := by
  exact (completed_bad_le law complete bad).trans hbad

/-- Conditional validity may deteriorate by the inverse completion probability;
this is the bound available without an independence assumption. -/
theorem conditioned_completed_bad_bound (law : Law Ω) (complete bad : Ω → Prop)
    (alpha : ℚ) (hcomplete : 0 < eventMass law complete)
    (hbad : eventMass law bad ≤ alpha) :
    eventMass law (fun ω => complete ω ∧ bad ω) / eventMass law complete ≤
      alpha / eventMass law complete := by
  exact div_le_div_of_nonneg_right (completed_bad_bound law complete bad alpha hbad)
    (le_of_lt hcomplete)

end Komorebi.AVOC.ObservationCensoring
