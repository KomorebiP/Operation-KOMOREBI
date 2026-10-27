import PaperICompletion
open Komorebi.PaperICompletion.ConditionedCoordinates
-- EXPECTED REJECTION: no nontriviality instance exists on the zero space.
example : 1 ≤ conditionNumber
    (ContinuousLinearEquiv.refl ℝ (EuclideanSpace ℝ (Fin 0))) :=
  one_le_conditionNumber _
