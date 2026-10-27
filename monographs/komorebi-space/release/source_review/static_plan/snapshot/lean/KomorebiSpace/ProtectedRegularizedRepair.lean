import KomorebiSpace.RegularizationCertificates
import KomorebiSpace.ProtectedHilbertRepair

set_option autoImplicit false

/-!
# Regularization on the actual protected Hilbert kernel

This is a bridge to ProtectedHilbertRepair.restricted, not a replacement
notion of protected correction. Measured residual data are independent of
D f. Protection holds for every such datum, but measured fit is not silently
identified with the actual residual of the repaired candidate.
-/
noncomputable section
universe u v w
namespace KomorebiSpace.ProtectedRegularizedRepair
open scoped RealInnerProductSpace
open ProtectedHilbertRepair
variable {E : Type u} {Y : Type v} {S : Type w}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable [NormedAddCommGroup S] [NormedSpace ℝ S]
variable (D : E →L[ℝ] Y) (p : E →L[ℝ] S) (α : ℝ)

/-- The restricted adjoint is the ambient adjoint projected into the permitted kernel. -/
theorem restricted_adjoint (r : Y) :
    (restricted D p).adjoint r = p.ker.orthogonalProjectionOnto (D.adjoint r) := by
  simp [restricted, ContinuousLinearMap.adjoint_comp, Submodule.adjoint_subtypeL]

def correction (hα : 0 < α) (r : Y) : p.ker :=
  RegularizedHilbertRepair.correction (restricted D p) α hα r

def repair (hα : 0 < α) (f : E) (r : Y) : E := f-(correction D p α hα r).val

theorem correction_permitted (hα : 0 < α) (r : Y) :
    p (correction D p α hα r).val = 0 := (correction D p α hα r).property

theorem repair_preserves (hα : 0 < α) (f : E) (r : Y) :
    p (repair D p α hα f r) = p f := by
  rw [repair, map_sub, correction_permitted, sub_zero]

theorem actual_residual (hα : 0 < α) (f : E) (r : Y) :
    D (repair D p α hα f r) = D f-restricted D p (correction D p α hα r) := by
  rw [repair, map_sub]
  rfl

theorem projected_normal_equation (hα : 0 < α) (r : Y) :
    p.ker.orthogonalProjectionOnto (D.adjoint (r-D (correction D p α hα r).val)) =
      α • correction D p α hα r := by
  rw [← restricted_adjoint]
  exact RegularizedHilbertRepair.normal_equation (restricted D p) α hα r

theorem energy_identity (hα : 0 < α) (r : Y) (a : p.ker) :
    (‖D a.val-r‖^2+α*‖a‖^2) -
      (‖D (correction D p α hα r).val-r‖^2+α*‖correction D p α hα r‖^2) =
      ‖D (a-correction D p α hα r).val‖^2 + α*‖a-correction D p α hα r‖^2 :=
  RegularizedHilbertRepair.energy_identity (restricted D p) α hα r a

theorem unique_best (hα : 0 < α) (r : Y) :
    ∃! a : p.ker, ∀ b : p.ker,
      ‖D a.val-r‖^2+α*‖a‖^2 ≤ ‖D b.val-r‖^2+α*‖b‖^2 :=
  RegularizedHilbertRepair.exists_unique_minimizer (restricted D p) α hα r

omit [CompleteSpace E] in
/-- An inexact proposal remains exactly protected when it is in the actual subtype. -/
theorem proposal_preserves (f : E) (a : p.ker) : p (f-a.val) = p f := by
  have ha : p a.val = 0 := a.property
  rw [map_sub, ha, sub_zero]

theorem proposal_error (hα : 0 < α) (f : E) (r : Y) (a : p.ker) :
    ‖(f-a.val)-repair D p α hα f r‖ ≤
      ‖RegularizedHilbertRepair.gradient (restricted D p) α r a‖/α := by
  have he : (f-a.val)-repair D p α hα f r = (correction D p α hα r).val-a.val := by
    rw [repair]; abel
  rw [he, norm_sub_rev]
  exact RegularizedHilbertRepair.correction_error_bound (restricted D p) α hα r a

theorem proposal_dual_gap (hα : 0 < α) (r z : Y) (a : p.ker) :
    RegularizedHilbertRepair.objective (restricted D p) α r a -
      RegularizationCertificates.dual (restricted D p) α r z =
      ‖D a.val-r+z‖^2 +
        ‖p.ker.orthogonalProjectionOnto (D.adjoint z)-α • a‖^2/α := by
  rw [RegularizationCertificates.primal_dual_gap _ _ hα, restricted_adjoint]
  rfl

end KomorebiSpace.ProtectedRegularizedRepair
