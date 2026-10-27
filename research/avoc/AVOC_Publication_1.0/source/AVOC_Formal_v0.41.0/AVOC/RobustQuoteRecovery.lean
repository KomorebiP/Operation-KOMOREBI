import AVOC.RobustQuoteRuntime

namespace Komorebi.AVOC.Affine.RobustQuoteRecovery

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Action)
open Komorebi.AVOC.Affine.QuoteAuthority
open Komorebi.AVOC.Affine.RobustQuote

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

variable {n m : Nat}

structure ArtifactView (n m : Nat) where
  identity : Identity n m
  kind : Kind
  source : Signature F n m
  selected : Signature F n m
  setup : Nat
  gross : ℚ
  sourceCost : Nat
  selectedCost : Nat

noncomputable instance artifactViewDecEq : DecidableEq (ArtifactView n m) := Classical.decEq _

def artifactView {md : QModel n m} {k : Kind} (a : BoundedArtifact md k) : ArtifactView n m :=
  ⟨a.identity,a.deployment.kind,coefficients a.deployment.source,
    coefficients a.deployment.selected,a.deployment.setup,a.gross,
    executionCost a.deployment.source,executionCost a.deployment.selected⟩

structure EvidenceView (n m : Nat) where
  warm : RawQuote n m
  cold : RawQuote n m

noncomputable instance evidenceViewDecEq : DecidableEq (EvidenceView n m) := Classical.decEq _

def evidence (md : QModel n m) : EvidenceView n m :=
  ⟨rawQuote md .warm,rawQuote md .cold⟩

structure StoreView (md : QModel n m) where
  plan : State md
  warm : Option (ArtifactView n m)
  cold : Option (ArtifactView n m)
  warmRefinement : Option (Nat × ℚ)
  coldRefinement : Option (Nat × ℚ)

noncomputable instance storeViewDecEq (md : QModel n m) : DecidableEq (StoreView md) := Classical.decEq _

def view (s : RobustQuote.RuntimeState md) : StoreView md :=
  ⟨s.plan,s.warmArtifact.map artifactView,s.coldArtifact.map artifactView,
    s.warmEvidence.map (fun q => (q.setup,q.gross)),
    s.coldEvidence.map (fun q => (q.setup,q.gross))⟩

structure Intent (md : QModel n m) where
  sequence : Nat
  before : StoreView md
  action : Action
  quoteEvidence : EvidenceView n m

noncomputable instance intentDecEq (md : QModel n m) : DecidableEq (Intent md) := Classical.decEq _

structure Commit (md : QModel n m) where
  intent : Intent md
  outcome : RobustQuote.OutcomeTag
  after : StoreView md

noncomputable instance commitDecEq (md : QModel n m) : DecidableEq (Commit md) := Classical.decEq _

structure Checkpoint (md : QModel n m) where
  next : Nat
  state : RobustQuote.RuntimeState md
  last : Option (Commit md)

noncomputable def initial (md : QModel n m) (credit : Nat) : Checkpoint md :=
  ⟨0,RobustQuote.initial md credit,none⟩

def Safe (credit : Nat) (c : Checkpoint md) : Prop := RobustQuote.Safe credit c.state

@[simp] theorem initial_safe (md : QModel n m) (credit : Nat) : Safe credit (initial md credit) :=
  RobustQuote.initial_safe md credit

/-- Quote evidence is bound into the operation identity selected by robust planning. -/
noncomputable def prepare (md : QModel n m) (h : Nat) (c : Checkpoint md) : Intent md :=
  ⟨c.next,view c.state,robustChoice md h c.state.plan,evidence md⟩

@[simp] theorem prepared_action_allowed (md : QModel n m) (h : Nat) (c : Checkpoint md) :
    (prepare md h c).action ∈ LazyStaged.actions (nominal md) c.state.plan :=
  robustChoice_allowed md h c.state.plan

noncomputable def acknowledge (md : QModel n m) (c : Checkpoint md)
    (r : Commit md) (out : RobustQuote.Outcome md) (actual : StoreView md)
    (currentEvidence : EvidenceView n m) : Except String (Checkpoint md) := by
  classical
  exact
    if r.intent.quoteEvidence ≠ currentEvidence then .error "quote evidence changed after planning"
    else if r.after ≠ actual then .error "commit post-state mismatch"
    else if c.last = some r then
      if c.next = r.intent.sequence + 1 ∧ view c.state = actual then .ok c
      else .error "duplicate commit does not match checkpoint"
    else if r.intent.sequence ≠ c.next then .error "commit sequence mismatch"
    else if r.intent.before ≠ view c.state then .error "commit pre-state mismatch"
    else if out.tag ≠ r.outcome then .error "commit outcome mismatch"
    else match RobustQuote.confirm md c.state r.intent.action out with
      | none => .error "checked outcome does not realize selected action"
      | some t =>
          if view t = r.after then .ok ⟨c.next+1,t,some r⟩
          else .error "checked successor differs from durable commit"

inductive DurableOutcome (md : QModel n m) where
  | unfinished (intent : Intent md)
  | committed (commit : Commit md) (checked : RobustQuote.Outcome md)

noncomputable def recover (md : QModel n m) (c : Checkpoint md)
    (r : DurableOutcome md) (actual : StoreView md) (currentEvidence : EvidenceView n m) :
    Except String (Checkpoint md) :=
  match r with
  | .unfinished _ => .error "no durable result: do not infer a report or retry"
  | .committed k checked => acknowledge md c k checked actual currentEvidence

@[simp] theorem unfinished_rejected (md : QModel n m) (c : Checkpoint md)
    (i : Intent md) (actual : StoreView md) (ev : EvidenceView n m) :
    recover md c (.unfinished i) actual ev =
      .error "no durable result: do not infer a report or retry" := rfl

@[simp] theorem quote_mutation_rejected (md : QModel n m) (c : Checkpoint md)
    (r : Commit md) (out : RobustQuote.Outcome md) (actual : StoreView md) (ev : EvidenceView n m)
    (h : r.intent.quoteEvidence ≠ ev) :
    acknowledge md c r out actual ev = .error "quote evidence changed after planning" := by
  simp [acknowledge,h]

theorem acknowledge_fresh_contract (md : QModel n m) (c d : Checkpoint md)
    (r : Commit md) (out : RobustQuote.Outcome md) (actual : StoreView md)
    (ev : EvidenceView n m) (hfresh : c.last ≠ some r)
    (h : acknowledge md c r out actual ev = .ok d) :
    r.intent.quoteEvidence = ev ∧ r.after = actual ∧
      r.intent.sequence = c.next ∧ r.intent.before = view c.state ∧
      out.tag = r.outcome ∧
      ∃ t, RobustQuote.confirm md c.state r.intent.action out = some t ∧
        view t = r.after ∧ d = ⟨c.next+1,t,some r⟩ := by
  classical
  by_cases he : r.intent.quoteEvidence = ev
  · by_cases ha : r.after = actual
    · by_cases hn : r.intent.sequence = c.next
      · by_cases hb : r.intent.before = view c.state
        · by_cases ho : out.tag = r.outcome
          · cases hc : RobustQuote.confirm md c.state r.intent.action out with
            | none => simp [acknowledge,he,ha,hfresh,hn,hb,ho,hc] at h
            | some t =>
                have hactual : view t = actual := by
                  by_contra hna
                  simp [acknowledge,he,ha,hfresh,hn,hb,ho,hc,hna] at h
                have hv : view t = r.after := hactual.trans ha.symm
                have hd : (⟨c.next+1,t,some r⟩ : Checkpoint md) = d := by
                  simpa [acknowledge,he,ha,hfresh,hn,hb,ho,hc,hactual] using h
                exact ⟨he,ha,hn,hb,ho,t,rfl,hv,hd.symm⟩
          · simp [acknowledge,he,ha,hfresh,hn,hb,ho] at h
        · simp [acknowledge,he,ha,hfresh,hn,hb] at h
      · simp [acknowledge,he,ha,hfresh,hn] at h
    · simp [acknowledge,he,ha] at h
  · simp [acknowledge,he] at h

theorem acknowledge_duplicate (md : QModel n m) (c : Checkpoint md)
    (r : Commit md) (out : RobustQuote.Outcome md) (actual : StoreView md) (ev : EvidenceView n m)
    (he : r.intent.quoteEvidence = ev) (ha : r.after = actual)
    (hl : c.last = some r) (hn : c.next = r.intent.sequence+1)
    (hv : view c.state = actual) : acknowledge md c r out actual ev = .ok c := by
  classical
  simp [acknowledge,he,ha,hl,hn,hv]

theorem acknowledge_safe (md : QModel n m) (credit : Nat) (c d : Checkpoint md)
    (r : Commit md) (out : RobustQuote.Outcome md) (actual : StoreView md) (ev : EvidenceView n m)
    (hs : Safe credit c) (h : acknowledge md c r out actual ev = .ok d) : Safe credit d := by
  classical
  by_cases hl : c.last = some r
  · unfold acknowledge at h
    by_cases he : r.intent.quoteEvidence = ev
    · by_cases ha : r.after = actual
      · simp only [he,ha,hl,ne_eq,not_true_eq_false,↓reduceIte] at h
        by_cases hd : c.next = r.intent.sequence+1 ∧ view c.state = actual
        · have hc : c = d := by simpa [hd] using h
          exact hc ▸ hs
        · simp [hd] at h
      · simp [he,ha] at h
    · simp [he] at h
  · obtain ⟨_,_,_,_,_,t,ht,_,hd⟩ :=
      acknowledge_fresh_contract md c d r out actual ev hl h
    subst d
    exact RobustQuote.confirm_safe md credit c.state t r.intent.action out hs ht

theorem acknowledge_idempotent (md : QModel n m) (c d : Checkpoint md)
    (r : Commit md) (out : RobustQuote.Outcome md) (actual : StoreView md) (ev : EvidenceView n m)
    (h : acknowledge md c r out actual ev = .ok d) :
    acknowledge md d r out actual ev = .ok d := by
  classical
  by_cases hl : c.last = some r
  · unfold acknowledge at h
    by_cases he : r.intent.quoteEvidence = ev
    · by_cases ha : r.after = actual
      · simp only [he,ha,hl,ne_eq,not_true_eq_false,↓reduceIte] at h
        by_cases hd : c.next = r.intent.sequence+1 ∧ view c.state = actual
        · have hc : c = d := by simpa [hd] using h
          subst d
          exact acknowledge_duplicate md c r out actual ev he ha hl hd.1 hd.2
        · simp [hd] at h
      · simp [he,ha] at h
    · simp [he] at h
  · obtain ⟨he,ha,hn,_,_,t,ht,hv,hd⟩ :=
      acknowledge_fresh_contract md c d r out actual ev hl h
    subst d
    exact acknowledge_duplicate md _ r out actual ev he ha rfl (by simp [hn]) (hv.trans ha)

theorem recover_safe (md : QModel n m) (credit : Nat) (c d : Checkpoint md)
    (r : DurableOutcome md) (actual : StoreView md) (ev : EvidenceView n m)
    (hs : Safe credit c) (h : recover md c r actual ev = .ok d) : Safe credit d := by
  cases r with
  | unfinished i => simp [recover] at h
  | committed k checked => exact acknowledge_safe md credit c d k checked actual ev hs h

def intentFor (md : QModel n m) (c : Checkpoint md) (a : Action) : Intent md :=
  ⟨c.next,view c.state,a,evidence md⟩

def commitFor (md : QModel n m) (c : Checkpoint md) (a : Action)
    (out : RobustQuote.Outcome md) (t : RobustQuote.RuntimeState md) : Commit md :=
  ⟨intentFor md c a,out.tag,view t⟩

theorem acknowledge_checked_transition (md : QModel n m) (c : Checkpoint md)
    (a : Action) (out : RobustQuote.Outcome md) (t : RobustQuote.RuntimeState md)
    (hc : RobustQuote.confirm md c.state a out = some t)
    (hl : c.last ≠ some (commitFor md c a out t)) :
    acknowledge md c (commitFor md c a out t) out (view t) (evidence md) =
      .ok ⟨c.next+1,t,some (commitFor md c a out t)⟩ := by
  classical
  unfold commitFor intentFor at hl ⊢
  simp [acknowledge,hc,hl]

end Komorebi.AVOC.Affine.RobustQuoteRecovery
