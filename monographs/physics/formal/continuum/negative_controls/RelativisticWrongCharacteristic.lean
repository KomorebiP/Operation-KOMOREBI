import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.RelativisticPauli
open KomorebiPhysics.Relativistic1DExamples
open scoped Matrix

example : Matrix.det ((0 : ℂ) • (1 : Mat2) -
    KomorebiPhysics.DiracWalk1D.update 1 1 (Real.pi / 2)) = 0 := by
  rw [characteristic_pi_div_two]

end
