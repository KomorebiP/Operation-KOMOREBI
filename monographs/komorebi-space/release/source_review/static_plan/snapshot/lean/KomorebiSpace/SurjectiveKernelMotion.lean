import KomorebiSpace.SplitKernelPerturbation

set_option autoImplicit false

/-!
# Constructing the splitting from a surjective Hilbert defect

The right inverse required by SplitKernel is derived here from surjectivity and
the Hilbert orthogonal complement. A pre-existing residual bound controls its
norm. Consequently a perturbed bound and a moving-kernel equivalence need only
the old certificate, surjectivity, and a strict operator-error radius.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace SurjectiveKernel
open HilbertKernelProjection
variable {E : Type u} {R : Type v}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R] [CompleteSpace R]
variable (d : E →L[ℝ] R) (hd : Function.Surjective d)

include hd in
omit [CompleteSpace R] in
theorem reduced_surjective : Function.Surjective (reduced d) := by
  intro r
  obtain ⟨x,hx⟩ := hd r
  refine ⟨⟨x-projection d x,error_orthogonal d x⟩,?_⟩
  exact (defect_error d x).trans hx

/-- Restriction to the orthogonal complement is a continuous linear equivalence. -/
def transverseEquiv : d.kerᗮ ≃L[ℝ] R :=
  ContinuousLinearEquiv.ofBijective (reduced d)
    (LinearMap.ker_eq_bot.mpr (reduced_injective d))
    (LinearMap.range_eq_top.mpr (reduced_surjective d hd))

/-- Canonical minimal-norm right inverse for the declared Hilbert geometry. -/
def sectionMap : R →L[ℝ] E :=
  d.kerᗮ.subtypeL.comp (transverseEquiv d hd).symm.toContinuousLinearMap

@[simp] theorem section_right (r : R) : d (sectionMap d hd r) = r :=
  (transverseEquiv d hd).apply_symm_apply r

theorem section_orthogonal (r : R) : sectionMap d hd r ∈ d.kerᗮ :=
  ((transverseEquiv d hd).symm r).property

theorem section_bound (B : ResidualRobustness.Bound d) (r : R) :
    ‖sectionMap d hd r‖ ≤ B.constant*‖r‖ := by
  have h := B.estimate (sectionMap d hd r)
  rw [projection_orthogonal_zero d _ (section_orthogonal d hd r),sub_zero,section_right] at h
  exact h

/-- No right inverse or new-kernel stability is supplied in this interface. -/
def certificate (B : ResidualRobustness.Bound d) (e : E →L[ℝ] R)
    {ε : ℝ} (hε : 0 ≤ ε) (he : ‖d-e‖ ≤ ε) (hs : B.constant*ε<1) :
    SplitKernel.Certificate d e where
  sectionMap := sectionMap d hd
  right_inverse := section_right d hd
  constant := B.constant
  nonneg := B.nonneg
  section_bound := section_bound d hd B
  epsilon := ε
  epsilon_nonneg := hε
  operator_error := he
  small := hs

/-- Surjectivity persists and supplies a full perturbed residual bound. -/
def perturbedBound (B : ResidualRobustness.Bound d) (e : E →L[ℝ] R)
    {ε : ℝ} (hε : 0 ≤ ε) (he : ‖d-e‖ ≤ ε) (hs : B.constant*ε<1) :
    ResidualRobustness.Bound e := (certificate d hd B e hε he hs).perturbedBound

include hd in
theorem projection_motion (B : ResidualRobustness.Bound d) (e : E →L[ℝ] R)
    {ε : ℝ} (hε : 0 ≤ ε) (he : ‖d-e‖ ≤ ε) (hs : B.constant*ε<1) :
    ‖projection d-projection e‖ ≤ (B.constant*ε)/(1-B.constant*ε) :=
  (certificate d hd B e hε he hs).projection_motion

/-- The perturbed exact space is explicitly equivalent, not asserted equal. -/
def kernelEquiv (B : ResidualRobustness.Bound d) (e : E →L[ℝ] R)
    {ε : ℝ} (hε : 0 ≤ ε) (he : ‖d-e‖ ≤ ε) (hs : B.constant*ε<1) :
    d.ker ≃L[ℝ] e.ker := (certificate d hd B e hε he hs).kernelEquiv

end SurjectiveKernel
end KomorebiSpace
end
