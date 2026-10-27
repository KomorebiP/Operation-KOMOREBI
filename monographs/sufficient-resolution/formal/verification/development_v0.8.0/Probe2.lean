import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Analysis.Normed.Operator.Banach
set_option autoImplicit false
noncomputable section
variable {G V : Type*} [NormedAddCommGroup G] [InnerProductSpace ℝ G]
 [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace G] [CompleteSpace V]
 (A : G →L[ℝ] V)
example : CompleteSpace A.ker := inferInstance
example : A.ker.HasOrthogonalProjection := inferInstance
example : CompleteSpace A.kerᗮ := inferInstance
example : A.kerᗮ.HasOrthogonalProjection := inferInstance
example (h : IsClosed (A.range : Set V)) : A.range.HasOrthogonalProjection := by
 letI : CompleteSpace A.range := h.completeSpace_coe
 infer_instance
#check ContinuousLinearEquiv.toContinuousLinearMap
#check ContinuousLinearMap.norm_le_opNorm
#check ContinuousLinearMap.le_opNorm
#check Submodule.norm_starProjection_apply_le
#check Submodule.orthogonal_orthogonal_eq_closure
