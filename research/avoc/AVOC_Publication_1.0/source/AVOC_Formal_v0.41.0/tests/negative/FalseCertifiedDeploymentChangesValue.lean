import AVOC.OperationalExamples

open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.OperationalExamples

example : execute warmDeployment.selected (fun _ => 0) 0 = 1 := by
  decide
