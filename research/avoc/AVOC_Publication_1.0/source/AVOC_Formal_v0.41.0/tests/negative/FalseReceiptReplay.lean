import AVOC.ArtifactExamples
open Komorebi.AVOC.ArtifactExamples Komorebi.AVOC.Binding
example : (consume (consume exampleSlot exampleIdentity exampleReceipt).1
    exampleIdentity exampleReceipt).2 = some exampleTicket := by
  rw [replay_rejected]
  decide
