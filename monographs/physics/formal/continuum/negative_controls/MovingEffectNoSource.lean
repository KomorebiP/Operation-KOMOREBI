import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : deriv (fun t => (oscillatingAtlas t).probability 1 0) 0 = 0 := by
  rw [oscillating_probability_hasDerivAt.deriv]
  norm_num
