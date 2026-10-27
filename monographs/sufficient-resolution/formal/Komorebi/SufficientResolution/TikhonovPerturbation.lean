import Komorebi.SufficientResolution.TikhonovBounds
import Mathlib.Tactic.GCongr

/-!
# Fixed-positive-parameter operator perturbation

Resolvent identities compare actual inverses. No fixed rank or positive lower
singular value of A or C is imposed. Constants depend explicitly on lambda.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovPerturbation

open TikhonovConstruction TikhonovBounds

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A C : G →L[ℝ] V) (lam mu : ℝ)

 theorem normal_operator_difference : normal C lam-normal A lam =
    C.adjoint.comp (C-A)+(C.adjoint-A.adjoint).comp A := by
  ext x
  simp only [sub_apply, add_apply,
    ContinuousLinearMap.comp_apply, normal_apply, map_sub]
  abel

 theorem normal_operator_difference_bound :
    ‖normal C lam-normal A lam‖ ≤ (‖C‖+‖A‖)*‖C-A‖ := by
  rw [normal_operator_difference]
  calc
    _ ≤ ‖C.adjoint.comp (C-A)‖+‖(C.adjoint-A.adjoint).comp A‖ := norm_add_le _ _
    _ ≤ ‖C.adjoint‖*‖C-A‖+‖C.adjoint-A.adjoint‖*‖A‖ :=
      add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _)
    _ = (‖C‖+‖A‖)*‖C-A‖ := by
      rw [← map_sub, LinearIsometryEquiv.norm_map, LinearIsometryEquiv.norm_map]
      ring

 theorem resolvent_difference (hlam : 0 < lam) (hmu : 0 < mu) :
    resolvent A lam hlam-resolvent C mu hmu =
      (resolvent A lam hlam).comp ((normal C mu-normal A lam).comp (resolvent C mu hmu)) := by
  ext x
  simp only [sub_apply, ContinuousLinearMap.comp_apply, map_sub,
    normal_resolvent, resolvent_normal]

 theorem resolvent_difference_bound (hlam : 0 < lam) (hmu : 0 < mu) :
    ‖resolvent A lam hlam-resolvent C mu hmu‖ ≤
      ‖normal C mu-normal A lam‖/(lam*mu) := by
  rw [resolvent_difference A C lam mu hlam hmu]
  calc
    _ ≤ ‖resolvent A lam hlam‖ *
        (‖normal C mu-normal A lam‖*‖resolvent C mu hmu‖) :=
      (ContinuousLinearMap.opNorm_comp_le _ _).trans
        (mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _))
    _ ≤ lam⁻¹*(‖normal C mu-normal A lam‖*mu⁻¹) := by
      gcongr
      · exact resolvent_opNorm_bound A lam hlam
      · exact resolvent_opNorm_bound C mu hmu
    _ = _ := by simp only [div_eq_mul_inv, mul_inv_rev]; ring

 theorem same_parameter_resolvent_bound (hlam : 0 < lam) :
    ‖resolvent A lam hlam-resolvent C lam hlam‖ ≤
      (‖A‖+‖C‖)*‖A-C‖/(lam*lam) := by
  apply (resolvent_difference_bound A C lam lam hlam hlam).trans
  apply (div_le_div_iff_of_pos_right (mul_pos hlam hlam)).mpr
  simpa only [add_comm, norm_sub_rev] using normal_operator_difference_bound A C lam

 theorem regularized_operator_difference (hlam : 0 < lam) :
    regularized A lam hlam-regularized C lam hlam =
      (resolvent A lam hlam).comp (A.adjoint-C.adjoint)+
        (resolvent A lam hlam-resolvent C lam hlam).comp C.adjoint := by
  ext v
  simp only [regularized, sub_apply, add_apply,
    ContinuousLinearMap.comp_apply, map_sub]
  abel

 theorem regularized_operator_difference_bound (hlam : 0 < lam) :
    ‖regularized A lam hlam-regularized C lam hlam‖ ≤
      ‖A-C‖/lam + ((‖A‖+‖C‖)*‖A-C‖/(lam*lam))*‖C‖ := by
  rw [regularized_operator_difference A C lam hlam]
  calc
    _ ≤ ‖(resolvent A lam hlam).comp (A.adjoint-C.adjoint)‖+
        ‖(resolvent A lam hlam-resolvent C lam hlam).comp C.adjoint‖ := norm_add_le _ _
    _ ≤ ‖resolvent A lam hlam‖*‖A.adjoint-C.adjoint‖+
        ‖resolvent A lam hlam-resolvent C lam hlam‖*‖C.adjoint‖ :=
      add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _)
    _ = ‖resolvent A lam hlam‖*‖A-C‖+
        ‖resolvent A lam hlam-resolvent C lam hlam‖*‖C‖ := by
      rw [← map_sub, LinearIsometryEquiv.norm_map, LinearIsometryEquiv.norm_map]
    _ ≤ lam⁻¹*‖A-C‖ + ((‖A‖+‖C‖)*‖A-C‖/(lam*lam))*‖C‖ := by
      gcongr
      · exact resolvent_opNorm_bound A lam hlam
      · exact same_parameter_resolvent_bound A C lam hlam
    _ = _ := by simp only [div_eq_mul_inv]; ring

 theorem parameter_difference_identity (hlam : 0 < lam) (hmu : 0 < mu) (x : G) :
    resolvent A lam hlam x-resolvent A mu hmu x =
      (mu-lam) • resolvent A lam hlam (resolvent A mu hmu x) := by
  have he := congrArg (fun f : G →L[ℝ] G => f x)
    (resolvent_difference A A lam mu hlam hmu)
  simp only [sub_apply, ContinuousLinearMap.comp_apply] at he
  rw [he]
  have hn : normal A mu (resolvent A mu hmu x)-normal A lam (resolvent A mu hmu x) =
      (mu-lam) • resolvent A mu hmu x := by rw [normal_apply, normal_apply, sub_smul]; abel
  rw [hn, map_smul]

 theorem parameter_difference_bound (hlam : 0 < lam) (hmu : 0 < mu) (x : G) :
    ‖resolvent A lam hlam x-resolvent A mu hmu x‖ ≤
      |mu-lam|/(lam*mu)*‖x‖ := by
  rw [parameter_difference_identity A lam mu hlam hmu, norm_smul, Real.norm_eq_abs]
  calc
    _ ≤ |mu-lam| *(‖resolvent A mu hmu x‖/lam) :=
      mul_le_mul_of_nonneg_left (resolvent_bound A lam hlam _) (abs_nonneg _)
    _ ≤ |mu-lam| *((‖x‖/mu)/lam) := by
      gcongr
      exact resolvent_bound A mu hmu x
    _ = _ := by simp only [div_eq_mul_inv, mul_inv_rev]; ring

 theorem regularized_parameter_difference (hlam : 0 < lam) (hmu : 0 < mu) (v : V) :
    regularized A lam hlam v-regularized A mu hmu v =
      (mu-lam) • resolvent A lam hlam (regularized A mu hmu v) :=
  parameter_difference_identity A lam mu hlam hmu (A.adjoint v)

end Komorebi.SufficientResolution.TikhonovPerturbation
