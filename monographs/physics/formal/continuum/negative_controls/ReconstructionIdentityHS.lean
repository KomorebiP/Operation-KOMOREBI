import KomorebiPhysics.ReconstructionExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HilbertSchmidtExamples Filter
open scoped Topology

example : HilbertSchmidtCore.IsHS basis (1 : Space →L[ℂ] Space) := by
  simp only [HilbertSchmidtCore.IsHS, one_apply_eq_self, ReconstructionExamples.basis_norm, one_pow]
  norm_num [summable_const_iff]

end
