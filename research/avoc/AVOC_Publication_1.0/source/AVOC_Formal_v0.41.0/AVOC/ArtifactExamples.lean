import AVOC.CertificateResearch

namespace Komorebi.AVOC.ArtifactExamples
open Certificate Binding

def conjSwap : Derivation :=
  .abstract (.conj (.atom 0) (.atom 1))
    (.pair (.second (.use (.conj (.atom 0) (.atom 1))))
           (.first (.use (.conj (.atom 0) (.atom 1)))))

def swapTarget : Formula := .impl (.conj (.atom 0) (.atom 1)) (.conj (.atom 1) (.atom 0))

def exampleIdentity : Identity :=
  ⟨"and-commute", swapTarget, "canonical target bytes", [], [("checker", "version 1")]⟩

def exampleArtifact : Artifact := ⟨exampleIdentity, "candidate version A", conjSwap⟩

def exampleSlot : Slot := register ⟨0, none⟩ exampleArtifact

def exampleTicket : Ticket := ⟨0, exampleArtifact⟩

def exampleReceipt : Receipt := ⟨exampleTicket, true⟩

theorem conjunction_swap_checked : check [] swapTarget conjSwap = true := by decide

theorem conjunction_swap_all_propositions (p q : Prop) : (p ∧ q) → (q ∧ p) := by
  let v : Nat → Prop := fun n => if n = 0 then p else q
  have h := check_sound [] swapTarget conjSwap conjunction_swap_checked v
    (by intro f hf; simp at hf)
  simpa [swapTarget, Denote, v] using h

theorem disjunction_swap_checked :
    check [] (.impl (.disj (.atom 0) (.atom 1)) (.disj (.atom 1) (.atom 0)))
      (.abstract (.disj (.atom 0) (.atom 1))
        (.cases (.use (.disj (.atom 0) (.atom 1)))
          (.right (.atom 1) (.use (.atom 0)))
          (.left (.atom 0) (.use (.atom 1))))) = true := by decide

theorem modus_ponens_checked :
    check [.impl (.atom 0) (.atom 1), .atom 0] (.atom 1)
      (.apply (.use (.impl (.atom 0) (.atom 1))) (.use (.atom 0))) = true := by decide

theorem false_elimination_checked :
    check [.falsity] (.atom 7) (.absurd (.atom 7) (.use .falsity)) = true := by decide

theorem missing_premise_rejected : check [] (.atom 0) (.use (.atom 0)) = false := by decide

theorem wrong_application_rejected :
    check [.impl (.atom 0) (.atom 1), .atom 2] (.atom 1)
      (.apply (.use (.impl (.atom 0) (.atom 1))) (.use (.atom 2))) = false := by decide

theorem valid_snapshot_admitted :
    (consume exampleSlot exampleIdentity exampleReceipt).2 = some exampleTicket := by decide

theorem replay_rejected :
    (consume (consume exampleSlot exampleIdentity exampleReceipt).1 exampleIdentity exampleReceipt).2 = none := by decide

theorem candidate_substitution_rejected :
    validate exampleIdentity exampleTicket
      ⟨⟨0, {exampleArtifact with sourceBytes := "candidate version B"}⟩, true⟩ = false := by decide

theorem changed_environment_rejected :
    validate {exampleIdentity with environment := [("checker", "version 2")]}
      exampleTicket exampleReceipt = false := by decide

theorem changed_dependency_rejected :
    validate {exampleIdentity with dependencies := [⟨"new", .truth, "different artifact"⟩]}
      exampleTicket exampleReceipt = false := by decide

theorem old_generation_rejected :
    (consume (register exampleSlot exampleArtifact) exampleIdentity exampleReceipt).2 = none := by decide

theorem false_approval_rejected :
    let i : Identity := ⟨"false-task", .falsity, "false", [], []⟩
    let a : Artifact := ⟨i, "fake", .truth⟩
    let t : Ticket := ⟨0, a⟩
    validate i t ⟨t, true⟩ = false := by decide

end Komorebi.AVOC.ArtifactExamples
