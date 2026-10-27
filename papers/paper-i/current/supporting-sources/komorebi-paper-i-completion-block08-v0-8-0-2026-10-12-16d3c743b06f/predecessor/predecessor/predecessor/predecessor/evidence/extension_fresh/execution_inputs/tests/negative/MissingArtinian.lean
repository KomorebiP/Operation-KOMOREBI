import PaperICompletion4
open Polynomial Komorebi.PaperICompletion4.IntrinsicPrimary
-- Polynomial rings are not Artinian modules over themselves. This use must fail.
example : Function.Surjective (primaryToGlobal ℚ[X] (X : ℚ[X])) :=
  primaryToGlobal_surjective ℚ[X] X
