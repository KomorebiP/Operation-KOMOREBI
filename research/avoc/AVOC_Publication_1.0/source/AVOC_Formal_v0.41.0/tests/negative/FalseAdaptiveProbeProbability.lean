import AVOC.AdaptiveProbeExamples
open Komorebi.AVOC.AdaptiveProbe
open Komorebi.AVOC.AdaptiveProbe.Examples

example : successProb equalFeeModel initial 0 = 1/4 := by
  rw [initial_broad_probability]
