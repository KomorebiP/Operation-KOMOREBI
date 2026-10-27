import AVOC.BayesianObservationTransport
import AVOC.BayesianExamples
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC.BayesianTransportExamples

/-- The true signal is rare and favors one hidden world. -/
def rareFalseChannel : RationalChannel Bool Bool where
  prob w o := if o then (if w then 0 else 1/100) else (if w then 1 else 99/100)
  nonneg := by intro w o; cases w <;> cases o <;> norm_num
  sum_one := by intro w; cases w <;> norm_num [Fintype.sum_bool]

def rareTrueChannel : RationalChannel Bool Bool where
  prob w o := if o then (if w then 1/100 else 0) else (if w then 99/100 else 1)
  nonneg := by intro w o; cases w <;> cases o <;> norm_num
  sum_one := by intro w; cases w <;> norm_num [Fintype.sum_bool]

theorem rare_joint_error : jointObservationL1 uniformBoolBelief uniformBoolBelief
    rareFalseChannel rareTrueChannel = 1/50 := by
  norm_num [jointObservationL1, uniformBoolBelief, rareFalseChannel, rareTrueChannel, Fintype.sum_bool]

theorem rare_predictive_mass : predictiveProb uniformBoolBelief rareFalseChannel true = 1/200 := by
  norm_num [predictiveProb, uniformBoolBelief, rareFalseChannel, Fintype.sum_bool]

theorem rare_branch_posterior_error :
    beliefL1Distance (bayesUpdateTotal uniformBoolBelief rareFalseChannel true)
      (bayesUpdateTotal uniformBoolBelief rareTrueChannel true) = 2 := by
  norm_num [beliefL1Distance, bayesUpdateTotal, bayesUpdate, bayesNumerator,
    predictiveProb, uniformBoolBelief, rareFalseChannel, rareTrueChannel, Fintype.sum_bool]

theorem common_predictive_mass : predictiveProb uniformBoolBelief rareFalseChannel false = 199/200 := by
  norm_num [predictiveProb, uniformBoolBelief, rareFalseChannel, Fintype.sum_bool]

theorem common_branch_posterior_error :
    beliefL1Distance (bayesUpdateTotal uniformBoolBelief rareFalseChannel false)
      (bayesUpdateTotal uniformBoolBelief rareTrueChannel false) = 2/199 := by
  norm_num [beliefL1Distance, bayesUpdateTotal, bayesUpdate, bayesNumerator,
    predictiveProb, uniformBoolBelief, rareFalseChannel, rareTrueChannel, Fintype.sum_bool]

theorem rare_average_posterior_error :
    (∑ o, predictiveProb uniformBoolBelief rareFalseChannel o *
      beliefL1Distance (bayesUpdateTotal uniformBoolBelief rareFalseChannel o)
        (bayesUpdateTotal uniformBoolBelief rareTrueChannel o)) = 1/50 := by
  rw [Fintype.sum_bool, rare_predictive_mass, common_predictive_mass,
    rare_branch_posterior_error, common_branch_posterior_error]
  norm_num

/-- The general average guarantee must not be relabeled as a per-branch bound. -/
theorem rare_average_bound_is_not_pointwise :
    ¬ beliefL1Distance (bayesUpdateTotal uniformBoolBelief rareFalseChannel true)
      (bayesUpdateTotal uniformBoolBelief rareTrueChannel true) ≤
      2 * jointObservationL1 uniformBoolBelief uniformBoolBelief rareFalseChannel rareTrueChannel := by
  rw [rare_branch_posterior_error, rare_joint_error]
  norm_num

end Komorebi.AVOC.BayesianTransportExamples
