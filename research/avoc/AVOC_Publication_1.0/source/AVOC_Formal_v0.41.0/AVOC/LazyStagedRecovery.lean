import AVOC.LazyStagedControl

namespace Komorebi.AVOC.Affine.LazyRecovery

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Action)
open Komorebi.AVOC.Affine.LazyStaged

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

variable {n m : Nat}

/-- Data retained across the trust boundary.  Proof fields are reconstructed by
rechecking the artifact; the fingerprint still binds its exact affine semantics. -/
structure ArtifactView (n m : Nat) where
  kind : Kind
  source : Signature F n m
  selected : Signature F n m
  setup : Nat
  sourceCost : Nat
  selectedCost : Nat


noncomputable instance artifactViewDecEq : DecidableEq (ArtifactView n m) := Classical.decEq _

def artifactView {md : Model n m} {k : Kind} (a : CheckedArtifact md k) :
    ArtifactView n m :=
  ⟨a.deployment.kind, coefficients a.deployment.source,
    coefficients a.deployment.selected, a.deployment.setup,
    executionCost a.deployment.source, executionCost a.deployment.selected⟩

structure StoreView (md : Model n m) where
  plan : PlanState md
  warm : Option (ArtifactView n m)
  cold : Option (ArtifactView n m)


noncomputable instance storeViewDecEq (md : Model n m) : DecidableEq (StoreView md) := Classical.decEq _

def view {md : Model n m} (s : RuntimeState md) : StoreView md :=
  ⟨s.plan, s.warmArtifact.map artifactView, s.coldArtifact.map artifactView⟩

structure Intent (md : Model n m) where
  sequence : Nat
  before : StoreView md
  action : Action


noncomputable instance intentDecEq (md : Model n m) : DecidableEq (Intent md) := Classical.decEq _

structure Commit (md : Model n m) where
  intent : Intent md
  outcome : OutcomeTag
  after : StoreView md


noncomputable instance commitDecEq (md : Model n m) : DecidableEq (Commit md) := Classical.decEq _

structure Checkpoint (md : Model n m) where
  next : Nat
  state : RuntimeState md
  last : Option (Commit md)

def initial (md : Model n m) (credit : Nat) : Checkpoint md :=
  ⟨0, LazyStaged.initial md credit, none⟩

def Safe (credit : Nat) (c : Checkpoint md) : Prop := LazyStaged.Safe credit c.state

@[simp] theorem initial_safe (md : Model n m) (credit : Nat) :
    Safe credit (initial md credit) := LazyStaged.initial_safe md credit

/-- The full Bellman recommendation is converted into a sequence-bound intent.
No external checker or generator is called by this function. -/
def prepare (md : Model n m) (h : Nat) (c : Checkpoint md) : Intent md :=
  ⟨c.next, view c.state, recommend md h c.state⟩

theorem prepared_action_allowed (md : Model n m) (h : Nat) (c : Checkpoint md) :
    (prepare md h c).action ∈ actions md c.state.plan := recommend_allowed md h c.state

theorem prepared_action_optimal (md : Model n m) (h : Nat) (c : Checkpoint md) :
    ∀ b ∈ actions md c.state.plan,
      Guarded.qValue (system md) h c.state.plan b ≤
        Guarded.qValue (system md) h c.state.plan (prepare md h c).action :=
  recommend_optimal md h c.state

inductive ExternalOp where
  | warmCheck | coldGenerate
  deriving Repr, DecidableEq

def requiredExternal : Action → Option ExternalOp
  | .inspectWarm => some .warmCheck
  | .generateCold => some .coldGenerate
  | _ => none

@[simp] theorem external_warm : requiredExternal .inspectWarm = some .warmCheck := rfl
@[simp] theorem external_cold : requiredExternal .generateCold = some .coldGenerate := rfl
@[simp] theorem no_external_stop : requiredExternal .stop = none := rfl
@[simp] theorem no_external_deployWarm : requiredExternal .deployWarm = none := rfl
@[simp] theorem no_external_deployCold : requiredExternal .deployCold = none := rfl

/-- Reconciliation validates the exact selected transition.  It does not run an
external operation.  A checked artifact is supplied again so its proof can be
reconstructed after restart. -/
noncomputable def acknowledge (md : Model n m) (c : Checkpoint md)
    (r : Commit md) (out : Outcome md) (actual : StoreView md) :
    Except String (Checkpoint md) := by
  classical
  exact
    if r.after ≠ actual then .error "commit post-state mismatch"
    else if c.last = some r then
      if c.next = r.intent.sequence + 1 ∧ view c.state = actual then .ok c
      else .error "duplicate commit does not match checkpoint"
    else if r.intent.sequence ≠ c.next then .error "commit sequence mismatch"
    else if r.intent.before ≠ view c.state then .error "commit pre-state mismatch"
    else if out.tag ≠ r.outcome then .error "commit outcome mismatch"
    else match confirm md c.state r.intent.action out with
      | none => .error "checked outcome does not realize selected action"
      | some t =>
          if view t = r.after then .ok ⟨c.next+1,t,some r⟩
          else .error "checked successor differs from durable commit"

/-- No durable result means no report.  Recovery deliberately refuses to guess
whether an external operation succeeded. -/
inductive DurableOutcome (md : Model n m) where
  | unfinished (intent : Intent md)
  | committed (commit : Commit md) (checked : Outcome md)

noncomputable def recover (md : Model n m) (c : Checkpoint md) (r : DurableOutcome md)
    (actual : StoreView md) : Except String (Checkpoint md) :=
  match r with
  | .unfinished _ => .error "no durable result: do not infer a report or retry"
  | .committed k checked => acknowledge md c k checked actual

@[simp] theorem unfinished_rejected (md : Model n m) (c : Checkpoint md)
    (i : Intent md) (actual : StoreView md) :
    recover md c (.unfinished i) actual =
      .error "no durable result: do not infer a report or retry" := rfl

/-- Contract for a fresh successful acknowledgement.  Exact duplicates are the
other permitted branch and return the entire checkpoint unchanged. -/
theorem acknowledge_fresh_contract (md : Model n m) (c d : Checkpoint md)
    (r : Commit md) (out : Outcome md) (actual : StoreView md)
    (hfresh : c.last ≠ some r)
    (h : acknowledge md c r out actual = .ok d) :
    r.after = actual ∧ r.intent.sequence = c.next ∧
      r.intent.before = view c.state ∧ out.tag = r.outcome ∧
      ∃ t, confirm md c.state r.intent.action out = some t ∧
        view t = r.after ∧ d = ⟨c.next+1,t,some r⟩ := by
  classical
  by_cases ha : r.after = actual
  · by_cases hn : r.intent.sequence = c.next
    · by_cases hb : r.intent.before = view c.state
      · by_cases ho : out.tag = r.outcome
        · cases hc : confirm md c.state r.intent.action out with
          | none => simp [acknowledge,ha,hfresh,hn,hb,ho,hc] at h
          | some t =>
              have hactual : view t = actual := by
                by_contra hna
                simp [acknowledge,ha,hfresh,hn,hb,ho,hc,hna] at h
              have hv : view t = r.after := hactual.trans ha.symm
              have hd : (⟨c.next+1,t,some r⟩ : Checkpoint md) = d := by
                simpa [acknowledge,ha,hfresh,hn,hb,ho,hc,hactual] using h
              exact ⟨ha,hn,hb,ho,t,rfl,hv,hd.symm⟩
        · simp [acknowledge,ha,hfresh,hn,hb,ho] at h
      · simp [acknowledge,ha,hfresh,hn,hb] at h
    · simp [acknowledge,ha,hfresh,hn] at h
  · simp [acknowledge,ha] at h

theorem acknowledge_duplicate (md : Model n m) (c : Checkpoint md)
    (r : Commit md) (out : Outcome md) (actual : StoreView md)
    (ha : r.after = actual) (hl : c.last = some r)
    (hn : c.next = r.intent.sequence+1) (hv : view c.state = actual) :
    acknowledge md c r out actual = .ok c := by
  classical
  simp [acknowledge,ha,hl,hn,hv]

theorem acknowledge_safe (md : Model n m) (credit : Nat) (c d : Checkpoint md)
    (r : Commit md) (out : Outcome md) (actual : StoreView md)
    (hs : Safe credit c) (h : acknowledge md c r out actual = .ok d) : Safe credit d := by
  classical
  by_cases hl : c.last = some r
  · unfold acknowledge at h
    by_cases ha : r.after = actual
    · simp only [ne_eq, ha, not_true_eq_false, ↓reduceIte, hl, ↓reduceIte] at h
      by_cases hd : c.next = r.intent.sequence+1 ∧ view c.state = actual
      · have he : c = d := by simpa [hd] using h
        exact he ▸ hs
      · simp [hd] at h
    · simp [ha] at h
  · obtain ⟨_,_,_,_,t,ht,_,hd⟩ := acknowledge_fresh_contract md c d r out actual hl h
    subst d
    exact confirm_safe md credit c.state t r.intent.action out hs ht

theorem acknowledge_idempotent (md : Model n m) (c d : Checkpoint md)
    (r : Commit md) (out : Outcome md) (actual : StoreView md)
    (h : acknowledge md c r out actual = .ok d) :
    acknowledge md d r out actual = .ok d := by
  classical
  by_cases hl : c.last = some r
  · unfold acknowledge at h
    by_cases ha : r.after = actual
    · simp only [ne_eq, ha, not_true_eq_false, ↓reduceIte, hl, ↓reduceIte] at h
      by_cases hd : c.next = r.intent.sequence+1 ∧ view c.state = actual
      · have he : c = d := by simpa [hd] using h
        subst d
        exact acknowledge_duplicate md c r out actual ha hl hd.1 hd.2
      · simp [hd] at h
    · simp [ha] at h
  · obtain ⟨ha,hn,_,_,t,ht,hv,hd⟩ :=
      acknowledge_fresh_contract md c d r out actual hl h
    subst d
    have hlast : (⟨c.next+1,t,some r⟩ : Checkpoint md).last = some r := rfl
    have hnext : (⟨c.next+1,t,some r⟩ : Checkpoint md).next = r.intent.sequence+1 := by
      simp [hn]
    exact acknowledge_duplicate md _ r out actual ha hlast hnext (hv.trans ha)

theorem recover_safe (md : Model n m) (credit : Nat) (c d : Checkpoint md)
    (r : DurableOutcome md) (actual : StoreView md)
    (hs : Safe credit c) (h : recover md c r actual = .ok d) : Safe credit d := by
  cases r with
  | unfinished i => simp [recover] at h
  | committed k checked => exact acknowledge_safe md credit c d k checked actual hs h

end Komorebi.AVOC.Affine.LazyRecovery

namespace Komorebi.AVOC.Affine.LazyRecovery

open Komorebi.AVOC.Affine.Staged (Action)
open Komorebi.AVOC.Affine.LazyStaged

variable {n m : Nat}

/-- Canonical durable records for a selected transition. -/
def intentFor (c : Checkpoint md) (a : Action) : Intent md :=
  ⟨c.next,view c.state,a⟩


def commitFor (c : Checkpoint md) (a : Action) (out : Outcome md)
    (t : RuntimeState md) : Commit md :=
  ⟨intentFor c a,out.tag,view t⟩

/-- A freshly checked transition can be acknowledged without rerunning the
external generator. Reconstructing `out` may recheck its retained certificate. -/
theorem acknowledge_checked_transition (md : Model n m) (c : Checkpoint md)
    (a : Action) (out : Outcome md) (t : RuntimeState md)
    (hc : confirm md c.state a out = some t)
    (hl : c.last ≠ some (commitFor c a out t)) :
    acknowledge md c (commitFor c a out t) out (view t) =
      .ok ⟨c.next+1,t,some (commitFor c a out t)⟩ := by
  classical
  have hlast : c.last ≠ some
      ({ intent := { sequence := c.next, before := view c.state, action := a },
         outcome := out.tag, after := view t } : Commit md) := by
    simpa [commitFor,intentFor] using hl
  simp [acknowledge,commitFor,intentFor,hc,hlast]

/-- The canonical record is sequence- and pre-state-bound. -/
@[simp] theorem commitFor_sequence (c : Checkpoint md) (a : Action)
    (out : Outcome md) (t : RuntimeState md) :
    (commitFor c a out t).intent.sequence = c.next := rfl

@[simp] theorem commitFor_before (c : Checkpoint md) (a : Action)
    (out : Outcome md) (t : RuntimeState md) :
    (commitFor c a out t).intent.before = view c.state := rfl

@[simp] theorem commitFor_after (c : Checkpoint md) (a : Action)
    (out : Outcome md) (t : RuntimeState md) :
    (commitFor c a out t).after = view t := rfl

end Komorebi.AVOC.Affine.LazyRecovery
