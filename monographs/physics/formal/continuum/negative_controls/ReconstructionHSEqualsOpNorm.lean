import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : HilbertSchmidtCore.hsNorm basis (residual 2)^2 = ‖residual 2‖^2 := by
  rw [residual_hs_norm_sq, residual_opNorm]
  norm_num

end
