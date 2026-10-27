import AVOC.SchedulingExamples
open Komorebi.AVOC.Scheduling Komorebi.AVOC.Scheduling.Examples
example : Legal (∅ : Finset Diamond) [tip,root,left,right] := by
  have h := diamond_bad_order
  contradiction
