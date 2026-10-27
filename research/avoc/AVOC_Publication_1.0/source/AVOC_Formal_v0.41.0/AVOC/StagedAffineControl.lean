import AVOC.AffineTerminal
import AVOC.ExecutablePlanner
import Mathlib.Tactic.Linarith
import Lean.Elab.Tactic.Omega

namespace Komorebi.AVOC.Affine.Staged

open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

/-- A possible checked deployment returned by a paid operational stage.
The probability models whether that operation returns this valid result. -/
structure OptionPlan {n m : Nat} (expected : Kind) (source : DenseProgram F n m) where
  deployment : Deployment n m
  source_eq : deployment.source = source
  kind_eq : deployment.kind = expected
  successProb : ℚ
  prob_nonneg : 0 ≤ successProb
  prob_le_one : successProb ≤ 1

namespace OptionPlan

variable {n m : Nat} {k : Kind} {source : DenseProgram F n m}

/-- Gross deployment savings before the operational setup fee is charged. -/
def grossSaving (p : OptionPlan k source) (calls : Nat) : ℚ :=
  (calls : ℚ) * ((executionCost source : ℚ) - (executionCost p.deployment.selected : ℚ))

@[simp] theorem grossSaving_nonneg (p : OptionPlan k source) (calls : Nat) :
    0 ≤ p.grossSaving calls := by
  unfold grossSaving
  have hcost : executionCost p.deployment.selected ≤ executionCost source := by
    calc
      executionCost p.deployment.selected ≤ executionCost p.deployment.source :=
        p.deployment.noWorse
      _ = executionCost source := congrArg executionCost p.source_eq
  exact mul_nonneg (by positivity) (sub_nonneg.mpr (by exact_mod_cast hcost))

/-- Paying the operational stage and then deploying reproduces the deployment's
original net-payoff definition. -/
theorem fee_then_gross_eq_payoff (p : OptionPlan k source) (calls : Nat) :
    -(p.deployment.setup : ℚ) + p.grossSaving calls = p.deployment.payoff calls := by
  unfold grossSaving Deployment.payoff MultiLevelEconomics.netGain
  rw [p.source_eq]
  ring

end OptionPlan

/-- A single-workload staged model. Cache inspection and cold generation are
nonterminal, paid, fallible operations. Their successful results already carry
semantic and cost proofs. -/
structure Model (n m : Nat) where
  source : DenseProgram F n m
  calls : Nat
  warm : OptionPlan .warm source
  cold : OptionPlan .cold source

inductive Status where
  | untried | failed | ready
  deriving Repr, DecidableEq

structure State {n m : Nat} (md : Model n m) where
  warmStatus : Status
  coldStatus : Status
  budget : Nat
  spent : Nat
  total : Nat
  done : Bool

inductive Action where
  | stop
  | inspectWarm
  | generateCold
  | deployWarm
  | deployCold
  deriving Repr, DecidableEq

variable {n m : Nat}

/-- Initial state with one common operational envelope. -/
def initial (md : Model n m) (credit : Nat) : State md :=
  ⟨.untried,.untried,credit,0,credit,false⟩

@[simp] theorem initial_budget (md : Model n m) (credit : Nat) :
    (initial md credit).budget + (initial md credit).spent = credit := by rfl


def warmFee (md : Model n m) : Nat := md.warm.deployment.setup
def coldFee (md : Model n m) : Nat := md.cold.deployment.setup

/-- The action list preserves a stable tie order: stop, warm inspection, cold
search, warm deployment, cold deployment. -/
def actionList (md : Model n m) (s : State md) : List Action :=
  if s.done then [.stop]
  else [.stop] ++
    (if s.warmStatus = .untried ∧ warmFee md ≤ s.budget then [.inspectWarm] else []) ++
    (if s.coldStatus = .untried ∧ coldFee md ≤ s.budget then [.generateCold] else []) ++
    (if s.warmStatus = .ready then [.deployWarm] else []) ++
    (if s.coldStatus = .ready then [.deployCold] else [])


def actions (md : Model n m) (s : State md) : Finset Action :=
  (actionList md s).toFinset

@[simp] theorem mem_actionList (md : Model n m) (s : State md) (a : Action) :
    a ∈ actionList md s ↔ a ∈ actions md s := by simp [actions]

theorem stop_mem_actions (md : Model n m) (s : State md) : .stop ∈ actions md s := by
  cases hd : s.done <;> simp [actions,actionList,hd]


theorem inspectWarm_mem_iff (md : Model n m) (s : State md) :
    .inspectWarm ∈ actions md s ↔
      s.done = false ∧ s.warmStatus = .untried ∧ warmFee md ≤ s.budget := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]


theorem generateCold_mem_iff (md : Model n m) (s : State md) :
    .generateCold ∈ actions md s ↔
      s.done = false ∧ s.coldStatus = .untried ∧ coldFee md ≤ s.budget := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]


theorem deployWarm_mem_iff (md : Model n m) (s : State md) :
    .deployWarm ∈ actions md s ↔ s.done = false ∧ s.warmStatus = .ready := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]


theorem deployCold_mem_iff (md : Model n m) (s : State md) :
    .deployCold ∈ actions md s ↔ s.done = false ∧ s.coldStatus = .ready := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]


def probability (md : Model n m) (_s : State md) (a : Action) (o : Bool) : ℚ :=
  match a with
  | .inspectWarm => if o then md.warm.successProb else 1-md.warm.successProb
  | .generateCold => if o then md.cold.successProb else 1-md.cold.successProb
  | _ => if o then 0 else 1


theorem probability_nonneg (md : Model n m) (s : State md) (a : Action) (o : Bool) :
    0 ≤ probability md s a o := by
  cases a <;> cases o <;> simp [probability,md.warm.prob_nonneg,md.warm.prob_le_one,
    md.cold.prob_nonneg,md.cold.prob_le_one]


theorem probability_sum_one (md : Model n m) (s : State md) (a : Action) :
    ∑ o : Bool, probability md s a o = 1 := by
  cases a <;> simp [probability]


def spend (s : State md) (fee : Nat) : State md :=
  { s with budget := s.budget-fee, spent := s.spent+fee }


def terminal (s : State md) : State md := { s with done := true }


def step (md : Model n m) (s : State md) (a : Action) (o : Bool) : State md :=
  match a with
  | .stop => terminal s
  | .deployWarm => terminal s
  | .deployCold => terminal s
  | .inspectWarm =>
      let paid := spend s (warmFee md)
      { paid with warmStatus := if o then .ready else .failed }
  | .generateCold =>
      let paid := spend s (coldFee md)
      { paid with coldStatus := if o then .ready else .failed }


def reward (md : Model n m) (_s : State md) : Action → ℚ
  | .stop => 0
  | .inspectWarm => -(warmFee md : ℚ)
  | .generateCold => -(coldFee md : ℚ)
  | .deployWarm => md.warm.grossSaving md.calls
  | .deployCold => md.cold.grossSaving md.calls


def system (md : Model n m) : Guarded.System (State md) Action Bool where
  actions := actions md
  actions_nonempty s := ⟨.stop,stop_mem_actions md s⟩
  prob := probability md
  prob_nonneg := probability_nonneg md
  prob_sum_one := probability_sum_one md
  step := step md
  reward := reward md


def executable (md : Model n m) : ExecutablePlanner.Model (State md) Action Bool where
  actions := actionList md
  observations := [false,true]
  prob := probability md
  step := step md
  reward := reward md


theorem executable_realizes (md : Model n m) :
    ExecutablePlanner.Realizes (executable md) (system md) where
  actions_iff := mem_actionList md
  observations_nodup := by simp [executable]
  observations_full := by ext o; cases o <;> simp [executable]
  prob_eq := rfl
  step_eq := rfl
  reward_eq := rfl


theorem evaluated_value_exact (md : Model n m) (h : Nat) (s : State md) :
    (ExecutablePlanner.evaluate (executable md) h s).score = Guarded.value (system md) h s :=
  ExecutablePlanner.evaluate_exact _ _ (executable_realizes md) h s


theorem evaluated_choice_optimal (md : Model n m) (h : Nat) (s : State md) :
    ∃ a, (ExecutablePlanner.evaluate (executable md) (h+1) s).choice = some a ∧
      a ∈ (system md).actions s ∧ ∀ b ∈ (system md).actions s,
        Guarded.qValue (system md) h s b ≤ Guarded.qValue (system md) h s a :=
  ExecutablePlanner.evaluate_choice_optimal _ _ (executable_realizes md) h s

/-- Exact common-envelope accounting. -/
def BudgetSafe (credit : Nat) (s : State md) : Prop := s.budget+s.spent=credit


theorem spend_preserves (s : State md) (fee credit : Nat)
    (hs : BudgetSafe credit s) (hf : fee ≤ s.budget) :
    BudgetSafe credit (spend s fee) := by
  unfold BudgetSafe spend at *
  simp only
  omega


theorem terminal_preserves (s : State md) (credit : Nat) (hs : BudgetSafe credit s) :
    BudgetSafe credit (terminal s) := hs


theorem step_budgetSafe (md : Model n m) (s : State md) (credit : Nat)
    (hs : BudgetSafe credit s) (a : Action) (ha : a ∈ actions md s) (o : Bool) :
    BudgetSafe credit (step md s a o) := by
  cases a with
  | stop => exact terminal_preserves s credit hs
  | deployWarm => exact terminal_preserves s credit hs
  | deployCold => exact terminal_preserves s credit hs
  | inspectWarm =>
      apply spend_preserves s (warmFee md) credit hs
      exact (inspectWarm_mem_iff md s).1 ha |>.2.2
  | generateCold =>
      apply spend_preserves s (coldFee md) credit hs
      exact (generateCold_mem_iff md s).1 ha |>.2.2


theorem budget_preserves (md : Model n m) (credit : Nat) :
    Guarded.Preserves (system md) (BudgetSafe credit) := by
  intro s hs a ha o
  exact step_budgetSafe md s credit hs a ha o


theorem safe_optimal_plan_exists (md : Model n m) (credit h : Nat)
    (s : State md) (hs : BudgetSafe credit s) :
    ∃ p : Guarded.Plan Action Bool h,
      Guarded.Legal (system md) s p ∧
      Guarded.TreeSafe (system md) (BudgetSafe credit) s p ∧
      Guarded.planValue (system md) s p = Guarded.value (system md) h s ∧
      ∀ q : Guarded.Plan Action Bool h, Guarded.Legal (system md) s q →
        Guarded.planValue (system md) s q ≤ Guarded.planValue (system md) s p :=
  Guarded.safe_optimal_plan_exists (system md) (BudgetSafe credit)
    (budget_preserves md credit) h s hs

/-- A staged successful warm operation followed by deployment reproduces the
proof-carrying deployment payoff. -/
theorem warm_stage_then_deploy (md : Model n m) (s : State md) :
    reward md s .inspectWarm + reward md s .deployWarm =
      md.warm.deployment.payoff md.calls := by
  simpa [reward,warmFee] using md.warm.fee_then_gross_eq_payoff md.calls


theorem cold_stage_then_deploy (md : Model n m) (s : State md) :
    reward md s .generateCold + reward md s .deployCold =
      md.cold.deployment.payoff md.calls := by
  simpa [reward,coldFee] using md.cold.fee_then_gross_eq_payoff md.calls

/-- Once halted, only stop remains and every finite continuation value is zero. -/
theorem halted_value_zero (md : Model n m) (h : Nat) (s : State md) (hd : s.done=true) :
    Guarded.value (system md) h s = 0 := by
  induction h generalizing s with
  | zero => rfl
  | succ h ih =>
      rw [Guarded.value_eq_q_of_optimal (system md) h s .stop (stop_mem_actions md s)]
      · change reward md s .stop + ∑ o, probability md s .stop o *
          Guarded.value (system md) h (step md s .stop o) = 0
        have hz : ∀ o, Guarded.value (system md) h (step md s .stop o) = 0 := by
          intro o
          exact ih _ rfl
        simp_rw [hz]
        simp [reward,probability]
      · intro a ha
        have hacts : (system md).actions s = {.stop} := by
          change actions md s = {.stop}
          simp [actions,actionList,hd]
        rw [hacts] at ha
        have hstop : a = .stop := by simpa using ha
        subst a
        exact le_rfl

end Komorebi.AVOC.Affine.Staged
