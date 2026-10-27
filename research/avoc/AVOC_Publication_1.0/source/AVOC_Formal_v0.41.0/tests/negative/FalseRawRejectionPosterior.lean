import AVOC.ArtifactWorkflowExamples
open Komorebi.AVOC
open ArtifactWorkflowExamples
example : (bayesUpdateTotal prior coarse false).prob true =
    (bayesUpdateTotal prior raw (1 : Fin 3)).prob true := by
  rw [coarse_rejection_posterior, raw_rejection_posterior]
  norm_num
