import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : ‖(1 : Space →L[ℂ] Space) - SpectralTruncation.cutoff 3‖ = 0 := by
  rw [ReconstructionExamples.identity_norm_error]
  norm_num

end
