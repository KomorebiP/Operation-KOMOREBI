import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : HilbertSchmidtCore.hsNorm basis (residual 2)^2 = 1/16 := by
  rw [residual_hs_norm_sq]
  norm_num

end
