import KomorebiLSM.ConditionalEventTV

/-! A zero-mass event does not acquire a probability posterior by normalization. -/
set_option autoImplicit false
open MeasureTheory ProbabilityTheory
example : (ProbabilityTheory.cond (Measure.dirac false) {true}).real Set.univ=1 := by
  norm_num [ProbabilityTheory.cond,Measure.real]
