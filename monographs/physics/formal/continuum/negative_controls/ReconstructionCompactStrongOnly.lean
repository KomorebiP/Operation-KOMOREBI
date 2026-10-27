import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : Tendsto (fun n => ‖StrongReconstruction.compression
    (ReconstructionExamples.sheared n) ReconstructionExamples.packet - ReconstructionExamples.packet‖)
    atTop (𝓝 0) := by
  simp only [ReconstructionExamples.sheared_compact_error_norm]
  norm_num [tendsto_const_nhds_iff]

end
