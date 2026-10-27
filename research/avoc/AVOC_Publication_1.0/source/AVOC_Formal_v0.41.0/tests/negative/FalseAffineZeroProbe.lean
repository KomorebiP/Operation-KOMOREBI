import AVOC.AffineExamples
open Komorebi.AVOC.Affine Komorebi.AVOC.Affine.Examples
example : eval (identity 1 : Signature F 1 1) 0 = eval constantOne 0 := by decide
