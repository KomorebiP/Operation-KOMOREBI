import Komorebi.SufficientResolution.OperatorUncertainty

/-!
# Transporting actually computed residuals to the true operator

These a posteriori estimates complement inflated-noise discrepancy selection.
They keep model error distinct from the normal residual of the computed model.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.OperatorResidualTransport

open OperatorUncertainty InexactResidual TikhonovConstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A C : G →L[ℝ] V)

 theorem normal_residual_difference (lam : ℝ) (v : V) (x : G) :
    normalResidual A lam v x-normalResidual C lam v x =
      (A.adjoint-C.adjoint) (C x-v)+A.adjoint ((A-C) x) := by
  simp only [normalResidual, normal_apply, sub_apply, map_sub]
  abel

 theorem normal_residual_difference_bound (lam : ℝ) (v : V) (x : G)
    (delta : ℝ) (hd : ‖C-A‖ ≤ delta) :
    ‖normalResidual A lam v x-normalResidual C lam v x‖ ≤
      delta*‖C x-v‖+‖A‖*delta*‖x‖ := by
  have had : ‖A.adjoint-C.adjoint‖ ≤ delta := by
    rw [← map_sub, LinearIsometryEquiv.norm_map, norm_sub_rev]
    exact hd
  have h1 : ‖(A.adjoint-C.adjoint) (C x-v)‖ ≤ delta*‖C x-v‖ :=
    ((A.adjoint-C.adjoint).le_opNorm _).trans
      (mul_le_mul_of_nonneg_right had (norm_nonneg _))
  have h2 : ‖A.adjoint ((A-C) x)‖ ≤ ‖A‖*(delta*‖x‖) := by
    calc
      _ ≤ ‖A.adjoint‖*‖(A-C) x‖ := A.adjoint.le_opNorm _
      _ = ‖A‖*‖A x-C x‖ := by rw [LinearIsometryEquiv.norm_map]; rfl
      _ ≤ ‖A‖*(delta*‖x‖) := mul_le_mul_of_nonneg_left
        (reverse_action_error A C delta hd x) (norm_nonneg _)
  rw [normal_residual_difference]
  exact (norm_add_le _ _).trans (by nlinarith [add_le_add h1 h2])

 theorem normal_residual_available_bound (lam : ℝ) (v : V) (x : G)
    (delta : ℝ) (hd : ‖C-A‖ ≤ delta) :
    ‖normalResidual A lam v x-normalResidual C lam v x‖ ≤
      delta*(‖C x-v‖+(‖C‖+delta)*‖x‖) := by
  have hdn := operator_allowance_nonneg A C delta hd
  have hAn := true_operator_norm_le A C delta hd
  calc
    _ ≤ delta*‖C x-v‖+‖A‖*delta*‖x‖ :=
      normal_residual_difference_bound A C lam v x delta hd
    _ ≤ delta*‖C x-v‖+(‖C‖+delta)*delta*‖x‖ := by gcongr
    _ = _ := by ring

 theorem true_normal_residual_bound (lam : ℝ) (v : V) (x : G)
    (delta rho : ℝ) (hd : ‖C-A‖ ≤ delta)
    (hr : ‖normalResidual C lam v x‖ ≤ rho) :
    ‖normalResidual A lam v x‖ ≤
      rho+delta*(‖C x-v‖+(‖C‖+delta)*‖x‖) := by
  calc
    _ ≤ ‖normalResidual A lam v x-normalResidual C lam v x‖+
        ‖normalResidual C lam v x‖ := norm_le_norm_sub_add _ _
    _ ≤ delta*(‖C x-v‖+(‖C‖+delta)*‖x‖)+rho :=
      add_le_add (normal_residual_available_bound A C lam v x delta hd) hr
    _ = _ := add_comm _ _

end Komorebi.SufficientResolution.OperatorResidualTransport
