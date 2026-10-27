import AVOC.ModelBridgeExamples
open Komorebi.AVOC.Guarded Komorebi.AVOC.ModelBridgeExamples
example (s : BState) : |backup learnedSystem (coarseValue 0) s - coarseValue 1 s| ≤ 0 := by
  rw [coarse_residual]
  norm_num
