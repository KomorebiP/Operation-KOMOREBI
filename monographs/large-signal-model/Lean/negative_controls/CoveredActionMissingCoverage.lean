import KomorebiLSM.CoveredActionBoundaries

/-! A zero-propensity action cannot be recovered by the importance-weighted
observation, even in an actual finite Markov experiment. -/
set_option autoImplicit false
open MeasureTheory ProbabilityTheory
open Komorebi.LSM.CoveredAdaptiveActions
open Komorebi.LSM.CoveredAdaptiveActions.Boundaries
example : (∫ r,weightedTest neverPolicy oneTest true ((),r)∂
    (neverPolicy ⊗ₖ observations true) ())=
    targetMean (observations true) oneTest true () := by
  simp only [unobserved_evidence_zero,integral_zero,unobserved_mean_one]
  norm_num
