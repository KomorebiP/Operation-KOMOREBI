import AVOC.AffineExamples
open Komorebi.AVOC.Affine Komorebi.AVOC.Affine.Examples
example : executionCost (fuse bottleneck) ≤ executionCost bottleneck := by decide
