import PaperIRelease.CategoryBoundaries
open Komorebi.PaperIRelease.CategoryBoundaries
example : mergeTwoPackets.packetMap (0 : Fin 2) ≠ mergeTwoPackets.packetMap 1 := by
  decide
