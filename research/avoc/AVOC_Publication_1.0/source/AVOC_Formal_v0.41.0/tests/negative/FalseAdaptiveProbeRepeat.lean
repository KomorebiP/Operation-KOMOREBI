import AVOC.AdaptiveProbeExamples
open Komorebi.AVOC.AdaptiveProbe
open Komorebi.AVOC.AdaptiveProbe.Examples

example : (0 : Probe) ∈ afterBroadFailure.remaining := by
  exact List.mem_of_mem_erase (by simp)
