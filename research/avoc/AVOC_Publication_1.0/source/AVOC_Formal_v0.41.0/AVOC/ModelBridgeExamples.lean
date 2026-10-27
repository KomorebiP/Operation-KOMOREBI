import AVOC.BayesianGuardedBridge
import AVOC.BeliefValueTables
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC.ModelBridgeExamples
open Guarded

/-- Single uninformative observation. Hidden beliefs still form an infinite
state space; this example isolates reward and table-residual error. -/
def silentChannel : RationalChannel Bool Unit where
  prob _ _ := 1
  nonneg := by intros; norm_num
  sum_one := by intros; simp

theorem silent_predictive (b : RationalBelief Bool) (o : Unit) :
    predictiveProb b silentChannel o = 1 := by
  simpa [predictiveProb, silentChannel] using b.sum_one

theorem silent_posterior (b : RationalBelief Bool) (o : Unit) :
    bayesUpdateTotal b silentChannel o = b := by
  have hp : 0 < predictiveProb b silentChannel o := by rw [silent_predictive]; norm_num
  rw [bayesUpdateTotal_eq_of_pos b silentChannel o hp]
  apply RationalBelief.ext
  intro w
  change (b.prob w * 1) / predictiveProb b silentChannel o = b.prob w
  rw [silent_predictive]; ring

abbrev BState := RationalBelief Bool × Unit

def rawReward (a : Bool) : ℚ := if a then 2/5 else 1/2
def learnedReward (a : Bool) : ℚ := if a then 2/5 else 3/10

def rawSystem : System BState Bool Unit where
  actions _ := Finset.univ
  actions_nonempty _ := Finset.univ_nonempty
  prob _ _ _ := 1
  prob_nonneg := by intros; norm_num
  prob_sum_one := by intros; simp
  step s _ _ := s
  reward _ a := rawReward a

def learnedSystem : System BState Bool Unit where
  actions _ := Finset.univ
  actions_nonempty _ := Finset.univ_nonempty
  prob _ _ _ := 1
  prob_nonneg := by intros; norm_num
  prob_sum_one := by intros; simp
  step s _ _ := s
  reward _ a := learnedReward a

/-- Deliberately inexact value table: model optimum is 2n/5, not n/3. -/
def coarseValue (k : ℕ) (_s : BState) : ℚ := (k : ℚ) / 3

theorem learned_table_q (k : ℕ) (s : BState) (a : Bool) :
    tableQ learnedSystem (coarseValue k) s a = learnedReward a + (k : ℚ)/3 := by
  simp [tableQ, expectation, learnedSystem, coarseValue]

theorem learned_backup (k : ℕ) (s : BState) :
    backup learnedSystem (coarseValue k) s = 2/5 + (k : ℚ)/3 := by
  obtain ⟨a, _, he⟩ := backup_attained learnedSystem (coarseValue k) s
  have hl := tableQ_le_backup learnedSystem (coarseValue k) s true (Finset.mem_univ true)
  rw [learned_table_q] at hl
  rw [learned_table_q] at he
  rw [he]
  cases a
  · norm_num [learnedReward] at *
    linarith
  · rfl

theorem coarse_residual (k : ℕ) (s : BState) :
    |backup learnedSystem (coarseValue k) s - coarseValue (k + 1) s| = 1/15 := by
  rw [learned_backup]
  simp only [coarseValue, Nat.cast_add, Nat.cast_one]
  have h : (2/5 : ℚ) + (k : ℚ)/3 - ((k : ℚ)+1)/3 = 1/15 := by ring
  rw [h]; norm_num

def silentLink : BayesianStepLink rawSystem learnedSystem id (fun s => s.1) where
  rawExperiment _ _ := silentChannel
  modelExperiment _ _ := silentChannel
  raw_prob s a o := by change 1 = predictiveProb s.1 silentChannel o; rw [silent_predictive]
  model_prob s a o := by change 1 = predictiveProb s.1 silentChannel o; rw [silent_predictive]
  model_posterior s a o := by change s.1 = bayesUpdateTotal s.1 silentChannel o; rw [silent_posterior]
  metadata_match := by intros; rfl

/-- Nonvacuous primitive certificate with nonzero reward error and nonzero
Bellman-table residual. No actual optimal-Q errors occur in its inputs. -/
def exampleCertificate : BayesianModelCertificate rawSystem learnedSystem id (fun s => s.1)
    coarseValue (1/5) 0 0 (fun _ => 0) (fun k => (k : ℚ)/3) (fun _ => 0) (fun _ => 1/15) where
  link := silentLink
  actions_eq _ := rfl
  initial _ := by simp [coarseValue]
  reward_error s a _ := by cases a <;> norm_num [rawSystem, learnedSystem, rawReward, learnedReward]
  prior_error s := by simp [beliefL1Distance]
  channel_error s a _ w := by simp [silentLink, silentChannel]
  codec_error k s a _ := by simp [rawSystem, silentLink, silent_posterior, beliefL1Distance]
  lip_nonneg _ := by norm_num
  bound_nonneg k := by positivity
  table_lipschitz k m b c := by simp [coarseValue]
  table_bound k z := by simp [coarseValue, abs_of_nonneg (show (0 : ℚ) ≤ (k : ℚ)/3 by positivity)]
  residual_error k s := by rw [coarse_residual]

theorem example_transport_zero (k : ℕ) :
    bayesianTransportBudget 0 0 (fun _ => 0) (fun k => (k : ℚ)/3) (fun _ => 0) k = 0 := by
  simp [bayesianTransportBudget]

theorem example_transport_eq_zero :
    bayesianTransportBudget 0 0 (fun _ => 0) (fun k => (k : ℚ)/3) (fun _ => 0) = (fun _ => 0) := by
  funext k
  exact example_transport_zero k

theorem example_derived_q_bound (k : ℕ) (s : BState) (a : Bool) :
    |qValue rawSystem k s a - tableQ learnedSystem (coarseValue k) s a| ≤
      modelQBudget (1/5) (fun _ => 0) (fun _ => 1/15) k := by
  have h := bayesian_primitive_q_error exampleCertificate k s a (Finset.mem_univ a)
  simpa only [example_transport_eq_zero, id_eq] using h

theorem raw_value_exact (k : ℕ) (s : BState) : value rawSystem k s = (k : ℚ)/2 := by
  induction k generalizing s with
  | zero => simp
  | succ k ih =>
    have hq (a : Bool) : qValue rawSystem k s a = rawReward a + (k : ℚ)/2 := by
      change rawReward a + (∑ _o : Unit, (1 : ℚ) * value rawSystem k s) = _
      simp [ih]
    have hm : ∀ a ∈ rawSystem.actions s, qValue rawSystem k s a ≤ qValue rawSystem k s false := by
      intro a _
      rw [hq, hq]
      cases a <;> norm_num [rawReward]
    rw [value_eq_q_of_optimal rawSystem k s false (Finset.mem_univ false) hm, hq]
    simp only [rawReward, Bool.false_eq_true, ite_false, Nat.cast_add, Nat.cast_one]
    ring

theorem learned_choice_value (k : ℕ) (s : BState) :
    planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) k s) = (k : ℚ) * (2/5) := by
  induction k generalizing s with
  | zero => simp [policyPlan, planValue]
  | succ k ih =>
    change (2/5 : ℚ) + (∑ _o : Unit, (1 : ℚ) *
      planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) k s)) = _
    simp [ih, Nat.cast_add, add_mul, add_comm]

theorem example_actual_regret (k : ℕ) (s : BState) :
    value rawSystem k s - planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) k s) =
      (k : ℚ)/10 := by
  rw [raw_value_exact, learned_choice_value]
  ring

theorem example_model_policy_bound (k : ℕ) (s : BState) :
    0 ≤ value rawSystem k s - planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) k s) ∧
    value rawSystem k s - planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) k s) ≤
      regretBudget (fun j => 2 * modelQBudget (1/5) (fun _ => 0) (fun _ => 1/15) j) k := by
  have hm : ∀ j (s : BState) a, a ∈ rawSystem.actions s →
      tableQ learnedSystem (coarseValue j) s a ≤ tableQ learnedSystem (coarseValue j) s true + 0 := by
    intro j s a _
    rw [learned_table_q, learned_table_q]
    cases a <;> norm_num [learnedReward]
  have h := model_decoded_policy_regret rawSystem learnedSystem id coarseValue (1/5)
    _ (fun _ => 1/15) exampleCertificate.toModelCertificate
    (fun j s a => tableQ learnedSystem (coarseValue j) s a) (fun _ _ => true)
    (fun _ => 0) (fun _ => 0) (fun _ _ => Finset.mem_univ true)
    (by intros; simp) hm k s
  simpa only [example_transport_eq_zero, add_zero] using h

theorem example_not_zero_regret (s : BState) :
    value rawSystem 1 s - planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) 1 s) ≠ 0 := by
  rw [example_actual_regret]; norm_num

theorem residual_cannot_be_ignored (s : BState) :
    ¬ |backup learnedSystem (coarseValue 0) s - coarseValue 1 s| ≤ 0 := by
  rw [coarse_residual]; norm_num

end Komorebi.AVOC.ModelBridgeExamples
