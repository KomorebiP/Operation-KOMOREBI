import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.RelativisticPauli
open scoped Matrix

example : alpha * beta = beta * alpha := by
  rw [alpha_mul_beta, beta_mul_alpha]

end
