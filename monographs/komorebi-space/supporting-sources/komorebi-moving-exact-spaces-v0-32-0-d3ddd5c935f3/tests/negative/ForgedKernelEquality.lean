import KomorebiSpace
open KomorebiSpace.MovingKernelExamples KomorebiSpace.HilbertKernelProjection
example : projection (defect (1/2)) (vec 0 1)=projection (defect 0) (vec 0 1) := by
  rw [projection_formula,zero_projection]
  ext i
  fin_cases i <;> norm_num [projected,vec]
