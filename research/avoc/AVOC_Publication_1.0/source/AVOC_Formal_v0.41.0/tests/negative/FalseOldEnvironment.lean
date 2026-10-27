import AVOC.ArtifactExamples
open Komorebi.AVOC.ArtifactExamples Komorebi.AVOC.Binding
example : validate {exampleIdentity with environment := [("checker", "version 2")]}
    exampleTicket exampleReceipt = true := by
  rw [changed_environment_rejected]
  decide
