import AVOC.ArtifactBinding
import AVOC.CertificateCodec

namespace Komorebi.AVOC.Binding
open Lean Certificate

/-- Wire format uses explicit arrays and exact source strings. Its dependency
formulas are provided by the orchestrator after recursively checking their
snapshots. That filesystem connection remains a stated trusted boundary. -/
def parseDependency (j : Json) : Except String Dependency := do
  match (← j.getArr?).toList with
  | [name, statement, bytes] =>
      return ⟨← name.getStr?, ← parseFormula 64 statement, ← bytes.getStr?⟩
  | _ => .error "invalid dependency record"

def parseEnvironmentItem (j : Json) : Except String (String × String) := do
  match (← j.getArr?).toList with
  | [name, bytes] => return (← name.getStr?, ← bytes.getStr?)
  | _ => .error "invalid environment record"

def parseIdentity (j : Json) : Except String Identity := do
  match (← j.getArr?).toList with
  | [task, statement, bytes, .arr deps, .arr env] =>
      return ⟨← task.getStr?, ← parseFormula 64 statement, ← bytes.getStr?,
        ← deps.toList.mapM parseDependency, ← env.toList.mapM parseEnvironmentItem⟩
  | _ => .error "invalid identity record"

/-- The proof object is obtained from the exact source string held in the artifact. -/
def artifactFromSource (i : Identity) (bytes : String) : Except String Artifact :=
  match Json.parse bytes with
  | .error e => .error e
  | .ok j => match parseDerivation 128 j with
      | .error e => .error e
      | .ok p => .ok ⟨i, bytes, p⟩

theorem source_artifact_consistent (i : Identity) (bytes : String) (a : Artifact)
    (h : artifactFromSource i bytes = .ok a) :
    a.identity = i ∧ a.sourceBytes = bytes ∧
      ∃ j, Json.parse bytes = .ok j ∧ parseDerivation 128 j = .ok a.proof := by
  cases hj : Json.parse bytes with
  | error e => simp [artifactFromSource, hj] at h
  | ok j =>
      cases hp : parseDerivation 128 j with
      | error e => simp [artifactFromSource, hj, hp] at h
      | ok p =>
          have he : (⟨i,bytes,p⟩ : Artifact) = a := by simpa [artifactFromSource, hj, hp] using h
          subst a
          exact ⟨rfl,rfl,j,rfl,hp⟩

theorem source_artifact_checked_sound (i : Identity) (bytes : String) (a : Artifact)
    (h : artifactFromSource i bytes = .ok a)
    (hc : Certificate.check (context i) i.statement a.proof = true) :
    a.sourceBytes = bytes ∧ ∀ v : Nat → Prop, Satisfies v (context i) → Denote v i.statement :=
  ⟨(source_artifact_consistent i bytes a h).2.1,
    fun v hv => Certificate.check_sound _ _ _ hc v hv⟩

def parseArtifact (j : Json) : Except String Artifact := do
  match (← j.getArr?).toList with
  | [identity, source] =>
      let i ← parseIdentity identity
      let bytes ← source.getStr?
      artifactFromSource i bytes
  | _ => .error "invalid artifact record"

def parseTicket (j : Json) : Except String Ticket := do
  match (← j.getArr?).toList with
  | [generation, artifact] => return ⟨← generation.getNat?, ← parseArtifact artifact⟩
  | _ => .error "invalid ticket"

def parseSlot (j : Json) : Except String Slot := do
  match (← j.getArr?).toList with
  | [next, .null] => return ⟨← next.getNat?, none⟩
  | [next, ticket] => return ⟨← next.getNat?, some (← parseTicket ticket)⟩
  | _ => .error "invalid slot"

def parseReceipt (j : Json) : Except String Receipt := do
  match (← j.getArr?).toList with
  | [ticket, .bool approved] => return ⟨← parseTicket ticket, approved⟩
  | _ => .error "invalid receipt"

def parseBoundRequest (j : Json) : Except String (Identity × Slot × Receipt) := do
  match (← j.getArr?).toList with
  | [.str "bound", identity, slot, receipt] =>
      return (← parseIdentity identity, ← parseSlot slot, ← parseReceipt receipt)
  | _ => .error "invalid binding request"

def checkBoundJson (j : Json) : Except String Bool :=
  match parseBoundRequest j with
  | .error e => .error e
  | .ok (i,s,r) => .ok ((consume s i r).2.isSome)

/-- The executed binding gate has both an exact pending subject and a sound
proof at every successful parse/check result. -/
theorem accepted_bound_json_has_evidence (j : Json) (h : checkBoundJson j = .ok true) :
    ∃ i s r t, parseBoundRequest j = .ok (i,s,r) ∧
      s.pending = some t ∧ r.subject = t ∧ t.artifact.identity = i ∧ Valid t.artifact := by
  cases hp : parseBoundRequest j with
  | error e => simp [checkBoundJson, hp] at h
  | ok data =>
      rcases data with ⟨i,s,r⟩
      have ha : (consume s i r).2.isSome = true := by simpa [checkBoundJson, hp] using h
      cases he : (consume s i r).2 with
      | none => simp [he] at ha
      | some t =>
          have hh := (admission_iff s i r t).1 he
          exact ⟨i,s,r,t,rfl,hh.1,validated_receipt i t r hh.2,
            validated_identity i t r hh.2,validated_artifact_valid i t r hh.2⟩

end Komorebi.AVOC.Binding
