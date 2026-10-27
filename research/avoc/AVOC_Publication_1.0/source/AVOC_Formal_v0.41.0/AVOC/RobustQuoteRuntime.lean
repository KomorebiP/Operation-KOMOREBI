import AVOC.RobustQuotePlanning

namespace Komorebi.AVOC.Affine.RobustQuote

open Komorebi.AVOC
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Status Action)
open Komorebi.AVOC.Affine.LazyStaged
open Komorebi.AVOC.Affine.QuoteAuthority

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

variable {n m : Nat}

/-- A proof-carrying result bound to the exact quote authority.  The deterministic
setup/gross fields are checked to lie inside the authorized intervals; the
probability band is deliberately not collapsed by an artifact. -/
structure BoundedArtifact (md : QModel n m) (k : Kind) where
  deployment : Deployment n m
  identity : Identity n m
  identity_eq : identity = quoteIdentity md k
  kind_eq : deployment.kind = k
  source_eq : deployment.source = md.source
  setup_mem : (setupBand md k).Contains deployment.setup
  gross_mem : (grossBand md k).Contains (LazyStaged.deploymentGross deployment md.calls)

namespace BoundedArtifact

variable {md : QModel n m} {k : Kind}

def gross (a : BoundedArtifact md k) : ℚ :=
  LazyStaged.deploymentGross a.deployment md.calls

def refined (a : BoundedArtifact md k) : RefinedQuote md k :=
  ⟨a.deployment.setup, a.gross, a.setup_mem, a.gross_mem⟩

@[simp] theorem refined_setup (a : BoundedArtifact md k) : a.refined.setup = a.deployment.setup := rfl
@[simp] theorem refined_gross (a : BoundedArtifact md k) : a.refined.gross = a.gross := rfl
@[simp] theorem refined_probability_unchanged (a : BoundedArtifact md k) :
    a.refined.probabilityBand = probBand md k := rfl

@[simp] theorem semantic (a : BoundedArtifact md k) (x : Fin n → F) :
    execute a.deployment.selected x = execute md.source x := by
  exact (a.deployment.correct x).trans
    (congrArg (fun p => execute p x) a.source_eq)

@[simp] theorem noWorse (a : BoundedArtifact md k) :
    executionCost a.deployment.selected ≤ executionCost md.source := by
  calc
    executionCost a.deployment.selected ≤ executionCost a.deployment.source := a.deployment.noWorse
    _ = executionCost md.source := congrArg executionCost a.source_eq

end BoundedArtifact

structure RuntimeState (md : QModel n m) where
  plan : State md
  warmArtifact : Option (BoundedArtifact md .warm)
  coldArtifact : Option (BoundedArtifact md .cold)
  warmEvidence : Option (RefinedQuote md .warm)
  coldEvidence : Option (RefinedQuote md .cold)

noncomputable def initial (md : QModel n m) (credit : Nat) : RuntimeState md :=
  ⟨LazyStaged.initialPlan (nominal md) credit, none, none, none, none⟩

def Coherent (s : RuntimeState md) : Prop :=
  (s.plan.warmStatus = .ready ↔ ∃ a, s.warmArtifact = some a ∧ s.warmEvidence = some a.refined) ∧
  (s.plan.coldStatus = .ready ↔ ∃ a, s.coldArtifact = some a ∧ s.coldEvidence = some a.refined)

def Safe (credit : Nat) (s : RuntimeState md) : Prop :=
  LazyStaged.BudgetSafe credit s.plan ∧ Coherent s

@[simp] theorem initial_safe (md : QModel n m) (credit : Nat) : Safe credit (initial md credit) := by
  simp [Safe,Coherent,initial,LazyStaged.initialPlan,LazyStaged.BudgetSafe]

inductive Outcome (md : QModel n m) where
  | noExternal
  | rejected
  | warmSuccess (artifact : BoundedArtifact md .warm)
  | coldSuccess (artifact : BoundedArtifact md .cold)
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

/-- Interval evidence says only whether a report remains possible. -/
def reportPossible (md : QModel n m) (a : Action) (o : Bool) : Prop :=
  match a with
  | .inspectWarm => if o then 0 < (probBand md .warm).upper else (probBand md .warm).lower < 1
  | .generateCold => if o then 0 < (probBand md .cold).upper else (probBand md .cold).lower < 1
  | _ => o = false

def Supported (md : QModel n m) (s : State md) (a : Action) (o : Bool) : Prop :=
  a ∈ LazyStaged.actions (nominal md) s ∧ reportPossible md a o

noncomputable def install (s : RuntimeState md) (a : Action) (r : Outcome md) (p : State md) :
    RuntimeState md :=
  match a,r with
  | .inspectWarm,.warmSuccess art => ⟨p,some art,s.coldArtifact,some art.refined,s.coldEvidence⟩
  | .inspectWarm,.rejected => ⟨p,none,s.coldArtifact,none,s.coldEvidence⟩
  | .generateCold,.coldSuccess art => ⟨p,s.warmArtifact,some art,s.warmEvidence,some art.refined⟩
  | .generateCold,.rejected => ⟨p,s.warmArtifact,none,s.warmEvidence,none⟩
  | _,_ => ⟨p,s.warmArtifact,s.coldArtifact,s.warmEvidence,s.coldEvidence⟩

def reportPossibleCheck (md : QModel n m) (a : Action) (o : Bool) : Bool :=
  match a with
  | .inspectWarm => if o then decide (0 < (probBand md .warm).upper)
      else decide ((probBand md .warm).lower < 1)
  | .generateCold => if o then decide (0 < (probBand md .cold).upper)
      else decide ((probBand md .cold).lower < 1)
  | _ => decide (o = false)

@[simp] theorem reportPossibleCheck_eq_true_iff (md : QModel n m) (a : Action) (o : Bool) :
    reportPossibleCheck md a o = true ↔ reportPossible md a o := by
  cases a <;> cases o <;> simp [reportPossibleCheck,reportPossible]

def supportedCheck (md : QModel n m) (s : State md) (a : Action) (o : Bool) : Bool :=
  decide (a ∈ LazyStaged.actions (nominal md) s) && reportPossibleCheck md a o

@[simp] theorem supportedCheck_eq_true_iff (md : QModel n m) (s : State md)
    (a : Action) (o : Bool) : supportedCheck md s a o = true ↔ Supported md s a o := by
  simp [supportedCheck,Supported]

def installExec (s : RuntimeState md) (a : Action) (r : Outcome md) (p : State md) :
    RuntimeState md :=
  match a,r with
  | .inspectWarm,.warmSuccess art => ⟨p,some art,s.coldArtifact,some art.refined,s.coldEvidence⟩
  | .inspectWarm,.rejected => ⟨p,none,s.coldArtifact,none,s.coldEvidence⟩
  | .generateCold,.coldSuccess art => ⟨p,s.warmArtifact,some art,s.warmEvidence,some art.refined⟩
  | .generateCold,.rejected => ⟨p,s.warmArtifact,none,s.warmEvidence,none⟩
  | _,_ => ⟨p,s.warmArtifact,s.coldArtifact,s.warmEvidence,s.coldEvidence⟩

@[simp] theorem installExec_eq_install (s : RuntimeState md) (a : Action)
    (r : Outcome md) (p : State md) : installExec s a r p = install s a r p := by
  cases a <;> cases r <;> rfl

/-- Finite executable counterpart of interval-aware confirmation. -/
def confirmExec (md : QModel n m) (s : RuntimeState md) (a : Action) (r : Outcome md) :
    Option (RuntimeState md) :=
  match reportOf a r with
  | none => none
  | some o => if supportedCheck md s.plan a o then
      some (installExec s a r (LazyStaged.step (nominal md) s.plan a o)) else none

noncomputable def confirm (md : QModel n m) (s : RuntimeState md) (a : Action) (r : Outcome md) :
    Option (RuntimeState md) := by
  classical
  exact match reportOf a r with
  | none => none
  | some o => if Supported md s.plan a o then
      some (install s a r (LazyStaged.step (nominal md) s.plan a o)) else none

theorem confirmExec_eq_confirm (md : QModel n m) (s : RuntimeState md)
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

@[simp] theorem fault_rejected (md : QModel n m) (s : RuntimeState md) (a : Action) :
    confirm md s a .fault = none := by cases a <;> rfl

theorem confirm_exact (md : QModel n m) (s t : RuntimeState md) (a : Action)
    (r : Outcome md) (h : confirm md s a r = some t) :
    ∃ o, reportOf a r = some o ∧ Supported md s.plan a o ∧
      t = install s a r (LazyStaged.step (nominal md) s.plan a o) := by
  cases hro : reportOf a r with
  | none => simp [confirm,hro] at h
  | some o =>
      by_cases hs : Supported md s.plan a o
      · have ht : install s a r (LazyStaged.step (nominal md) s.plan a o) = t := by
          simpa [confirm,hro,hs] using h
        exact ⟨o,rfl,hs,ht.symm⟩
      · simp [confirm,hro,hs] at h

theorem confirm_plan (md : QModel n m) (s t : RuntimeState md) (a : Action)
    (r : Outcome md) (h : confirm md s a r = some t) :
    ∃ o, Supported md s.plan a o ∧ t.plan = LazyStaged.step (nominal md) s.plan a o := by
  obtain ⟨o,_,hs,rfl⟩ := confirm_exact md s t a r h
  refine ⟨o,hs,?_⟩
  cases a <;> cases r <;> rfl

theorem confirm_budgetSafe (md : QModel n m) (credit : Nat) (s t : RuntimeState md)
    (a : Action) (r : Outcome md) (hs : LazyStaged.BudgetSafe credit s.plan)
    (h : confirm md s a r = some t) : LazyStaged.BudgetSafe credit t.plan := by
  obtain ⟨o,ha,he⟩ := confirm_plan md s t a r h
  rw [he]
  exact LazyStaged.step_budgetSafe (nominal md) s.plan credit hs a ha.1 o

theorem confirm_coherent (md : QModel n m) (s t : RuntimeState md)
    (a : Action) (r : Outcome md) (hs : Coherent s)
    (h : confirm md s a r = some t) : Coherent t := by
  obtain ⟨o,hr,hp,rfl⟩ := confirm_exact md s t a r h
  cases a with
  | stop =>
      cases r <;> simp [reportOf] at hr
      simpa [install,LazyStaged.step,LazyStaged.terminal,Coherent] using hs
  | inspectWarm =>
      cases r with
      | noExternal => simp [reportOf] at hr
      | rejected =>
          simp [reportOf] at hr; subst o
          refine ⟨by simp [install,LazyStaged.step,LazyStaged.spend], ?_⟩
          simpa [install,LazyStaged.step,LazyStaged.spend] using hs.2
      | warmSuccess art =>
          simp [reportOf] at hr; subst o
          refine ⟨by simp [install,LazyStaged.step,LazyStaged.spend], ?_⟩
          simpa [install,LazyStaged.step,LazyStaged.spend] using hs.2
      | coldSuccess art => simp [reportOf] at hr
      | fault => simp [reportOf] at hr
  | generateCold =>
      cases r with
      | noExternal => simp [reportOf] at hr
      | rejected =>
          simp [reportOf] at hr; subst o
          refine ⟨?_, by simp [install,LazyStaged.step,LazyStaged.spend]⟩
          simpa [install,LazyStaged.step,LazyStaged.spend] using hs.1
      | warmSuccess art => simp [reportOf] at hr
      | coldSuccess art =>
          simp [reportOf] at hr; subst o
          refine ⟨?_, by simp [install,LazyStaged.step,LazyStaged.spend]⟩
          simpa [install,LazyStaged.step,LazyStaged.spend] using hs.1
      | fault => simp [reportOf] at hr
  | deployWarm =>
      cases r <;> simp [reportOf] at hr
      simpa [install,LazyStaged.step,LazyStaged.terminal,Coherent] using hs
  | deployCold =>
      cases r <;> simp [reportOf] at hr
      simpa [install,LazyStaged.step,LazyStaged.terminal,Coherent] using hs

theorem confirm_safe (md : QModel n m) (credit : Nat) (s t : RuntimeState md)
    (a : Action) (r : Outcome md) (hs : Safe credit s)
    (h : confirm md s a r = some t) : Safe credit t :=
  ⟨confirm_budgetSafe md credit s t a r hs.1 h,
    confirm_coherent md s t a r hs.2 h⟩

theorem warm_success_stores_refinement (md : QModel n m) (s t : RuntimeState md)
    (a : BoundedArtifact md .warm)
    (h : confirm md s .inspectWarm (.warmSuccess a) = some t) :
    t.plan.warmStatus = .ready ∧ t.warmArtifact = some a ∧ t.warmEvidence = some a.refined := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .inspectWarm (.warmSuccess a) h
  simp [reportOf] at hr; subst o
  simp [install,LazyStaged.step,LazyStaged.spend]

theorem cold_success_stores_refinement (md : QModel n m) (s t : RuntimeState md)
    (a : BoundedArtifact md .cold)
    (h : confirm md s .generateCold (.coldSuccess a) = some t) :
    t.plan.coldStatus = .ready ∧ t.coldArtifact = some a ∧ t.coldEvidence = some a.refined := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .generateCold (.coldSuccess a) h
  simp [reportOf] at hr; subst o
  simp [install,LazyStaged.step,LazyStaged.spend]

theorem warm_success_preserves_cold (md : QModel n m) (s t : RuntimeState md)
    (a : BoundedArtifact md .warm)
    (h : confirm md s .inspectWarm (.warmSuccess a) = some t) :
    t.coldArtifact = s.coldArtifact ∧ t.coldEvidence = s.coldEvidence := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .inspectWarm (.warmSuccess a) h
  simp [reportOf] at hr; subst o
  exact ⟨rfl,rfl⟩

theorem cold_success_preserves_warm (md : QModel n m) (s t : RuntimeState md)
    (a : BoundedArtifact md .cold)
    (h : confirm md s .generateCold (.coldSuccess a) = some t) :
    t.warmArtifact = s.warmArtifact ∧ t.warmEvidence = s.warmEvidence := by
  obtain ⟨o,hr,_,rfl⟩ := confirm_exact md s t .generateCold (.coldSuccess a) h
  simp [reportOf] at hr; subst o
  exact ⟨rfl,rfl⟩

end Komorebi.AVOC.Affine.RobustQuote
