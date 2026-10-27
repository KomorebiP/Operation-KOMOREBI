module
public import Mathlib.Analysis.Normed.Operator.Basic
public import Mathlib.Analysis.Normed.Operator.Bilinear
public import Mathlib.Analysis.Normed.Group.InfiniteSum

/-!
Author: Komorebi P.
Paper VIII item 8.1. Actual bounded linear maps and their operator norm.
Only error support is needed for the inequality; exact-block support is not assumed.
This is not a proof about IEEE arithmetic or a particular CUDA implementation.
-/

public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators
variable {K X I E : Type*} [NontriviallyNormedField K]
variable [NormedAddCommGroup X] [NormedSpace K X] [Fintype E]

/-- The actual operator error is the sum of source-supported error blocks. -/
theorem packet_error_operator_identity (P : I → X →L[K] X) (src : E → I)
    (A Δ : E → X →L[K] X) (hΔ : ∀ e, Δ e = (Δ e).comp (P (src e))) :
    (∑ e, (A e + Δ e)) - (∑ e, A e) = ∑ e, (Δ e).comp (P (src e)) := by
  rw [Finset.sum_add_distrib, add_sub_cancel_left]
  exact Finset.sum_congr rfl (fun e _ => hΔ e)

/-- The source-vector identity underlying the packetwise certificate. -/
theorem packet_error_action_identity (P : I → X →L[K] X) (src : E → I)
    (A Δ : E → X →L[K] X) (hΔ : ∀ e, Δ e = (Δ e).comp (P (src e))) (x : X) :
    ((∑ e, (A e + Δ e)) - (∑ e, A e)) x = ∑ e, Δ e (P (src e) x) := by
  rw [packet_error_operator_identity P src A Δ hΔ]
  simp only [sum_apply, ContinuousLinearMap.comp_apply]

/-- Theorem 8.1, absolute form, for the actual vector produced by the perturbed operator. -/
theorem packet_perturbation_bound (P : I → X →L[K] X) (src : E → I)
    (A Δ : E → X →L[K] X) (hΔ : ∀ e, Δ e = (Δ e).comp (P (src e))) (x : X) :
    ‖((∑ e, (A e + Δ e)) - (∑ e, A e)) x‖ ≤ ∑ e, ‖Δ e‖ * ‖P (src e) x‖ := by
  rw [packet_error_action_identity P src A Δ hΔ]
  exact (norm_sum_le _ _).trans (Finset.sum_le_sum (fun e _ => (Δ e).le_opNorm _))

/-- Theorem 8.1, relative edge-error form. -/
theorem packet_relative_perturbation_bound (P : I → X →L[K] X) (src : E → I)
    (A Δ : E → X →L[K] X) (hΔ : ∀ e, Δ e = (Δ e).comp (P (src e)))
    (ε : E → ℝ) (hε : ∀ e, ‖Δ e‖ ≤ ε e * ‖A e‖) (x : X) :
    ‖((∑ e, (A e + Δ e)) - (∑ e, A e)) x‖ ≤
      ∑ e, ε e * ‖A e‖ * ‖P (src e) x‖ := by
  apply (packet_perturbation_bound P src A Δ hΔ x).trans
  exact Finset.sum_le_sum (fun e _ => mul_le_mul_of_nonneg_right (hε e) (norm_nonneg _))

/-- A uniform operator certificate, suitable for use in later product-chain estimates. -/
theorem packet_operator_perturbation_bound (P : I → X →L[K] X) (src : E → I)
    (A Δ : E → X →L[K] X) (hΔ : ∀ e, Δ e = (Δ e).comp (P (src e))) :
    ‖(∑ e, (A e + Δ e)) - (∑ e, A e)‖ ≤ ∑ e, ‖Δ e‖ * ‖P (src e)‖ := by
  rw [packet_error_operator_identity P src A Δ hΔ]
  exact (norm_sum_le _ _).trans
    (Finset.sum_le_sum (fun e _ => ContinuousLinearMap.opNorm_comp_le _ _))

/-- Contractive source projectors turn the local errors into a simple uniform bound. -/
theorem contractive_packet_operator_bound (P : I → X →L[K] X) (src : E → I)
    (A Δ : E → X →L[K] X) (hΔ : ∀ e, Δ e = (Δ e).comp (P (src e)))
    (hP : ∀ i, ‖P i‖ ≤ 1) :
    ‖(∑ e, (A e + Δ e)) - (∑ e, A e)‖ ≤ ∑ e, ‖Δ e‖ := by
  apply (packet_operator_perturbation_bound P src A Δ hΔ).trans
  apply Finset.sum_le_sum
  intro e _
  simpa using mul_le_mul_of_nonneg_left (hP (src e)) (norm_nonneg (Δ e))

end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.packet_error_operator_identity
#print axioms KomorebiPaperVIII.packet_error_action_identity
#print axioms KomorebiPaperVIII.packet_perturbation_bound
#print axioms KomorebiPaperVIII.packet_relative_perturbation_bound
#print axioms KomorebiPaperVIII.packet_operator_perturbation_bound
#print axioms KomorebiPaperVIII.contractive_packet_operator_bound
