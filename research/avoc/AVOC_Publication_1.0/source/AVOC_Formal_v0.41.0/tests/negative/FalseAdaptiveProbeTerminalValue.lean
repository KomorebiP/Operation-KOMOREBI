import AVOC.AdaptiveProbeExamples
open Komorebi.AVOC.AdaptiveProbe
open Komorebi.AVOC.AdaptiveProbe.Examples

example : successProb equalFeeModel afterBroadLeftFailure 2 = 0 := by
  rw [final_probe_certain]
