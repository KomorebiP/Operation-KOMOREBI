import Mathlib.Analysis.InnerProductSpace.LaxMilgram
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Tactic

set_option autoImplicit false

noncomputable section
universe u v
namespace KomorebiSpace.RegularizedHilbertRepair
open scoped RealInnerProductSpace
variable {H : Type u} {Y : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable (T : H →L[ℝ] Y) (α : ℝ)

def normal : H →L[ℝ] H := T.adjoint.comp T + α • ContinuousLinearMap.id ℝ H

@[simp] theorem normal_apply (a : H) : normal T α a = T.adjoint (T a) + α • a := rfl

@[simp] theorem normal_inner (a b : H) :
    ⟪normal T α a, b⟫ = ⟪T a, T b⟫ + α * ⟪a, b⟫ := by
  simp only [normal_apply, inner_add_left, real_inner_smul_left,
    ContinuousLinearMap.adjoint_inner_left]

def energyBilin : H →L[ℝ] H →L[ℝ] ℝ := (innerSL ℝ).comp (normal T α)

@[simp] theorem energyBilin_apply (a b : H) :
    energyBilin T α a b = ⟪T a, T b⟫ + α * ⟪a, b⟫ := by
  change ⟪normal T α a, b⟫ = _
  exact normal_inner T α a b

theorem energyBilin_coercive (hα : 0 < α) : IsCoercive (energyBilin T α) := by
  refine ⟨α, hα, ?_⟩
  intro a
  rw [energyBilin_apply, real_inner_self_eq_norm_sq, real_inner_self_eq_norm_sq]
  nlinarith [sq_nonneg ‖T a‖]

def normalEquiv (hα : 0 < α) : H ≃L[ℝ] H :=
  (energyBilin_coercive T α hα).continuousLinearEquivOfBilin

@[simp] theorem normalEquiv_apply (hα : 0 < α) (a : H) :
    normalEquiv T α hα a = normal T α a := by
  apply ext_inner_right ℝ
  intro b
  exact (IsCoercive.continuousLinearEquivOfBilin_apply (energyBilin_coercive T α hα) a b).trans
    (show energyBilin T α a b = ⟪normal T α a,b⟫ from rfl)

def correction (hα : 0 < α) (r : Y) : H :=
  (normalEquiv T α hα).symm (T.adjoint r)

@[simp] theorem normal_correction (hα : 0 < α) (r : Y) :
    normal T α (correction T α hα r) = T.adjoint r := by
  rw [← normalEquiv_apply T α hα]
  exact (normalEquiv T α hα).apply_symm_apply _

def objective (r : Y) (a : H) : ℝ := ‖T a - r‖^2 + α * ‖a‖^2

def gradient (r : Y) (a : H) : H := normal T α a - T.adjoint r

@[simp] theorem gradient_correction (hα : 0 < α) (r : Y) :
    gradient T α r (correction T α hα r) = 0 := by
  simp [gradient]

theorem normal_equation (hα : 0 < α) (r : Y) :
    T.adjoint (r - T (correction T α hα r)) = α • correction T α hα r := by
  have h := normal_correction T α hα r
  rw [normal_apply] at h
  rw [map_sub, ← h]
  abel

theorem objective_expansion (r : Y) (a h : H) :
    objective T α r (a+h) = objective T α r a +
      2 * ⟪gradient T α r a,h⟫ + ‖T h‖^2 + α * ‖h‖^2 := by
  have hm : T (a+h)-r = (T a-r)+T h := by rw [map_add]; abel
  simp only [objective, hm, norm_add_sq_real, gradient, inner_sub_left,
    normal_inner, ContinuousLinearMap.adjoint_inner_left, inner_sub_left]
  ring

theorem energy_identity (hα : 0 < α) (r : Y) (a : H) :
    objective T α r a - objective T α r (correction T α hα r) =
      ‖T (a-correction T α hα r)‖^2 + α * ‖a-correction T α hα r‖^2 := by
  have he := objective_expansion T α r (correction T α hα r) (a-correction T α hα r)
  rw [add_sub_cancel, gradient_correction, inner_zero_left] at he
  linarith

end KomorebiSpace.RegularizedHilbertRepair
