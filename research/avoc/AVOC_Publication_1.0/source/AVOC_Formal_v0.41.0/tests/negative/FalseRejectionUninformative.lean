import AVOC.ArtifactWorkflowExamples
open Komorebi.AVOC
open ArtifactWorkflowExamples
example : (bayesUpdateTotal prior coarse false).prob true = 1/2 := by
  rw [coarse_rejection_posterior]
  norm_num
