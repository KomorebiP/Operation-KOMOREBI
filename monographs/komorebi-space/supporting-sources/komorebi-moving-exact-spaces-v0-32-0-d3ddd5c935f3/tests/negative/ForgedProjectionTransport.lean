import KomorebiSpace
open KomorebiSpace.MovingKernelExamples KomorebiSpace.HilbertKernelProjection
example : ((intervalCertificate (1/2) (by norm_num)).kernelEquiv
    ⟨vec 0 1,by simp [defect_apply,vec]⟩).val=projection (defect (1/2)) (vec 0 1) := by
  rw [kernel_transport_formula,projection_formula]
  ext i
  fin_cases i <;> norm_num [projected,vec]
