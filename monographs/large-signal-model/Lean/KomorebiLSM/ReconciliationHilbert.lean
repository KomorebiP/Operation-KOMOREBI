import KomorebiLSM.AtlasReconciliation
import KomorebiLSM.PacketApproximation
import KomorebiLSM.StrongRefinement
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Matrix.ToLin

/-! Actual Hilbert-space adapters for P20 and P21. The matrix coordinates are
constructed from an orthonormal basis, not a supplied minimization witness. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Reconciliation
universe u v
variable {X : Type u} [NormedAddCommGroup X] [InnerProductSpace ℝ X]
variable [FiniteDimensional ℝ X]

noncomputable def orthonormalOperatorCoordinates :
    (X →ₗ[ℝ] X) ≃ₗ[ℝ] Matrix (Fin (Module.finrank ℝ X)) (Fin (Module.finrank ℝ X)) ℝ :=
  (LinearMap.toMatrixAlgEquiv (stdOrthonormalBasis ℝ X).toBasis).toLinearEquiv

/-- The Frobenius objective uses actual orthonormal matrix coordinates. -/
theorem hilbert_operator_unique_minimizer {I : Type*} [Fintype I]
    (L : I → X →ₗ[ℝ] X) (w : I → ℝ) (total : ∑ i, w i=1) :
    ∃! M : X →ₗ[ℝ] X, ∀ N,
      frobeniusCost w (fun i => orthonormalOperatorCoordinates (L i))
        (orthonormalOperatorCoordinates M) ≤
      frobeniusCost w (fun i => orthonormalOperatorCoordinates (L i))
        (orthonormalOperatorCoordinates N) :=
  operator_unique_frobenius_minimizer orthonormalOperatorCoordinates L w total

/-- The independently fitted atlases are pulled back before the mean is taken.
The norm here is the actual continuous-operator norm on the common object space. -/
theorem reconciled_target_error {I : Type*} [Fintype I] {C : I → Type v}
    [∀ i, AddCommGroup (C i)] [∀ i, Module ℝ (C i)]
    (atlas : (i : I) → LinearAtlas X (C i))
    (G : (i : I) → C i →ₗ[ℝ] C i) (w : I → ℝ)
    (positive : ∀ i, 0 ≤ w i) (total : ∑ i, w i=1) (target : X →L[ℝ] X) :
    ‖(reconciledOperator atlas G w).toContinuousLinearMap-target‖ ≤
      ∑ i, w i*‖((atlas i).objectFit (G i)).toContinuousLinearMap-target‖ := by
  have hm : (reconciledOperator atlas G w).toContinuousLinearMap =
      weightedMean w (fun i => ((atlas i).objectFit (G i)).toContinuousLinearMap) := by
    simp only [reconciledOperator,weightedMean,map_sum,map_smul]
  rw [hm]
  exact weighted_target_error w _ positive total target

end Komorebi.LSM.Reconciliation

namespace Komorebi.LSM.PacketApproximation
variable {X Y : Type*} [NormedAddCommGroup X] [InnerProductSpace ℝ X]
variable [NormedAddCommGroup Y] [NormedSpace ℝ Y]
variable {I : Type*}

/-- Orthogonal subspace projectors discharge the contractivity hypothesis in the
multilinear Lipschitz estimate. No extra projection-norm hypothesis is supplied. -/
theorem orthogonal_packet_lipschitz_bound
    (S : I → Submodule ℝ X) [∀ i, (S i).HasOrthogonalProjection]
    (p : ℕ)
    (B : (m : Fin p) → ContinuousMultilinearMap ℝ (fun _ : Fin (m.val+1) => X) Y)
    (keep : (m : Fin p) → Finset (Fin (m.val+1) → I))
    (beta : (m : Fin p) → (Fin (m.val+1) → I) → ℝ)
    (hbeta : ∀ m f, 0 ≤ beta m f)
    (bound : ∀ m f, HasPacketBound (fun i => (S i).starProjection) (B m) f (beta m f))
    (b : Y) {R : ℝ} (hR : 0 ≤ R) (x y : X) (hx : ‖x‖ ≤ R) (hy : ‖y‖ ≤ R) :
    ‖retainedPolynomial p (fun i => (S i).starProjection) B keep b x-
      retainedPolynomial p (fun i => (S i).starProjection) B keep b y‖ ≤
      (∑ m, ∑ f ∈ keep m, (m.val+1:ℕ)*beta m f*R^m.val)*‖x-y‖ := by
  apply retained_polynomial_lipschitz_bound p _ _ B keep beta hbeta bound b hR x y hx hy
  intro i
  exact (S i).starProjection_norm_le

end Komorebi.LSM.PacketApproximation
