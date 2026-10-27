import AVOC.ArtifactWorkflowGuarantee
import AVOC.BindingCodec

namespace Komorebi.AVOC.ArtifactWorkflow

open Certificate Binding

/-- The proof AST is obtained by parsing this exact retained source string. -/
def SourceParsed (a : Artifact) : Prop :=
  artifactFromSource a.identity a.sourceBytes = .ok a

theorem successful_parse_is_sourceParsed (i : Identity) (bytes : String) (a : Artifact)
    (h : artifactFromSource i bytes = .ok a) : SourceParsed a := by
  obtain ⟨hi,hb,_⟩ := source_artifact_consistent i bytes a h
  unfold SourceParsed
  rw [hi,hb]
  exact h

def PendingParsed {Ω P : Type*} [Fintype Ω] (s : State Ω P) : Prop :=
  ∀ t, s.slot.pending = some t → SourceParsed t.artifact

variable {Ω P C O : Type*} [Fintype Ω] [Fintype O] [PartialOrder P]

/-- Catalogue construction is an explicit boundary. Each candidate must have
been produced by the inherited source parser; an unrelated AST is insufficient. -/
def CatalogueParsed (p : Protocol Ω P C O) : Prop :=
  ∀ x c, SourceParsed (p.candidate x c)

def SourceSafe (p : Protocol Ω P C O) (B : Nat) (s : State Ω P) : Prop :=
  BudgetSafe p B s ∧ PendingParsed s

variable [DecidableEq P]

omit [DecidableEq P] in
theorem register_pending_parsed (p : Protocol Ω P C O) (hc : CatalogueParsed p)
    (s : State Ω P) (x : P) (c : C) : PendingParsed (registerStep p s x c) := by
  intro t ht
  have he : (⟨s.slot.nextGeneration, p.candidate x c⟩ : Ticket) = t :=
    Option.some.inj ht
  subst t
  exact hc x c

theorem step_pending_parsed (p : Protocol Ω P C O) (hc : CatalogueParsed p)
    (s : State Ω P) (hp : PendingParsed s) (a : Action P C)
    (ha : Allowed p s a) (d : Bool) : PendingParsed (step p s a d) := by
  cases a with
  | register x c => exact register_pending_parsed p hc s x c
  | verify => exact hp
  | stop => exact hp
  | admit =>
      have hpre : Precondition p s .admit :=
        (ha.resolve_left (by intro he; cases he)).2.2
      intro t ht
      change (admitStep p s).slot.pending = some t at ht
      rw [(admit_consumes p s hpre).1] at ht
      cases ht

theorem step_source_safe (p : Protocol Ω P C O) (hc : CatalogueParsed p)
    (B : Nat) (s : State Ω P) (hs : SourceSafe p B s)
    (a : Action P C) (ha : Allowed p s a) (d : Bool) :
    SourceSafe p B (step p s a d) :=
  ⟨step_budgetSafe p B s hs.1 a ha d, step_pending_parsed p hc s hs.2 a ha d⟩

omit [DecidableEq P] in
theorem admission_retains_parsed_source (p : Protocol Ω P C O) (s : State Ω P)
    (hp : PendingParsed s) (ha : Precondition p s .admit) :
    ∃ x t r j,
      s.owner = some x ∧ s.slot.pending = some t ∧ s.checked = some r ∧
      r.subject = t ∧ t.artifact.identity = p.spec x ∧ Valid t.artifact ∧
      Lean.Json.parse t.artifact.sourceBytes = .ok j ∧
      parseDerivation 128 j = .ok t.artifact.proof := by
  obtain ⟨x,t,r,hx,ht,hr,hs,hi,hv⟩ := admission_has_exact_ticket p s ha
  obtain ⟨j,hj,hp⟩ :=
    (source_artifact_consistent t.artifact.identity t.artifact.sourceBytes
      t.artifact (hp t ht)).2.2
  exact ⟨x,t,r,j,hx,ht,hr,hs,hi,hv,hj,hp⟩

variable [Fintype P] [Fintype C] [DecidableEq C]

theorem controller_source_preserves (p : Protocol Ω P C O) (hc : CatalogueParsed p)
    (B : Nat) : Guarded.Preserves (controller p) (SourceSafe p B) := by
  intro s hs a ha d
  exact step_source_safe p hc B s hs a ((mem_actions p s a).1 ha) d

/-- Full-plan optimality for the actual filtered-observation model, together
with source parsing, certificate, dependency and budget invariants. -/
theorem source_bound_safe_optimal_plan (p : Protocol Ω P C O) (hc : CatalogueParsed p)
    (B n : Nat) (s : State Ω P) (hs : SourceSafe p B s) :
    ∃ plan : Guarded.Plan (Action P C) Bool n,
      Guarded.Legal (controller p) s plan ∧
      Guarded.TreeSafe (controller p) (SourceSafe p B) s plan ∧
      Guarded.planValue (controller p) s plan = Guarded.value (controller p) n s ∧
      ∀ other : Guarded.Plan (Action P C) Bool n,
        Guarded.Legal (controller p) s other →
        Guarded.planValue (controller p) s other ≤ Guarded.planValue (controller p) s plan := by
  exact Guarded.safe_optimal_plan_exists (controller p) (SourceSafe p B)
    (controller_source_preserves p hc B) n s hs

theorem source_bound_approximate_policy_safe (p : Protocol Ω P C O)
    (hc : CatalogueParsed p) (choose : Nat → State Ω P → Action P C)
    (ha : ∀ n s, Allowed p s (choose n s))
    (B n : Nat) (s : State Ω P) (hs : SourceSafe p B s) :
    Guarded.TreeSafe (controller p) (SourceSafe p B) s
      (Guarded.policyPlan (controller p) choose n s) := by
  exact Guarded.admissible_approximate_policy_safe (controller p) (SourceSafe p B)
    (controller_source_preserves p hc B) choose
    (fun n s => (mem_actions p s _).2 (ha n s)) n s hs

end Komorebi.AVOC.ArtifactWorkflow
