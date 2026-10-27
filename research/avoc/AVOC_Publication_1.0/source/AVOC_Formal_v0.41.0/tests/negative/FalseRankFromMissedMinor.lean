import AVOC.AffineProbeExamples
open Komorebi.AVOC.Affine.ProbeExamples
example : hiddenTwo.linear.rank ≤ 1 := by
  have h := missed_minor_no_upper_bound.2
  omega
