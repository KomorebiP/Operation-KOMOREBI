import KomorebiLSM.ObservationLawKernels
/- Negative control: a row null under Q's own prefix still needs a probability
fallback. A zero row cannot be accepted as the model's next-observation law. -/
open MeasureTheory ProbabilityTheory
noncomputable def missingFallback : Kernel Bool Unit :=
  Kernel.piecewise (measurableSet_singleton false)
    (Kernel.const _ (Measure.dirac ())) 0
example : (Measure.dirac false : Measure Bool) {true} = 0 := by simp
example : missingFallback true Set.univ = 1 := by
  simp [missingFallback, Kernel.piecewise_apply]
