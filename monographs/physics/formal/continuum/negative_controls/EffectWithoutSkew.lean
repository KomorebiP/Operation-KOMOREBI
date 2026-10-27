import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : deriv (fun t : ℝ => (oscillatingAtlas 0).probability (1 + (t : ℂ)) 0) 0 =
    ∑ j : Fin 2, (oscillatingAtlas 0).current (1 : ℂ →L[ℂ] ℂ) 1 0 j := by
  rw [identity_probability_derivative.deriv]
  simp only [identity_effect_current_zero, Finset.sum_const_zero]
  norm_num
