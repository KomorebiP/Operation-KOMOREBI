import AVOC.SchedulingExamples
open Komorebi.AVOC.Scheduling Komorebi.AVOC.Scheduling.Examples
example : Ready (∅ : Finset Diamond) tip := by
  have h := antichain_not_enough.2
  contradiction
