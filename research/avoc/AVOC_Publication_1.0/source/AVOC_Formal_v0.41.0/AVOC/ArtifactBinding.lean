import AVOC.CertificateLogic

namespace Komorebi.AVOC.Binding

open Certificate

/-- Dependencies bind their declared formula and the exact retained artifact bytes. -/
structure Dependency where
  name : String
  statement : Formula
  artifactBytes : String
  deriving DecidableEq, Repr

/-- Formal meaning and execution identity. Strings denote full byte snapshots in
this model, never an axiom that a finite hash is injective. -/
structure Identity where
  task : String
  statement : Formula
  statementBytes : String
  dependencies : List Dependency
  environment : List (String × String)
  deriving DecidableEq, Repr

structure Artifact where
  identity : Identity
  sourceBytes : String
  proof : Derivation
  deriving DecidableEq, Repr

/-- Generation distinguishes re-registration even of exactly the same payload. -/
structure Ticket where
  generation : Nat
  artifact : Artifact
  deriving DecidableEq, Repr

structure Receipt where
  subject : Ticket
  approved : Bool
  deriving DecidableEq, Repr

def context (i : Identity) : List Formula := i.dependencies.map Dependency.statement

def Valid (a : Artifact) : Prop :=
  ∀ v : Nat → Prop, Satisfies v (context a.identity) → Denote v a.identity.statement

/-- A persisted receipt is not trusted as proof. The data-only proof is rechecked. -/
def validate (current : Identity) (pending : Ticket) (r : Receipt) : Bool :=
  decide (pending.artifact.identity = current) &&
  decide (r.subject = pending) && r.approved &&
  Certificate.check (context current) current.statement pending.artifact.proof

theorem validate_iff (i : Identity) (t : Ticket) (r : Receipt) :
    validate i t r = true ↔
      t.artifact.identity = i ∧ r.subject = t ∧ r.approved = true ∧
      Certificate.check (context i) i.statement t.artifact.proof = true := by
  simp only [validate, Bool.and_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨⟨⟨h₁, h₂⟩, h₃⟩, h₄⟩; exact ⟨h₁, h₂, h₃, h₄⟩
  · rintro ⟨h₁,h₂,h₃,h₄⟩; exact ⟨⟨⟨h₁,h₂⟩,h₃⟩,h₄⟩

theorem validated_identity (i : Identity) (t : Ticket) (r : Receipt)
    (h : validate i t r = true) : t.artifact.identity = i := (validate_iff i t r).1 h |>.1

theorem validated_receipt (i : Identity) (t : Ticket) (r : Receipt)
    (h : validate i t r = true) : r.subject = t := (validate_iff i t r).1 h |>.2.1

theorem validated_proof (i : Identity) (t : Ticket) (r : Receipt)
    (h : validate i t r = true) :
    Certificate.check (context i) i.statement t.artifact.proof = true :=
  (validate_iff i t r).1 h |>.2.2.2

theorem validated_sound (i : Identity) (t : Ticket) (r : Receipt)
    (h : validate i t r = true) (v : Nat → Prop) (hc : Satisfies v (context i)) :
    Denote v i.statement := Certificate.check_sound _ _ _ (validated_proof i t r h) v hc

theorem validated_artifact_valid (i : Identity) (t : Ticket) (r : Receipt)
    (h : validate i t r = true) : Valid t.artifact := by
  intro v hc
  have heq := validated_identity i t r h
  simpa only [heq] using (validated_sound i t r h v (by simpa only [heq] using hc))

theorem stale_identity_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : t.artifact.identity ≠ i) : validate i t r = false := by simp [validate, h]

theorem substituted_ticket_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : r.subject ≠ t) : validate i t r = false := by simp [validate, h]

theorem failed_proof_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : Certificate.check (context i) i.statement t.artifact.proof = false) :
    validate i t r = false := by simp [validate, h]

theorem generation_mismatch_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : r.subject.generation ≠ t.generation) : validate i t r = false :=
  substituted_ticket_rejected i t r (fun he => h (congrArg Ticket.generation he))

theorem proof_bytes_mismatch_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : r.subject.artifact.sourceBytes ≠ t.artifact.sourceBytes) :
    validate i t r = false :=
  substituted_ticket_rejected i t r (fun he => h (congrArg (fun t => t.artifact.sourceBytes) he))

theorem target_mismatch_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : t.artifact.identity.statement ≠ i.statement) : validate i t r = false :=
  stale_identity_rejected i t r (fun he => h (congrArg Identity.statement he))

theorem environment_mismatch_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : t.artifact.identity.environment ≠ i.environment) : validate i t r = false :=
  stale_identity_rejected i t r (fun he => h (congrArg Identity.environment he))

theorem dependency_mismatch_rejected (i : Identity) (t : Ticket) (r : Receipt)
    (h : t.artifact.identity.dependencies ≠ i.dependencies) : validate i t r = false :=
  stale_identity_rejected i t r (fun he => h (congrArg Identity.dependencies he))

structure Slot where
  nextGeneration : Nat
  pending : Option Ticket
  deriving DecidableEq, Repr

def register (s : Slot) (a : Artifact) : Slot :=
  ⟨s.nextGeneration + 1, some ⟨s.nextGeneration, a⟩⟩

def WellFormed (s : Slot) : Prop :=
  ∀ t, s.pending = some t → t.generation < s.nextGeneration

/-- A failed validation leaves the pending candidate untouched; success consumes it. -/
def consume (s : Slot) (i : Identity) (r : Receipt) : Slot × Option Ticket :=
  match s.pending with
  | none => (s, none)
  | some t => if validate i t r then (⟨s.nextGeneration, none⟩, some t) else (s, none)

theorem register_pending (s : Slot) (a : Artifact) :
    (register s a).pending = some ⟨s.nextGeneration, a⟩ := rfl

theorem register_wellFormed (s : Slot) (a : Artifact) : WellFormed (register s a) := by
  intro t ht
  have he : (⟨s.nextGeneration, a⟩ : Ticket) = t := Option.some.inj ht
  subst t
  exact Nat.lt_succ_self _

theorem admission_iff (s : Slot) (i : Identity) (r : Receipt) (t : Ticket) :
    (consume s i r).2 = some t ↔ s.pending = some t ∧ validate i t r = true := by
  cases hp : s.pending with
  | none => simp [consume, hp]
  | some u =>
      by_cases he : u = t
      · subst t
        by_cases hv : validate i u r = true <;> simp [consume, hp, hv]
      · by_cases hv : validate i u r = true <;> simp [consume, hp, he, hv]

theorem admission_consumes (s : Slot) (i : Identity) (r : Receipt) (t : Ticket)
    (h : (consume s i r).2 = some t) : (consume s i r).1.pending = none := by
  obtain ⟨hp, hv⟩ := (admission_iff s i r t).1 h
  simp [consume, hp, hv]

theorem admission_sound (s : Slot) (i : Identity) (r : Receipt) (t : Ticket)
    (h : (consume s i r).2 = some t) : Valid t.artifact :=
  validated_artifact_valid i t r ((admission_iff s i r t).1 h).2

theorem no_pending_no_admission (s : Slot) (i : Identity) (r : Receipt)
    (h : s.pending = none) : (consume s i r).2 = none := by simp [consume, h]

theorem successful_receipt_not_replayable (s : Slot) (i : Identity) (r : Receipt) (t : Ticket)
    (h : (consume s i r).2 = some t) : (consume (consume s i r).1 i r).2 = none :=
  no_pending_no_admission _ i r (admission_consumes s i r t h)

theorem old_pending_rejected_after_register (s : Slot) (a : Artifact) (i : Identity)
    (r : Receipt) (hs : WellFormed s) (hr : s.pending = some r.subject) :
    (consume (register s a) i r).2 = none := by
  have hlt := hs _ hr
  have hne : r.subject.generation ≠ s.nextGeneration := Nat.ne_of_lt hlt
  have hv := generation_mismatch_rejected i ⟨s.nextGeneration, a⟩ r hne
  simp [consume, register, hv]

theorem consume_preserves_generation (s : Slot) (i : Identity) (r : Receipt) :
    (consume s i r).1.nextGeneration = s.nextGeneration := by
  cases hp : s.pending with
  | none => simp [consume, hp]
  | some t => by_cases hv : validate i t r = true <;> simp [consume, hp, hv]

theorem rejected_admission_unchanged (s : Slot) (i : Identity) (r : Receipt)
    (h : (consume s i r).2 = none) : (consume s i r).1 = s := by
  cases hp : s.pending with
  | none => simp [consume, hp]
  | some t =>
      by_cases hv : validate i t r = true
      · simp [consume, hp, hv] at h
      · simp [consume, hp, hv]

theorem consume_preserves_wellFormed (s : Slot) (i : Identity) (r : Receipt)
    (hs : WellFormed s) : WellFormed (consume s i r).1 := by
  cases hp : s.pending with
  | none => simpa [consume, hp] using hs
  | some t =>
      by_cases hv : validate i t r = true
      · intro u hu
        simp [consume, hp, hv] at hu
      · simpa [consume, hp, hv] using hs

end Komorebi.AVOC.Binding
