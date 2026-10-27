import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : residual 4 = 0 := by
  apply norm_eq_zero.mp
  rw [residual_opNorm]
  norm_num

end
