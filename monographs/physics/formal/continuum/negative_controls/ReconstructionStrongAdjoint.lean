import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : Tendsto (fun n => star (ReconstructionExamples.sheared n) (basis 0))
    atTop (𝓝 (basis 0)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  simp only [ReconstructionExamples.sheared_adjoint_error, ReconstructionExamples.basis_norm]
  norm_num [tendsto_const_nhds_iff]

end
