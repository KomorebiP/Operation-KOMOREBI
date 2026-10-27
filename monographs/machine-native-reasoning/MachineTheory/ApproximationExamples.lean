import MachineTheory.ApproximateDecision
import MachineTheory.PlanningSensor

/-!
Exact boundary examples. These are proof terms over specified probability laws,
not sampled observations, confidence intervals, or oracle-provided counter values.
-/
namespace Komorebi.MachineTheory.ApproximationExamples
open scoped BigOperators
open Instrument Variation ApproximateHistory ApproximateDecision
noncomputable section

abbrev Outcome := Bool × Bool

/-- First bit marks the rare report; second bit is the output of interest. -/
def rareP (δ : ℝ) : Outcome → ℝ
  | (false,false) => 1-δ
  | (true,false) => δ
  | _ => 0

def rareQ (δ : ℝ) : Outcome → ℝ
  | (false,false) => 1-δ
  | (true,true) => δ
  | _ => 0

def rareEvent : Finset Outcome := {(true,false),(true,true)}

theorem rareP_dist (δ : ℝ) (h0 : 0 ≤ δ) (h1 : δ ≤ 1) : IsDist (rareP δ) := by
  constructor
  · rintro ⟨a,b⟩; cases a <;> cases b <;> simp [rareP] <;> linarith
  · norm_num [mass, Fintype.sum_prod_type, Fintype.sum_bool, rareP]

theorem rareQ_dist (δ : ℝ) (h0 : 0 ≤ δ) (h1 : δ ≤ 1) : IsDist (rareQ δ) := by
  constructor
  · rintro ⟨a,b⟩; cases a <;> cases b <;> simp [rareQ] <;> linarith
  · norm_num [mass, Fintype.sum_prod_type, Fintype.sum_bool, rareQ]

theorem rare_distance (δ : ℝ) (h0 : 0 ≤ δ) : tv (rareP δ) (rareQ δ) = δ := by
  simp [tv, l1, Fintype.sum_prod_type, rareP, rareQ, abs_of_nonneg h0]

theorem rare_masses (δ : ℝ) : mass (restrict rareEvent (rareP δ)) = δ ∧
    mass (restrict rareEvent (rareQ δ)) = δ := by
  norm_num [mass, restrict, rareEvent, Fintype.sum_prod_type, Fintype.sum_bool, rareP, rareQ]

theorem rare_posteriors (δ : ℝ) (hδ : 0 < δ) :
    normalize (restrict rareEvent (rareP δ)) = basis (true,false) ∧
    normalize (restrict rareEvent (rareQ δ)) = basis (true,true) := by
  constructor
  · funext x; rcases x with ⟨a,b⟩
    unfold normalize; rw [(rare_masses δ).1]
    cases a <;> cases b <;> simp [restrict, rareEvent, rareP, basis, ne_of_gt hδ]
  · funext x; rcases x with ⟨a,b⟩
    unfold normalize; rw [(rare_masses δ).2]
    cases a <;> cases b <;> simp [restrict, rareEvent, rareQ, basis, ne_of_gt hδ]

/-- The event-probability denominator is necessary even for exact finite distributions. -/
theorem rare_conditional_distance (δ : ℝ) (hδ : 0 < δ) :
    tv (normalize (restrict rareEvent (rareP δ))) (normalize (restrict rareEvent (rareQ δ))) = 1 := by
  rw [(rare_posteriors δ hδ).1, (rare_posteriors δ hδ).2]
  norm_num [tv, l1, basis, Fintype.sum_prod_type, Fintype.sum_bool]

theorem rare_output_distance (δ : ℝ) (hδ : 0 < δ) :
    tv (push Prod.snd (normalize (restrict rareEvent (rareP δ))))
      (push Prod.snd (normalize (restrict rareEvent (rareQ δ)))) = 1 := by
  rw [(rare_posteriors δ hδ).1, (rare_posteriors δ hδ).2]
  norm_num [tv, l1, push, basis, Fintype.sum_prod_type, Fintype.sum_bool]
  decide

theorem no_unconditioned_posterior_bound :
    ¬ tv (normalize (restrict rareEvent (rareP (1/100))))
      (normalize (restrict rareEvent (rareQ (1/100)))) ≤ tv (rareP (1/100)) (rareQ (1/100)) := by
  rw [rare_conditional_distance _ (by norm_num), rare_distance _ (by norm_num)]
  norm_num

/-- Unequal masses attain the stronger maximum-denominator form. -/
def largerEventQ (δ : ℝ) : Outcome → ℝ
  | (false,false) => 1-2*δ
  | (true,false) => δ
  | (true,true) => δ
  | _ => 0

theorem largerEventQ_dist (δ : ℝ) (h0 : 0 ≤ δ) (h1 : δ ≤ 1/2) : IsDist (largerEventQ δ) := by
  constructor
  · rintro ⟨a,b⟩; cases a <;> cases b <;> simp [largerEventQ] <;> linarith
  · norm_num [mass, Fintype.sum_prod_type, Fintype.sum_bool, largerEventQ]; ring

theorem unequal_mass_sharp :
    tv (rareP (1/10)) (largerEventQ (1/10)) = 1/10 ∧
    mass (restrict rareEvent (rareP (1/10))) = 1/10 ∧
    mass (restrict rareEvent (largerEventQ (1/10))) = 1/5 ∧
    tv (normalize (restrict rareEvent (rareP (1/10))))
      (normalize (restrict rareEvent (largerEventQ (1/10)))) = 1/2 := by
  norm_num [tv, l1, normalize, mass, restrict, rareEvent, rareP, largerEventQ,
    Fintype.sum_prod_type, Fintype.sum_bool]

/-- The strict threshold for inferring positive counterpart mass cannot be weakened to equality. -/
theorem positive_threshold_is_strict :
    IsDist (rareP (1/10)) ∧ IsDist (rareP 0) ∧
    tv (rareP (1/10)) (rareP 0) = 1/10 ∧
    mass (restrict rareEvent (rareP (1/10))) = 1/10 ∧
    mass (restrict rareEvent (rareP 0)) = 0 := by
  refine ⟨rareP_dist _ (by norm_num) (by norm_num), rareP_dist _ (by norm_num) (by norm_num), ?_⟩
  norm_num [tv, l1, mass, restrict, rareEvent, rareP, Fintype.sum_prod_type, Fintype.sum_bool]

/-- The factor two in changed-policy regret can be attained because approximate ties can be resolved badly. -/
def truthLaw (b : Bool) : ℝ := if b then 3/4 else 1/4

def modelLaw (_b : Bool) : ℝ := 1/2

def classificationLoss (decision state : Bool) : ℝ := if decision=state then 0 else 1

theorem truthLaw_dist : IsDist truthLaw := by
  constructor
  · intro b; cases b <;> norm_num [truthLaw]
  · norm_num [mass, Fintype.sum_bool, truthLaw]

theorem modelLaw_dist : IsDist modelLaw := by
  constructor
  · intro b; norm_num [modelLaw]
  · norm_num [mass, Fintype.sum_bool, modelLaw]

theorem classification_values :
    risk truthLaw (classificationLoss false) = 3/4 ∧
    risk truthLaw (classificationLoss true) = 1/4 ∧
    risk modelLaw (classificationLoss false) = 1/2 ∧
    risk modelLaw (classificationLoss true) = 1/2 ∧ tv truthLaw modelLaw = 1/4 := by
  norm_num [risk, classificationLoss, truthLaw, modelLaw, tv, l1, Fintype.sum_bool]

theorem approximate_choice_is_optimal : ∀ d, risk modelLaw (classificationLoss false) ≤ risk modelLaw (classificationLoss d) := by
  intro d; cases d <;> norm_num [risk, classificationLoss, modelLaw, Fintype.sum_bool]

theorem true_choice_is_optimal : ∀ d, risk truthLaw (classificationLoss true) ≤ risk truthLaw (classificationLoss d) := by
  intro d; cases d <;> norm_num [risk, classificationLoss, truthLaw, Fintype.sum_bool]

theorem regret_factor_two_sharp :
    risk truthLaw (classificationLoss false)-risk truthLaw (classificationLoss true) = 2*tv truthLaw modelLaw := by
  rw [classification_values.1, classification_values.2.1, classification_values.2.2.2.2]
  norm_num

/-- A same-policy law bound is not a comparison between two different selected losses. -/
theorem same_law_not_same_policy_value :
    tv truthLaw truthLaw = 0 ∧ risk truthLaw (classificationLoss false)-risk truthLaw (classificationLoss true) = 1/2 := by
  rw [tv_self, classification_values.1, classification_values.2.1]
  norm_num

/-- The delivered regret theorem is instantiated, not only numerically quoted. -/
theorem checked_selected_regret :
    risk truthLaw (classificationLoss false)-risk truthLaw (classificationLoss true) ≤ min 1 (2*1*(1/4)) := by
  apply uniform_policy_regret (fun _ : Bool => truthLaw) (fun _ : Bool => modelLaw)
    classificationLoss Finset.univ 1 (1/4) (by norm_num)
    (fun _ _ => truthLaw_dist) (fun _ _ => modelLaw_dist)
  · intro d _ b; unfold classificationLoss; split_ifs <;> norm_num
  · intro _ _; exact le_of_eq classification_values.2.2.2.2
  · exact Finset.mem_univ _
  · exact Finset.mem_univ _
  · intro i _; exact approximate_choice_is_optimal i

/-- Source sensor: slightly misspecified calibration, while the hidden world is unchanged. -/
def calibrated37 : Law PlanningSensor.World Unit Bool where
  kernel _ o y x := if y=x then (if o=x.2.1 then 37/50 else 13/50) else 0
  nonnegative _ _ _ _ := by split_ifs <;> norm_num
  normalized _ x := by
    simp only [Finset.sum_ite_eq', Finset.mem_univ, ite_true]
    rcases x with ⟨b,s,n⟩
    cases s <;> norm_num [Fintype.sum_bool]

/-- Actual coarse report/state row error, not an isolated likelihood entry. -/
theorem sensor_joint_row_error (a : Unit) (x : PlanningSensor.World) :
    tv (push (reportMap PlanningSensor.project) (jointRow calibrated37 a x))
      (jointRow PlanningSensor.sensorLaw a (PlanningSensor.project x)) = 1/100 := by
  rcases x with ⟨b,s,n⟩
  cases b <;> cases s <;> cases n <;>
    norm_num [tv, l1, push, reportMap, jointRow, calibrated37, PlanningSensor.sensorLaw,
      PlanningSensor.project, PlanningSensor.accuracy, Fintype.sum_prod_type, Fintype.sum_bool, ite_and]

/-- The source's 1/100 per-report discrepancy accumulates on all recorded histories. -/
theorem sensor_all_history_error (g : Policy Unit Bool) (p : PlanningSensor.World → ℝ)
    (hp : IsDist p) (H : Nat) :
    tv (push (project PlanningSensor.project H) (law (fun _ => calibrated37) g p H))
      (law (fun _ => PlanningSensor.sensorLaw) g (push PlanningSensor.project p) H) ≤ min 1 ((H : ℝ)/100) := by
  have h := whole_history_bound PlanningSensor.project (fun _ => calibrated37)
    (fun _ => PlanningSensor.sensorLaw) g p (push PlanningSensor.project p) hp
    (push_dist _ _ hp) 0 (fun _ => 1/100) (by rw [tv_self])
    (fun _ a x => le_of_eq (sensor_joint_row_error a x)) H
  simpa [Finset.sum_const, Finset.card_range, nsmul_eq_mul, div_eq_mul_inv] using h

/-- Core 5.6's displayed sensor margin is exact rational arithmetic. -/
theorem sensor_uniform_margins :
    (23/20 : ℝ) * min 1 ((3 : ℝ)/100) = 69/2000 ∧
    min (23/20 : ℝ) (2*(23/20)*min 1 ((3 : ℝ)/100)) = 69/1000 := by norm_num

/-- One correctly audited alternative does not give a uniform bound on the chosen one. -/
theorem baseline_only_audit_fails :
    tv (basis false : Bool → ℝ) (basis false) = 0 ∧
    tv (basis true : Bool → ℝ) (basis false) = 1 ∧
    risk (basis true) (fun b : Bool => if b then 1 else 0) -
      risk (basis false) (fun b : Bool => if b then 1 else 0) = 1 := by
  norm_num [tv, l1, basis, risk, Fintype.sum_bool]

/-- Resetting the state cannot erase the old state from a complete path record. -/
def resetLaw : Law Bool Unit Unit where
  kernel _ _ y _ := if y=false then 1 else 0
  nonnegative _ _ _ _ := by split_ifs <;> norm_num
  normalized _ _ := by simp

def unitPolicy : Policy Unit Unit where
  probability _ _ := 1
  nonnegative _ _ := by norm_num
  normalized _ := by simp

theorem reset_path_one (p : Bool → ℝ) (b o : Bool) :
    law (fun _ => resetLaw) unitPolicy p 1 (b,(),(),o) = (if o=false then 1 else 0)*p b := by
  simpa only [unitPolicy, resetLaw, law_zero, observed, last, one_mul] using
    (law_succ (fun _ => resetLaw) unitPolicy p 0 b ((),(),o))

theorem reset_full_history_distance :
    tv (law (fun _ => resetLaw) unitPolicy (basis false) 1)
      (law (fun _ => resetLaw) unitPolicy (basis true) 1) = 1 := by
  norm_num [tv, l1, Fintype.sum_prod_type, Fintype.sum_bool, law, applyKernel, pathKernel, push, stepRow, jointRow, resetLaw, unitPolicy, basis, last, observed, Path, ite_and]

theorem reset_final_states_agree :
    push (last 1) (law (fun _ => resetLaw) unitPolicy (basis false) 1) =
      push (last 1) (law (fun _ => resetLaw) unitPolicy (basis true) 1) := by
  funext b
  cases b <;> norm_num [push, Fintype.sum_prod_type, Fintype.sum_bool, law, applyKernel, pathKernel, push, stepRow, jointRow, resetLaw, unitPolicy, basis, last, observed, Path, ite_and]

end
end Komorebi.MachineTheory.ApproximationExamples
