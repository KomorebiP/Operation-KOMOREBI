import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Linarith
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.InnerProductSpace.LaxMilgram

/-!
# Bounded Tikhonov reconstruction without a closed-range assumption

For lambda > 0, the actual normal operator A† A + lambda I is coercive.
Lax--Milgram constructs its continuous inverse on the full Hilbert source.
Neither an inverse nor closedness of range(A) is a premise.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovConstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V) (lam : ℝ)

/-- Positive regularized normal operator. -/
def normal : G →L[ℝ] G := A.adjoint.comp A + lam • ContinuousLinearMap.id ℝ G

 theorem normal_apply (x : G) : normal A lam x = A.adjoint (A x) + lam • x := rfl

/-- The genuine bilinear form of the normal operator. -/
def normalForm : G →L[ℝ] G →L[ℝ] ℝ := (innerSL ℝ).comp (normal A lam)

 theorem normal_inner (x y : G) :
    inner ℝ (normal A lam x) y = inner ℝ (A x) (A y) + lam * inner ℝ x y := by
  simp only [normal_apply, inner_add_left, real_inner_smul_left,
    ContinuousLinearMap.adjoint_inner_left]

 theorem normal_energy (x : G) :
    inner ℝ (normal A lam x) x = ‖A x‖^2 + lam * ‖x‖^2 := by
  rw [normal_inner, real_inner_self_eq_norm_sq, real_inner_self_eq_norm_sq]

 theorem normal_symmetric (x y : G) :
    inner ℝ (normal A lam x) y = inner ℝ x (normal A lam y) := by
  simp only [normal_apply, inner_add_left, inner_add_right, real_inner_smul_left,
    real_inner_smul_right, ContinuousLinearMap.adjoint_inner_left,
    ContinuousLinearMap.adjoint_inner_right]

 theorem normalForm_coercive (hlam : 0 < lam) : IsCoercive (normalForm A lam) := by
  refine ⟨lam, hlam, ?_⟩
  intro x
  change lam * ‖x‖ * ‖x‖ ≤ inner ℝ (normal A lam x) x
  rw [normal_energy]
  nlinarith [sq_nonneg ‖A x‖]

/-- Actual Lax--Milgram equivalence of the regularized normal operator. -/
def normalEquiv (hlam : 0 < lam) : G ≃L[ℝ] G :=
  (normalForm_coercive A lam hlam).continuousLinearEquivOfBilin

 theorem normalEquiv_apply (hlam : 0 < lam) (x : G) :
    normalEquiv A lam hlam x = normal A lam x := by
  apply ext_inner_right ℝ
  intro y
  exact (normalForm_coercive A lam hlam).continuousLinearEquivOfBilin_apply x y

/-- Bounded inverse of the normal operator. -/
def resolvent (hlam : 0 < lam) : G →L[ℝ] G :=
  (normalEquiv A lam hlam).symm.toContinuousLinearMap

 theorem normal_resolvent (hlam : 0 < lam) (x : G) :
    normal A lam (resolvent A lam hlam x) = x := by
  rw [← normalEquiv_apply A lam hlam]
  exact (normalEquiv A lam hlam).apply_symm_apply x

 theorem resolvent_normal (hlam : 0 < lam) (x : G) :
    resolvent A lam hlam (normal A lam x) = x := by
  rw [← normalEquiv_apply A lam hlam]
  exact (normalEquiv A lam hlam).symm_apply_apply x

 theorem normal_injective (hlam : 0 < lam) : Function.Injective (normal A lam) := by
  intro x y h
  have hh := congrArg (resolvent A lam hlam) h
  simpa only [resolvent_normal] using hh

 theorem normal_surjective (hlam : 0 < lam) : Function.Surjective (normal A lam) := by
  intro x
  exact ⟨resolvent A lam hlam x, normal_resolvent A lam hlam x⟩

/-- Regularized recovery, defined on all local data. -/
def regularized (hlam : 0 < lam) : V →L[ℝ] G :=
  (resolvent A lam hlam).comp A.adjoint

 theorem normal_equation (hlam : 0 < lam) (v : V) :
    normal A lam (regularized A lam hlam v) = A.adjoint v :=
  normal_resolvent A lam hlam (A.adjoint v)

 theorem normal_equation_expanded (hlam : 0 < lam) (v : V) :
    A.adjoint (A (regularized A lam hlam v) - v) +
      lam • regularized A lam hlam v = 0 := by
  have h := normal_equation A lam hlam v
  rw [normal_apply] at h
  calc
    _ = (A.adjoint (A (regularized A lam hlam v)) +
      lam • regularized A lam hlam v) - A.adjoint v := by rw [map_sub]; abel
    _ = 0 := sub_eq_zero.mpr h

 theorem normal_equation_iff (hlam : 0 < lam) (v : V) (x : G) :
    normal A lam x = A.adjoint v ↔ x = regularized A lam hlam v := by
  constructor
  · intro h
    exact normal_injective A lam hlam (h.trans (normal_equation A lam hlam v).symm)
  · rintro rfl
    exact normal_equation A lam hlam v

 theorem solution_energy (hlam : 0 < lam) (v : V) :
    ‖A (regularized A lam hlam v)‖^2 + lam * ‖regularized A lam hlam v‖^2 =
      inner ℝ v (A (regularized A lam hlam v)) := by
  rw [← normal_energy, normal_equation, ContinuousLinearMap.adjoint_inner_left]

end Komorebi.SufficientResolution.TikhonovConstruction
