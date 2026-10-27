import AVOC.StagedAffineControl
import AVOC.StagedAffineOperational

namespace Komorebi.AVOC.Affine.LazyStaged

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Status Action)

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

/-- Planning metadata.  It contains no proof artifact. -/
structure Quote (expected : Kind) where
  fee : Nat
  gross : ℚ
  gross_nonneg : 0 ≤ gross
  successProb : ℚ
  prob_nonneg : 0 ≤ successProb
  prob_le_one : successProb ≤ 1

structure Model (n m : Nat) where
  source : DenseProgram F n m
  calls : Nat
  warm : Quote .warm
  cold : Quote .cold

variable {n m : Nat}

structure PlanState (md : Model n m) where
  warmStatus : Status
  coldStatus : Status
  budget : Nat
  spent : Nat
  total : Nat
  done : Bool
  deriving Repr, DecidableEq

def initialPlan (md : Model n m) (credit : Nat) : PlanState md :=
  ⟨.untried,.untried,credit,0,credit,false⟩

@[simp] theorem initialPlan_budget (md : Model n m) (credit : Nat) :
    (initialPlan md credit).budget + (initialPlan md credit).spent = credit := rfl

def quote : (md : Model n m) → (k : Kind) → Quote k
  | md, .warm => md.warm
  | md, .cold => md.cold

def warmFee (md : Model n m) : Nat := md.warm.fee
def coldFee (md : Model n m) : Nat := md.cold.fee

def actionList (md : Model n m) (s : PlanState md) : List Action :=
  if s.done then [.stop]
  else [.stop] ++
    (if s.warmStatus = .untried ∧ warmFee md ≤ s.budget then [.inspectWarm] else []) ++
    (if s.coldStatus = .untried ∧ coldFee md ≤ s.budget then [.generateCold] else []) ++
    (if s.warmStatus = .ready then [.deployWarm] else []) ++
    (if s.coldStatus = .ready then [.deployCold] else [])

def actions (md : Model n m) (s : PlanState md) : Finset Action :=
  (actionList md s).toFinset

@[simp] theorem mem_actionList (md : Model n m) (s : PlanState md) (a : Action) :
    a ∈ actionList md s ↔ a ∈ actions md s := by simp [actions]

theorem stop_mem_actions (md : Model n m) (s : PlanState md) : .stop ∈ actions md s := by
  cases hd : s.done <;> simp [actions,actionList,hd]

theorem inspectWarm_mem_iff (md : Model n m) (s : PlanState md) :
    .inspectWarm ∈ actions md s ↔
      s.done = false ∧ s.warmStatus = .untried ∧ warmFee md ≤ s.budget := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]

theorem generateCold_mem_iff (md : Model n m) (s : PlanState md) :
    .generateCold ∈ actions md s ↔
      s.done = false ∧ s.coldStatus = .untried ∧ coldFee md ≤ s.budget := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]

theorem deployWarm_mem_iff (md : Model n m) (s : PlanState md) :
    .deployWarm ∈ actions md s ↔ s.done = false ∧ s.warmStatus = .ready := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]

theorem deployCold_mem_iff (md : Model n m) (s : PlanState md) :
    .deployCold ∈ actions md s ↔ s.done = false ∧ s.coldStatus = .ready := by
  cases hd : s.done <;> cases hw : s.warmStatus <;> cases hc : s.coldStatus <;>
    simp [actions,actionList,hd,hw,hc]

def probability (md : Model n m) (_s : PlanState md) (a : Action) (o : Bool) : ℚ :=
  match a with
  | .inspectWarm => if o then md.warm.successProb else 1-md.warm.successProb
  | .generateCold => if o then md.cold.successProb else 1-md.cold.successProb
  | _ => if o then 0 else 1

theorem probability_nonneg (md : Model n m) (s : PlanState md) (a : Action) (o : Bool) :
    0 ≤ probability md s a o := by
  cases a <;> cases o <;> simp [probability,md.warm.prob_nonneg,md.warm.prob_le_one,
    md.cold.prob_nonneg,md.cold.prob_le_one]

theorem probability_sum_one (md : Model n m) (s : PlanState md) (a : Action) :
    ∑ o : Bool, probability md s a o = 1 := by
  cases a <;> simp [probability]

def spend (s : PlanState md) (fee : Nat) : PlanState md :=
  { s with budget := s.budget-fee, spent := s.spent+fee }

def terminal (s : PlanState md) : PlanState md := { s with done := true }

def step (md : Model n m) (s : PlanState md) (a : Action) (o : Bool) : PlanState md :=
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

def reward (md : Model n m) (_s : PlanState md) : Action → ℚ
  | .stop => 0
  | .inspectWarm => -(warmFee md : ℚ)
  | .generateCold => -(coldFee md : ℚ)
  | .deployWarm => md.warm.gross
  | .deployCold => md.cold.gross

def system (md : Model n m) : Guarded.System (PlanState md) Action Bool where
  actions := actions md
  actions_nonempty s := ⟨.stop,stop_mem_actions md s⟩
  prob := probability md
  prob_nonneg := probability_nonneg md
  prob_sum_one := probability_sum_one md
  step := step md
  reward := reward md

def executable (md : Model n m) : ExecutablePlanner.Model (PlanState md) Action Bool where
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

theorem evaluated_value_exact (md : Model n m) (h : Nat) (s : PlanState md) :
    (ExecutablePlanner.evaluate (executable md) h s).score = Guarded.value (system md) h s :=
  ExecutablePlanner.evaluate_exact _ _ (executable_realizes md) h s

theorem evaluated_choice_optimal (md : Model n m) (h : Nat) (s : PlanState md) :
    ∃ a, (ExecutablePlanner.evaluate (executable md) (h+1) s).choice = some a ∧
      a ∈ (system md).actions s ∧ ∀ b ∈ (system md).actions s,
        Guarded.qValue (system md) h s b ≤ Guarded.qValue (system md) h s a :=
  ExecutablePlanner.evaluate_choice_optimal _ _ (executable_realizes md) h s

def BudgetSafe (credit : Nat) (s : PlanState md) : Prop := s.budget+s.spent=credit

theorem spend_preserves (s : PlanState md) (fee credit : Nat)
    (hs : BudgetSafe credit s) (hf : fee ≤ s.budget) :
    BudgetSafe credit (spend s fee) := by
  unfold BudgetSafe spend at *
  simp only
  omega

theorem step_budgetSafe (md : Model n m) (s : PlanState md) (credit : Nat)
    (hs : BudgetSafe credit s) (a : Action) (ha : a ∈ actions md s) (o : Bool) :
    BudgetSafe credit (step md s a o) := by
  cases a with
  | stop => exact hs
  | deployWarm => exact hs
  | deployCold => exact hs
  | inspectWarm =>
      apply spend_preserves s (warmFee md) credit hs
      exact (inspectWarm_mem_iff md s).1 ha |>.2.2
  | generateCold =>
      apply spend_preserves s (coldFee md) credit hs
      exact (generateCold_mem_iff md s).1 ha |>.2.2

def deploymentGross (d : Deployment n m) (calls : Nat) : ℚ :=
  (calls : ℚ) * ((executionCost d.source : ℚ) - (executionCost d.selected : ℚ))

/-- A proof-carrying result that agrees exactly with the quote used by planning. -/
structure CheckedArtifact (md : Model n m) (k : Kind) where
  deployment : Deployment n m
  kind_eq : deployment.kind = k
  source_eq : deployment.source = md.source
  setup_eq : deployment.setup = (quote md k).fee
  gross_eq : deploymentGross deployment md.calls = (quote md k).gross

namespace CheckedArtifact

variable {md : Model n m} {k : Kind}

theorem semantic (a : CheckedArtifact md k) (x : Fin n → F) :
    execute a.deployment.selected x = execute md.source x := by
  exact (a.deployment.correct x).trans
    (congrArg (fun p => execute p x) a.source_eq)

theorem noWorse (a : CheckedArtifact md k) :
    executionCost a.deployment.selected ≤ executionCost md.source := by
  calc
    executionCost a.deployment.selected ≤ executionCost a.deployment.source := a.deployment.noWorse
    _ = executionCost md.source := congrArg executionCost a.source_eq

theorem fee_then_gross (a : CheckedArtifact md k) :
    -((quote md k).fee : ℚ) + (quote md k).gross = a.deployment.payoff md.calls := by
  rw [← a.setup_eq, ← a.gross_eq]
  unfold deploymentGross Deployment.payoff MultiLevelEconomics.netGain
  ring

end CheckedArtifact

structure RuntimeState (md : Model n m) where
  plan : PlanState md
  warmArtifact : Option (CheckedArtifact md .warm)
  coldArtifact : Option (CheckedArtifact md .cold)

def initial (md : Model n m) (credit : Nat) : RuntimeState md :=
  ⟨initialPlan md credit, none, none⟩

def Coherent (s : RuntimeState md) : Prop :=
  (s.plan.warmStatus = .ready ↔ ∃ a, s.warmArtifact = some a) ∧
  (s.plan.coldStatus = .ready ↔ ∃ a, s.coldArtifact = some a)

def Safe (credit : Nat) (s : RuntimeState md) : Prop :=
  BudgetSafe credit s.plan ∧ Coherent s

@[simp] theorem initial_safe (md : Model n m) (credit : Nat) : Safe credit (initial md credit) := by
  simp [Safe,Coherent,initial,initialPlan,BudgetSafe]

inductive Outcome (md : Model n m) where
  | noExternal
  | rejected
  | warmSuccess (artifact : CheckedArtifact md .warm)
  | coldSuccess (artifact : CheckedArtifact md .cold)
  | fault

inductive OutcomeTag where
  | noExternal | rejected | warmSuccess | coldSuccess | fault
  deriving Repr, DecidableEq

def Outcome.tag : Outcome md → OutcomeTag
  | .noExternal => .noExternal
  | .rejected => .rejected
  | .warmSuccess _ => .warmSuccess
  | .coldSuccess _ => .coldSuccess
  | .fault => .fault

def reportOf : Action → Outcome md → Option Bool
  | .stop, .noExternal => some false
  | .deployWarm, .noExternal => some false
  | .deployCold, .noExternal => some false
  | .inspectWarm, .rejected => some false
  | .inspectWarm, .warmSuccess _ => some true
  | .generateCold, .rejected => some false
  | .generateCold, .coldSuccess _ => some true
  | _, _ => none

def Supported (md : Model n m) (s : PlanState md) (a : Action) (o : Bool) : Prop :=
  a ∈ actions md s ∧ 0 < probability md s a o

def install (s : RuntimeState md) (a : Action) (r : Outcome md) (p : PlanState md) :
    RuntimeState md :=
  match a,r with
  | .inspectWarm,.warmSuccess art => ⟨p,some art,s.coldArtifact⟩
  | .inspectWarm,.rejected => ⟨p,none,s.coldArtifact⟩
  | .generateCold,.coldSuccess art => ⟨p,s.warmArtifact,some art⟩
  | .generateCold,.rejected => ⟨p,s.warmArtifact,none⟩
  | _,_ => ⟨p,s.warmArtifact,s.coldArtifact⟩

def supportedCheck (md : Model n m) (s : PlanState md) (a : Action) (o : Bool) : Bool :=
  decide (a ∈ actions md s) && decide (0 < probability md s a o)

@[simp] theorem supportedCheck_eq_true_iff (md : Model n m) (s : PlanState md)
    (a : Action) (o : Bool) :
    supportedCheck md s a o = true ↔ Supported md s a o := by
  simp [supportedCheck,Supported]

/-- Executable counterpart of `confirm`; all tests are finite Boolean/rational tests. -/
def confirmExec (md : Model n m) (s : RuntimeState md) (a : Action) (r : Outcome md) :
    Option (RuntimeState md) :=
  match reportOf a r with
  | none => none
  | some o => if supportedCheck md s.plan a o then
      some (install s a r (step md s.plan a o)) else none

noncomputable def confirm (md : Model n m) (s : RuntimeState md) (a : Action) (r : Outcome md) :
    Option (RuntimeState md) := by
  classical
  exact   match reportOf a r with
  | none => none
  | some o => if Supported md s.plan a o then some (install s a r (step md s.plan a o)) else none

theorem confirmExec_eq_confirm (md : Model n m) (s : RuntimeState md)
    (a : Action) (r : Outcome md) : confirmExec md s a r = confirm md s a r := by
  cases hr : reportOf a r with
  | none => simp [confirmExec,confirm,hr]
  | some o =>
      by_cases hs : Supported md s.plan a o
      · have hb : supportedCheck md s.plan a o = true :=
          (supportedCheck_eq_true_iff md s.plan a o).2 hs
        simp [confirmExec,confirm,hr,hs,hb]
      · have hb : supportedCheck md s.plan a o = false := by
          cases h : supportedCheck md s.plan a o with
          | false => rfl
          | true => exact False.elim (hs ((supportedCheck_eq_true_iff md s.plan a o).1 h))
        simp [confirmExec,confirm,hr,hs,hb]

@[simp] theorem fault_rejected (md : Model n m) (s : RuntimeState md) (a : Action) :
    confirm md s a .fault = none := by cases a <;> rfl

theorem confirm_exact (md : Model n m) (s t : RuntimeState md) (a : Action)
    (r : Outcome md) (h : confirm md s a r = some t) :
    ∃ o, reportOf a r = some o ∧ Supported md s.plan a o ∧
      t = install s a r (step md s.plan a o) := by
  cases hro : reportOf a r with
  | none => simp [confirm,hro] at h
  | some o =>
      by_cases hs : Supported md s.plan a o
      · have ht : install s a r (step md s.plan a o) = t := by
          simpa [confirm,hro,hs] using h
        exact ⟨o,rfl,hs,ht.symm⟩
      · simp [confirm,hro,hs] at h

theorem confirm_plan (md : Model n m) (s t : RuntimeState md) (a : Action)
    (r : Outcome md) (h : confirm md s a r = some t) :
    ∃ o, Supported md s.plan a o ∧ t.plan = step md s.plan a o := by
  obtain ⟨o,_,hs,rfl⟩ := confirm_exact md s t a r h
  refine ⟨o,hs,?_⟩
  cases a <;> cases r <;> rfl

theorem confirm_budgetSafe (md : Model n m) (credit : Nat) (s t : RuntimeState md)
    (a : Action) (r : Outcome md) (hs : BudgetSafe credit s.plan)
    (h : confirm md s a r = some t) : BudgetSafe credit t.plan := by
  obtain ⟨o,ha,he⟩ := confirm_plan md s t a r h
  rw [he]
  exact step_budgetSafe md s.plan credit hs a ha.1 o

theorem confirm_coherent (md : Model n m) (s t : RuntimeState md)
    (a : Action) (r : Outcome md) (hs : Coherent s)
    (h : confirm md s a r = some t) : Coherent t := by
  obtain ⟨o,hr,hp,rfl⟩ := confirm_exact md s t a r h
  cases a with
  | stop =>
      cases r with
      | noExternal => simpa [reportOf,install,step,terminal,Coherent] using hs
      | rejected => simp [reportOf] at hr
      | warmSuccess art => simp [reportOf] at hr
      | coldSuccess art => simp [reportOf] at hr
      | fault => simp [reportOf] at hr
  | inspectWarm =>
      cases r with
      | noExternal => simp [reportOf] at hr
      | rejected =>
          simp [reportOf] at hr
          subst o
          refine ⟨by simp [install,step,spend], ?_⟩
          simpa [install,step,spend] using hs.2
      | warmSuccess art =>
          simp [reportOf] at hr
          subst o
          refine ⟨by simp [install,step,spend], ?_⟩
          simpa [install,step,spend] using hs.2
      | coldSuccess art => simp [reportOf] at hr
      | fault => simp [reportOf] at hr
  | generateCold =>
      cases r with
      | noExternal => simp [reportOf] at hr
      | rejected =>
          simp [reportOf] at hr
          subst o
          refine ⟨?_, by simp [install,step,spend]⟩
          simpa [install,step,spend] using hs.1
      | warmSuccess art => simp [reportOf] at hr
      | coldSuccess art =>
          simp [reportOf] at hr
          subst o
          refine ⟨?_, by simp [install,step,spend]⟩
          simpa [install,step,spend] using hs.1
      | fault => simp [reportOf] at hr
  | deployWarm =>
      cases r with
      | noExternal => simpa [reportOf,install,step,terminal,Coherent] using hs
      | rejected => simp [reportOf] at hr
      | warmSuccess art => simp [reportOf] at hr
      | coldSuccess art => simp [reportOf] at hr
      | fault => simp [reportOf] at hr
  | deployCold =>
      cases r with
      | noExternal => simpa [reportOf,install,step,terminal,Coherent] using hs
      | rejected => simp [reportOf] at hr
      | warmSuccess art => simp [reportOf] at hr
      | coldSuccess art => simp [reportOf] at hr
      | fault => simp [reportOf] at hr

theorem confirm_safe (md : Model n m) (credit : Nat) (s t : RuntimeState md)
    (a : Action) (r : Outcome md) (hs : Safe credit s)
    (h : confirm md s a r = some t) : Safe credit t :=
  ⟨confirm_budgetSafe md credit s t a r hs.1 h,
    confirm_coherent md s t a r hs.2 h⟩

theorem warm_success_stores_exact (md : Model n m) (s t : RuntimeState md)
    (a : CheckedArtifact md .warm)
    (h : confirm md s .inspectWarm (.warmSuccess a) = some t) :
    t.plan.warmStatus = .ready ∧ t.warmArtifact = some a := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .inspectWarm (.warmSuccess a) h
  simp [reportOf] at hr
  subst o
  simp [install,step,spend]

theorem cold_success_stores_exact (md : Model n m) (s t : RuntimeState md)
    (a : CheckedArtifact md .cold)
    (h : confirm md s .generateCold (.coldSuccess a) = some t) :
    t.plan.coldStatus = .ready ∧ t.coldArtifact = some a := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .generateCold (.coldSuccess a) h
  simp [reportOf] at hr
  subst o
  simp [install,step,spend]

theorem warm_success_preserves_cold (md : Model n m) (s t : RuntimeState md)
    (a : CheckedArtifact md .warm)
    (h : confirm md s .inspectWarm (.warmSuccess a) = some t) :
    t.coldArtifact = s.coldArtifact := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .inspectWarm (.warmSuccess a) h
  simp [reportOf] at hr
  subst o
  rfl

theorem cold_success_preserves_warm (md : Model n m) (s t : RuntimeState md)
    (a : CheckedArtifact md .cold)
    (h : confirm md s .generateCold (.coldSuccess a) = some t) :
    t.warmArtifact = s.warmArtifact := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .generateCold (.coldSuccess a) h
  simp [reportOf] at hr
  subst o
  rfl

/-- Full Bellman recommendation on quote metadata only.  No artifact is inspected here. -/
def recommend (md : Model n m) (h : Nat) (s : RuntimeState md) : Action :=
  (ExecutablePlanner.evaluate (executable md) (h+1) s.plan).choice.getD .stop

theorem recommend_allowed (md : Model n m) (h : Nat) (s : RuntimeState md) :
    recommend md h s ∈ actions md s.plan := by
  obtain ⟨a,ha,hamem,hm⟩ := evaluated_choice_optimal md h s.plan
  simpa [recommend,ha,system] using hamem

theorem recommend_optimal (md : Model n m) (h : Nat) (s : RuntimeState md) :
    ∀ b ∈ actions md s.plan,
      Guarded.qValue (system md) h s.plan b ≤
        Guarded.qValue (system md) h s.plan (recommend md h s) := by
  obtain ⟨a,ha,_,hm⟩ := evaluated_choice_optimal md h s.plan
  simpa [recommend,ha,system] using hm

end Komorebi.AVOC.Affine.LazyStaged
