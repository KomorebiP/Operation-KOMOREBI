import MachineTheory.PlanningTransport
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-! Exact source sensor, Core 5.4 worked example. No sampled outcomes or extracted numerical oracle. -/
namespace Komorebi.MachineTheory.PlanningSensor
open Instrument Planning BeliefPlanning
open scoped BigOperators
noncomputable section

abbrev Pair := Bool × Bool
abbrev World := Bool × Bool × Bool

def project (x : World) : Pair := (x.1, x.2.1)

def accuracy (s o : Bool) : ℝ := if o = s then 3/4 else 1/4

theorem accuracy_pos (s o : Bool) : 0 < accuracy s o := by
  unfold accuracy; split_ifs <;> norm_num

theorem accuracy_total (s : Bool) : (∑ o, accuracy s o) = 1 := by
  cases s <;> norm_num [accuracy]

def sensorLaw : Law Pair Unit Bool where
  kernel _ o y x := if y = x then accuracy x.2 o else 0
  nonnegative _ o y x := by split_ifs; exact le_of_lt (accuracy_pos _ _); exact le_rfl
  normalized _ x := by simpa using accuracy_total x.2

def fineLaw : Law World Unit Bool where
  kernel _ o y x := if y = x then accuracy x.2.1 o else 0
  nonnegative _ o y x := by split_ifs; exact le_of_lt (accuracy_pos _ _); exact le_rfl
  normalized _ x := by simpa using accuracy_total x.2.1

def contract : Contract Pair Unit Bool where
  actions _ := {()}
  decisions _ := Finset.univ
  decisions_nonempty _ := Finset.univ_nonempty
  charge _ _ := 1/20
  charge_nonnegative _ _ := by norm_num
  terminalLoss d z := if d = z.1 then 0 else 1

theorem sensor_joint_quotient (a : Unit) (o : Bool) :
    Intertwines project (fineLaw.kernel a o) (sensorLaw.kernel a o) := by
  apply (intertwines_iff_rows _ _ _).mpr
  intro z x
  classical
  simp only [fineLaw, sensorLaw]
  rw [Finset.sum_eq_single x]
  · by_cases hz : project x = z
    · subst z; simp [project]
    · have hz' : z ≠ project x := Ne.symm hz
      simp [hz, hz']
  · intro y _ hy
    simp [hy]
  · simp

/-- The full eight-world theorem holds for every initial nuisance distribution and every horizon. -/
theorem sensor_all_prior_values (h : Nat) (p : Belief World) :
    value (fineModel fineLaw project contract) h p =
      value (coarseModel sensorLaw contract) h (aggregate project p) :=
  (instrumentMap fineLaw sensorLaw project sensor_joint_quotient contract).value_eq h p

abbrev Counts := Nat × Nat

def wTrue (n : Counts) : ℝ := 3 ^ n.1
def wFalse (n : Counts) : ℝ := 3 ^ n.2
def total (n : Counts) : ℝ := wTrue n + wFalse n

theorem wTrue_pos (n : Counts) : 0 < wTrue n := pow_pos (by norm_num) _
theorem wFalse_pos (n : Counts) : 0 < wFalse n := pow_pos (by norm_num) _
theorem total_pos (n : Counts) : 0 < total n := add_pos (wTrue_pos n) (wFalse_pos n)

/-- Initial display zero fixes b=s. Counted reports then alter only the two diagonal masses. -/
def countBelief (n : Counts) : Belief Pair :=
  ⟨fun z => if z.1 = z.2 then (if z.1 then wTrue n else wFalse n) / total n else 0, by
    constructor
    · intro z
      have ha := wTrue_pos n
      have hb := wFalse_pos n
      have ht := total_pos n
      rcases z with ⟨b,s⟩
      cases b <;> cases s <;> dsimp <;> positivity
    · norm_num [mass, Fintype.sum_prod_type]
      rw [← add_div]
      exact div_self (ne_of_gt (total_pos n))⟩

def advance (n : Counts) (o : Bool) : Counts := if o then (n.1+1,n.2) else (n.1,n.2+1)

def report (n : Counts) (o : Bool) : ℝ :=
  if o then (3*wTrue n+wFalse n)/(4*total n)
  else (wTrue n+3*wFalse n)/(4*total n)

def stopRisk (n : Counts) (d : Bool) : ℝ :=
  if d then wFalse n / total n else wTrue n / total n

theorem report_pos (n : Counts) (o : Bool) : 0 < report n o := by
  have ha := wTrue_pos n; have hb := wFalse_pos n; have ht := total_pos n
  cases o <;> dsimp [report] <;> positivity

theorem report_total (n : Counts) : (∑ o, report n o) = 1 := by
  simp only [Fintype.sum_bool, report, Bool.false_eq_true, ite_false, ite_true]
  have ht := ne_of_gt (total_pos n)
  dsimp [total] at *
  field_simp
  ring

def countModel : Model Counts Unit Bool Bool where
  actions _ := {()}
  decisions _ := Finset.univ
  decisions_nonempty _ := Finset.univ_nonempty
  cost _ _ := 1/20
  cost_nonnegative _ _ := by norm_num
  loss := stopRisk
  prob n _ o := report n o
  nonnegative n _ o := le_of_lt (report_pos n o)
  normalized n _ := report_total n
  next n _ o _ := advance n o

theorem count_report_eq (n : Counts) (o : Bool) :
    report n o = (coarseModel sensorLaw contract).prob (countBelief n) () o := by
  have ht := ne_of_gt (total_pos n)
  cases o <;>
    simp [report, coarseModel, sensorLaw, countBelief, applyKernel, mass, accuracy,
      Fintype.sum_prod_type, total] <;> field_simp

theorem count_loss_eq (n : Counts) (d : Bool) :
    stopRisk n d = (coarseModel sensorLaw contract).loss (countBelief n) d := by
  cases d <;> simp [stopRisk, coarseModel, sensorLaw, contract, countBelief, Fintype.sum_prod_type]

theorem count_update_eq (n : Counts) (o : Bool) (ho : 0 < report n o) :
    countBelief (advance n o) = (coarseModel sensorLaw contract).next (countBelief n) () o
      (by rw [← count_report_eq]; exact ho) := by
  apply Subtype.ext
  funext z
  rcases z with ⟨b,s⟩
  have ha := wTrue_pos n; have hb := wFalse_pos n
  have ht := ne_of_gt (total_pos n)
  have hu : 3*wTrue n+wFalse n ≠ 0 := ne_of_gt (by positivity)
  have hv : wTrue n+3*wFalse n ≠ 0 := ne_of_gt (by positivity)
  cases o <;> cases b <;> cases s <;>
    simp [advance, countBelief, coarseModel, sensorLaw, normalize, mass, applyKernel,
      Fintype.sum_prod_type, accuracy, total, wTrue, wFalse, pow_succ] at * <;>
    field_simp

/-- The count interface is proved to be the actual Bayesian sensor, not an independently asserted model. -/
theorem countMap : ExactMap countModel (coarseModel sensorLaw contract) countBelief where
  actions _ := rfl
  decisions _ := rfl
  cost _ _ := rfl
  loss := count_loss_eq
  prob n a o := by cases a; exact count_report_eq n o
  next n a o ho := by cases a; exact count_update_eq n o ho

/-- A reduced arithmetic recursion, derived below from the finite-choice Bellman equation. -/
def scalarValue : Nat → Counts → ℝ
  | 0,n => min (stopRisk n false) (stopRisk n true)
  | h+1,n => min (min (stopRisk n false) (stopRisk n true))
      (1/20 + report n false * scalarValue h (advance n false) +
        report n true * scalarValue h (advance n true))

theorem count_zero (n : Counts) : value countModel 0 n =
    min (stopRisk n false) (stopRisk n true) := by
  apply le_antisymm
  · exact le_min (value_le_stop countModel 0 n false (by simp [countModel]))
      (value_le_stop countModel 0 n true (by simp [countModel]))
  · apply le_finiteMin
    intro d _
    cases d
    · exact min_le_left _ _
    · exact min_le_right _ _

theorem count_succ (h : Nat) (n : Counts) : value countModel (h+1) n =
    min (min (stopRisk n false) (stopRisk n true)) (backup countModel (value countModel h) n ()) := by
  apply le_antisymm
  · exact le_min (le_min (value_le_stop countModel _ n false (by simp [countModel]))
        (value_le_stop countModel _ n true (by simp [countModel])))
      (value_le_experiment countModel h n () (by simp [countModel]))
  · apply le_finiteMin
    intro c _
    cases c with
    | inl d =>
        cases d
        · exact le_trans (min_le_left _ _) (min_le_left _ _)
        · exact le_trans (min_le_left _ _) (min_le_right _ _)
    | inr a => cases a; exact min_le_right _ _

theorem count_value_eq_scalar (h : Nat) (n : Counts) : value countModel h n = scalarValue h n := by
  induction h generalizing n with
  | zero => exact count_zero n
  | succ h ih =>
      rw [count_succ]
      simp only [scalarValue]
      congr 1
      change (1/20 : ℝ) + (∑ o, if _ : 0 < report n o then
        report n o * value countModel h (advance n o) else 0) = _
      simp only [Fintype.sum_bool, report_pos, dite_true, ih]
      ring

/-- Exact values from the manuscript; Lean computes the finite recursion in rational real arithmetic. -/
theorem sensor_value_table :
    value countModel 0 (0,0) = 1/2 ∧ value countModel 1 (0,0) = 3/10 ∧
    value countModel 2 (0,0) = 3/10 ∧ value countModel 3 (0,0) = 11/40 := by
  simp only [count_value_eq_scalar]
  norm_num [scalarValue, stopRisk, report, advance, total, wTrue, wFalse]

/-- The same exact numbers are the values of the genuine coarse instrument, not just the count code. -/
theorem coarse_sensor_value_three :
    value (coarseModel sensorLaw contract) 3 (countBelief (0,0)) = 11/40 := by
  rw [← countMap.value_eq]
  exact sensor_value_table.2.2.2

/-- The source adaptive policy: inspect twice; use a third report only on disagreement. -/
def adaptiveThree : Tree Unit Bool Bool :=
  .experiment () (fun first => .experiment () (fun second =>
    if first = second then .stop first else .experiment () (fun third => .stop third)))

theorem adaptiveThree_bounded : adaptiveThree.Bounded 3 := by
  simp [adaptiveThree, Tree.Bounded]

theorem adaptiveThree_not_bounded_two : ¬ adaptiveThree.Bounded 2 := by
  simp [adaptiveThree, Tree.Bounded]

theorem adaptiveThree_feasible (n : Counts) : Feasible countModel 3 n adaptiveThree := by
  simp [adaptiveThree, Feasible, countModel]

theorem adaptiveThree_value : evaluate countModel adaptiveThree (0,0) = 11/40 := by
  norm_num [adaptiveThree, evaluate, countModel, report, advance, stopRisk, total, wTrue, wFalse]

theorem adaptiveThree_optimal :
    Feasible countModel 3 (0,0) adaptiveThree ∧
    (∀ P, Feasible countModel 3 (0,0) P →
      evaluate countModel adaptiveThree (0,0) ≤ evaluate countModel P (0,0)) := by
  refine ⟨adaptiveThree_feasible (0,0), ?_⟩
  intro P hp
  rw [adaptiveThree_value, ← sensor_value_table.2.2.2]
  exact value_le_tree countModel 3 (0,0) P hp

/-- The third report is genuinely reachable, with exact probability 3/8. -/
theorem adaptive_third_report_probability :
    report (0,0) false * report (advance (0,0) false) true +
      report (0,0) true * report (advance (0,0) true) false = 3/8 := by
  norm_num [report, advance, total, wTrue, wFalse]

/-- This auxiliary evaluator counts reports on exactly the same branches. -/
def reportCounter : Model Counts Unit Bool Bool :=
  { countModel with
    cost := fun _ _ => 1
    cost_nonnegative := by intros; norm_num
    loss := fun _ _ => 0 }

/-- This auxiliary evaluator charges only the terminal classification error. -/
def errorCounter : Model Counts Unit Bool Bool :=
  { countModel with
    cost := fun _ _ => 0
    cost_nonnegative := by intros; norm_num }

theorem adaptiveThree_reports : evaluate reportCounter adaptiveThree (0,0) = 19/8 := by
  norm_num [reportCounter, adaptiveThree, evaluate, countModel, report, advance, stopRisk, total, wTrue, wFalse]

theorem adaptiveThree_error : evaluate errorCounter adaptiveThree (0,0) = 5/32 := by
  norm_num [errorCounter, adaptiveThree, evaluate, countModel, report, advance, stopRisk, total, wTrue, wFalse]

theorem cost_and_error_are_same_tree :
    evaluate countModel adaptiveThree (0,0) =
      (1/20) * evaluate reportCounter adaptiveThree (0,0) + evaluate errorCounter adaptiveThree (0,0) := by
  rw [adaptiveThree_value, adaptiveThree_reports, adaptiveThree_error]
  norm_num

/-- The actual finite sensor tree is optimal for every eight-world prior with this same coarse belief. -/
theorem eight_world_adaptive_optimal (p : Belief World)
    (hp : aggregate project p = countBelief (0,0)) :
    Feasible (fineModel fineLaw project contract) 3 p adaptiveThree ∧
    evaluate (fineModel fineLaw project contract) adaptiveThree p = 11/40 ∧
    ∀ P, Feasible (fineModel fineLaw project contract) 3 p P →
      (11/40 : ℝ) ≤ evaluate (fineModel fineLaw project contract) P p := by
  have H := instrumentMap fineLaw sensorLaw project sensor_joint_quotient contract
  have hc := countMap.feasible_iff 3 (0,0) adaptiveThree
  have hv := countMap.evaluate_eq adaptiveThree (0,0)
  refine ⟨?_, ?_, ?_⟩
  · apply (H.feasible_iff 3 p adaptiveThree).mpr
    rw [hp]
    exact hc.mp (adaptiveThree_feasible (0,0))
  · rw [H.evaluate_eq, hp, ← hv, adaptiveThree_value]
  · intro P hP
    have he : value (fineModel fineLaw project contract) 3 p = 11/40 := by
      rw [H.value_eq, hp, coarse_sensor_value_three]
    rw [← he]
    exact value_le_tree _ 3 p P hP

/-- Realization of an initial fine prior, not just an assumption that the fibre is inhabited. -/
def initialFine : Belief World :=
  ⟨fun x => if x.1 = x.2.1 then 1/4 else 0, by
    constructor
    · intro x; dsimp; split_ifs <;> norm_num
    · norm_num [mass, Fintype.sum_prod_type]⟩

theorem initialFine_aggregates : aggregate project initialFine = countBelief (0,0) := by
  apply Subtype.ext
  funext z
  rcases z with ⟨b,s⟩
  cases b <;> cases s <;>
    norm_num [aggregate, push, project, initialFine, countBelief, total, wTrue, wFalse,
      Fintype.sum_prod_type]

theorem source_sensor_optimum :
    value (fineModel fineLaw project contract) 3 initialFine = 11/40 := by
  rw [sensor_all_prior_values, initialFine_aggregates, coarse_sensor_value_three]

end
end Komorebi.MachineTheory.PlanningSensor
