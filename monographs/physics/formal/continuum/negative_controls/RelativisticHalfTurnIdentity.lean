import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.RelativisticPauli
open KomorebiPhysics.DiracWalk1D
open KomorebiPhysics.Relativistic1DExamples
open scoped Matrix

example : update 1 1 (Real.pi / 2) = (1 : Mat2) := by
  rw [update_pi_div_two]
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two]

end
