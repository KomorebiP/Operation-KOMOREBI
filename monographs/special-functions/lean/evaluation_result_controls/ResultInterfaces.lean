import CoupledEvaluationResult
open Komorebi.SpecialFunctions.Coupled.Scales
#check evaluation_success_metadata
#check evaluation_success_encloses
#check evaluation_success_disk_error
#check evaluation_majorant_error
example (x : ℚ) : x < evaluationOuter x none := evaluation_default_outer_gt x
example (p : RationalScales) (x : ℚ) :
    certifiedEvaluationSpec p x none none = .error .lastInput := rfl
example (p : RationalScales) (x S B : ℚ) :
    (makeEvaluationResult p x S B 0).U.1 = x :=
  (evaluation_result_zero_index p x S B).2.1
