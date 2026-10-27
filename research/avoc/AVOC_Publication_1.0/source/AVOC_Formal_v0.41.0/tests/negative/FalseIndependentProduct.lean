import AVOC.VerifierExamples

namespace Komorebi.AVOC

/-- Deliberately false: perfectly correlated verifier failures do not factorize. -/
example : JointFailureFactorizes uniformBoolBelief perfectlyCorrelatedFailure := by
  unfold JointFailureFactorizes
  rw [perfectlyCorrelatedFailure_joint_prob,
    perfectlyCorrelatedFailure_product_marginals]
  norm_num

end Komorebi.AVOC
