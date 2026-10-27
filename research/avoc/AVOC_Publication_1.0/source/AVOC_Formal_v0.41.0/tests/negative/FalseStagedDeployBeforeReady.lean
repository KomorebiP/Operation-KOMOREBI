import AVOC.StagedAffineExamples
open Komorebi.AVOC.Affine.Staged
open Komorebi.AVOC.Affine.StagedExamples
example : Action.deployWarm ∈ actions certainModel startCertain := by
  exact warm_deploy_unavailable_initial
