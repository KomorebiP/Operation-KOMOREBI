import AVOC.BayesianExamples

open Komorebi.AVOC

/-- Deliberately false: a perfect `true` observation under the uniform prior
cannot leave all mass on `false`. -/
example :
    (bayesUpdate uniformBoolBelief (identityChannel Bool) true
      uniformBool_perfect_true_positive).prob false = 1 := by
  rw [perfectBoolPosterior_false]
