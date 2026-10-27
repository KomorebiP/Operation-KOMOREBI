import KomorebiSpace.MovingKernelBounds
import Mathlib.Analysis.SpecificLimits.Normed

set_option autoImplicit false

/-!
# Small perturbations of a split-surjective defect

A bounded right inverse of d is an explicit input. A Neumann inverse on the
residual space constructs a right inverse of e when a*epsilon<1. The perturbed
residual bound and kernel comparison are conclusions: no preservation of the
old kernel is assumed. The graph comparison is relative to the chosen splitting.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace SplitKernel
open HilbertKernelProjection
variable {E : Type u} {R : Type v}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R] [CompleteSpace R]
variable (d e : E →L[ℝ] R)

structure Certificate where
  sectionMap : R →L[ℝ] E
  right_inverse : ∀ r, d (sectionMap r) = r
  constant : ℝ
  nonneg : 0 ≤ constant
  section_bound : ∀ r, ‖sectionMap r‖ ≤ constant*‖r‖
  epsilon : ℝ
  epsilon_nonneg : 0 ≤ epsilon
  operator_error : ‖d-e‖ ≤ epsilon
  small : constant*epsilon < 1

namespace Certificate
variable {d e} (T : Certificate d e)

/-- Error in the old residual-coordinate section. -/
def residualError : R →L[ℝ] R := (d-e).comp T.sectionMap

omit [CompleteSpace E] [CompleteSpace R] in
theorem residualError_bound : ‖T.residualError‖ ≤ T.constant*T.epsilon := by
  apply ContinuousLinearMap.opNorm_le_bound _ (mul_nonneg T.nonneg T.epsilon_nonneg)
  intro r
  change ‖(d-e) (T.sectionMap r)‖ ≤ _
  calc
    _ ≤ ‖d-e‖*‖T.sectionMap r‖ := (d-e).le_opNorm _
    _ ≤ T.epsilon*(T.constant*‖r‖) :=
      mul_le_mul T.operator_error (T.section_bound r) (norm_nonneg _) T.epsilon_nonneg
    _ = _ := by ring

omit [CompleteSpace E] [CompleteSpace R] in
theorem residualError_small : ‖T.residualError‖ < 1 :=
  T.residualError_bound.trans_lt T.small

/-- A genuine invertible residual-coordinate map, constructed by a geometric series. -/
def residualEquiv : R ≃L[ℝ] R :=
  ContinuousLinearEquiv.ofUnit (Units.oneSub T.residualError T.residualError_small)

omit [CompleteSpace E] in
@[simp] theorem residualEquiv_apply (r : R) : T.residualEquiv r = e (T.sectionMap r) := by
  change r-(d-e) (T.sectionMap r)=_
  rw [sub_apply,T.right_inverse]
  abel

omit [CompleteSpace E] in
/-- The inverse norm is derived from the strict radius, not supplied separately. -/
theorem residual_inverse_bound (r : R) :
    ‖T.residualEquiv.symm r‖ ≤ (1/(1-T.constant*T.epsilon))*‖r‖ := by
  let z := T.residualEquiv.symm r
  have hid : z = r+T.residualError z := by
    have hi := T.residualEquiv.apply_symm_apply r
    change z-T.residualError z = r at hi
    exact (sub_eq_iff_eq_add).mp hi
  have hz : ‖z‖ ≤ ‖r‖+(T.constant*T.epsilon)*‖z‖ := by
    calc
      ‖z‖ = ‖r+T.residualError z‖ := congrArg norm hid
      _ ≤ ‖r‖+‖T.residualError z‖ := norm_add_le _ _
      _ ≤ _ := add_le_add le_rfl ((T.residualError.le_opNorm z).trans
        (mul_le_mul_of_nonneg_right T.residualError_bound (norm_nonneg z)))
  have hp : 0 < 1-T.constant*T.epsilon := sub_pos.mpr T.small
  have hh : (1-T.constant*T.epsilon)*‖z‖ ≤ ‖r‖ := by nlinarith
  calc
    ‖z‖ ≤ ‖r‖/(1-T.constant*T.epsilon) := (le_div_iff₀ hp).mpr (by nlinarith [hh])
    _ = _ := by ring

/-- The perturbed right inverse retains the old section range. -/
def perturbedSection : R →L[ℝ] E :=
  T.sectionMap.comp T.residualEquiv.symm.toContinuousLinearMap

omit [CompleteSpace E] in
@[simp] theorem perturbed_right_inverse (r : R) : e (T.perturbedSection r) = r := by
  change e (T.sectionMap (T.residualEquiv.symm r)) = r
  rw [← T.residualEquiv_apply]
  exact T.residualEquiv.apply_symm_apply r

omit [CompleteSpace E] in
theorem perturbed_section_bound (r : R) :
    ‖T.perturbedSection r‖ ≤ (T.constant/(1-T.constant*T.epsilon))*‖r‖ := by
  exact (T.section_bound _).trans (by
    calc
      T.constant*‖T.residualEquiv.symm r‖ ≤
          T.constant*((1/(1-T.constant*T.epsilon))*‖r‖) :=
        mul_le_mul_of_nonneg_left (T.residual_inverse_bound r) T.nonneg
      _ = _ := by ring)

include T in
omit [CompleteSpace E] in
theorem perturbed_surjective : Function.Surjective e :=
  fun r => ⟨T.perturbedSection r, T.perturbed_right_inverse r⟩

/-- A right inverse supplies an exact competitor, hence an orthogonal repair bound. -/
def referenceBound : ResidualRobustness.Bound d where
  constant := T.constant
  nonneg := T.nonneg
  estimate x := by
    have hx : d (x-T.sectionMap (d x))=0 := by rw [map_sub,T.right_inverse,sub_self]
    have hb := projection_best d x (x-T.sectionMap (d x)) hx
    have hid : x-(x-T.sectionMap (d x))=T.sectionMap (d x) := by abel
    rw [hid] at hb
    exact hb.trans (T.section_bound _)

def perturbedBound : ResidualRobustness.Bound e where
  constant := T.constant/(1-T.constant*T.epsilon)
  nonneg := div_nonneg T.nonneg (le_of_lt (sub_pos.mpr T.small))
  estimate x := by
    have hx : e (x-T.perturbedSection (e x))=0 := by
      rw [map_sub,T.perturbed_right_inverse,sub_self]
    have hb := projection_best e x (x-T.perturbedSection (e x)) hx
    have hid : x-(x-T.perturbedSection (e x))=T.perturbedSection (e x) := by abel
    rw [hid] at hb
    exact hb.trans (T.perturbed_section_bound _)

include T in
theorem perturbed_range_closed : IsClosed (Set.range e) :=
  closed_range_of_bound e T.perturbedBound.constant T.perturbedBound.nonneg
    T.perturbedBound.estimate

/-- A one-certificate motion bound; the new stability constant has been derived. -/
theorem projection_motion :
    ‖projection d-projection e‖ ≤
      (T.constant*T.epsilon)/(1-T.constant*T.epsilon) := by
  have hp : 0 < 1-T.constant*T.epsilon := sub_pos.mpr T.small
  have hc : T.constant ≤ T.constant/(1-T.constant*T.epsilon) := by
    apply (le_div_iff₀ hp).mpr
    nlinarith [mul_nonneg (mul_nonneg T.nonneg T.epsilon_nonneg) T.nonneg]
  have hb := MovingKernel.projection_opNorm d e T.referenceBound T.perturbedBound T.operator_error
  change ‖projection d-projection e‖ ≤ max T.constant
    (T.constant/(1-T.constant*T.epsilon))*T.epsilon at hb
  rw [max_eq_right hc] at hb
  convert hb using 1
  ring

/-- A literal old-kernel-preservation assumption is absent from this estimate. -/
theorem perturbed_measured (x : E) (r : R) (η : ℝ) (hr : ‖e x-r‖ ≤ η) :
    ‖x-projection e x‖ ≤ (T.constant/(1-T.constant*T.epsilon))*(‖r‖+η) :=
  T.perturbedBound.measured x r η hr

/-- The old splitting projection, not necessarily orthogonal. -/
def oldRetract : E →L[ℝ] E := ContinuousLinearMap.id ℝ E - T.sectionMap.comp d

/-- The new splitting projection; its kernel complement is the old section range. -/
def newRetract : E →L[ℝ] E := ContinuousLinearMap.id ℝ E - T.perturbedSection.comp e

omit [CompleteSpace E] [CompleteSpace R] in
@[simp] theorem oldRetract_apply (x : E) : T.oldRetract x = x-T.sectionMap (d x) := rfl
omit [CompleteSpace E] in
@[simp] theorem newRetract_apply (x : E) : T.newRetract x = x-T.perturbedSection (e x) := rfl

omit [CompleteSpace E] [CompleteSpace R] in
@[simp] theorem oldRetract_exact (x : E) : d (T.oldRetract x)=0 := by
  rw [T.oldRetract_apply,map_sub,T.right_inverse,sub_self]

omit [CompleteSpace E] in
@[simp] theorem newRetract_exact (x : E) : e (T.newRetract x)=0 := by
  rw [T.newRetract_apply,map_sub,T.perturbed_right_inverse,sub_self]

omit [CompleteSpace E] in
@[simp] theorem section_cancel (r : R) : T.perturbedSection (e (T.sectionMap r))=T.sectionMap r := by
  change T.sectionMap (T.residualEquiv.symm (e (T.sectionMap r)))=_
  rw [← T.residualEquiv_apply,T.residualEquiv.symm_apply_apply]

omit [CompleteSpace E] in
@[simp] theorem oldRetract_newSection (r : R) : T.oldRetract (T.perturbedSection r)=0 := by
  change T.sectionMap (T.residualEquiv.symm r)-
    T.sectionMap (d (T.sectionMap (T.residualEquiv.symm r)))=0
  rw [T.right_inverse,sub_self]

omit [CompleteSpace E] in
@[simp] theorem newRetract_oldSection (r : R) : T.newRetract (T.sectionMap r)=0 := by
  rw [T.newRetract_apply,T.section_cancel,sub_self]

def toNewKernel : d.ker →L[ℝ] e.ker :=
  (T.newRetract.comp d.ker.subtypeL).codRestrict e.ker (fun x => T.newRetract_exact x)

def toOldKernel : e.ker →L[ℝ] d.ker :=
  (T.oldRetract.comp e.ker.subtypeL).codRestrict d.ker (fun x => T.oldRetract_exact x)

omit [CompleteSpace E] in
theorem toOld_toNew (x : d.ker) : T.toOldKernel (T.toNewKernel x)=x := by
  apply Subtype.ext
  change T.oldRetract (T.newRetract x.val)=x.val
  have hx : d x.val = 0 := x.property
  rw [T.newRetract_apply,map_sub,T.oldRetract_newSection,sub_zero,
    T.oldRetract_apply,hx,map_zero,sub_zero]

omit [CompleteSpace E] in
theorem toNew_toOld (x : e.ker) : T.toNewKernel (T.toOldKernel x)=x := by
  apply Subtype.ext
  change T.newRetract (T.oldRetract x.val)=x.val
  have hx : e x.val = 0 := x.property
  rw [T.oldRetract_apply,map_sub,T.newRetract_oldSection,sub_zero,
    T.newRetract_apply,hx,map_zero,sub_zero]

/-- Actual continuously invertible transport between the moving exact spaces. -/
def kernelEquiv : d.ker ≃L[ℝ] e.ker where
  toLinearEquiv :=
    { T.toNewKernel.toLinearMap with
      invFun := T.toOldKernel
      left_inv := T.toOld_toNew
      right_inv := T.toNew_toOld }
  continuous_toFun := T.toNewKernel.continuous
  continuous_invFun := T.toOldKernel.continuous

/-- The new exact object is close to the old one in the declared ambient norm. -/
theorem kernel_transport_error (x : d.ker) :
    ‖(T.kernelEquiv x).val-x.val‖ ≤
      ((T.constant*T.epsilon)/(1-T.constant*T.epsilon))*‖x.val‖ := by
  change ‖(x.val-T.perturbedSection (e x.val))-x.val‖ ≤ _
  have hid : (x.val-T.perturbedSection (e x.val))-x.val = -T.perturbedSection (e x.val) := by abel
  rw [hid,norm_neg]
  have hd : ‖e x.val‖ ≤ T.epsilon*‖x.val‖ := by
    have he := ((d-e).le_opNorm x.val).trans
      (mul_le_mul_of_nonneg_right T.operator_error (norm_nonneg x.val))
    have hx : d x.val = 0 := x.property
    simpa only [sub_apply,hx,zero_sub,norm_neg] using he
  exact (T.perturbed_section_bound _).trans (by
    calc
      (T.constant/(1-T.constant*T.epsilon))*‖e x.val‖ ≤
          (T.constant/(1-T.constant*T.epsilon))*(T.epsilon*‖x.val‖) :=
        mul_le_mul_of_nonneg_left hd T.perturbedBound.nonneg
      _ = _ := by ring)

end Certificate
end SplitKernel
end KomorebiSpace
end
