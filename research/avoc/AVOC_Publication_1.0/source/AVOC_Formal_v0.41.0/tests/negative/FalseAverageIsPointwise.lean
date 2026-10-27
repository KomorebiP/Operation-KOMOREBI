import AVOC.BayesianTransportExamples
open Komorebi.AVOC Komorebi.AVOC.BayesianTransportExamples
example : beliefL1Distance (bayesUpdateTotal uniformBoolBelief rareFalseChannel true)
    (bayesUpdateTotal uniformBoolBelief rareTrueChannel true) ≤
    2 * jointObservationL1 uniformBoolBelief uniformBoolBelief rareFalseChannel rareTrueChannel := by
  rw [rare_branch_posterior_error, rare_joint_error]
  norm_num
