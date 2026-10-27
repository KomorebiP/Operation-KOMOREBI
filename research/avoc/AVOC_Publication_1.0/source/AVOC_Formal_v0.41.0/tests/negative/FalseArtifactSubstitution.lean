import AVOC.ArtifactExamples
open Komorebi.AVOC.ArtifactExamples Komorebi.AVOC.Binding
example : validate exampleIdentity exampleTicket
    ⟨⟨0, {exampleArtifact with sourceBytes := "candidate version B"}⟩, true⟩ = true := by
  rw [candidate_substitution_rejected]
  decide
