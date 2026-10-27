import AVOC.Retrospective
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- Deliberately false: the two evidence-conditioned fine posteriors differ. -/
example :
    (conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
      retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive).prob true =
    (conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
      retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive).prob true := by
  rw [retrospectivePosteriorTrue_true, retrospectivePosteriorFalse_true]
  norm_num

end Komorebi.AVOC
