import PaperIRelease.PacketBoundaryTests
open Komorebi.PaperIRelease.PacketBoundaryTests
example : Module.End ℤ ((ℤ × ℤ) ⧸ horizontal) :=
  horizontal.mapQ horizontal swapEnd (by
    intro x hx
    exact hx)
