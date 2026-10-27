import Komorebi.SufficientResolution.TikhonovConstruction
import Mathlib.Tactic.Ring

/-!
# Actual Tikhonov objective and its unique minimizer

The normal equation is connected to the actual squared-norm objective by a
completed-square identity. No minimization property is assumed in the construction.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovOptimality

open TikhonovConstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V) (lam : ℝ)

/-- Actual data-fit plus squared-source penalty. -/
def objective (v : V) (x : G) : ℝ := ‖A x-v‖^2 + lam * ‖x‖^2

omit [CompleteSpace G] [CompleteSpace V] in
 theorem objective_nonneg (hlam : 0 ≤ lam) (v : V) (x : G) :
    0 ≤ objective A lam v x := by
  unfold objective
  positivity

 theorem residual_pairing (hlam : 0 < lam) (v : V) (h : G) :
    inner ℝ (A (regularized A lam hlam v)-v) (A h) +
      lam * inner ℝ (regularized A lam hlam v) h = 0 := by
  have he := congrArg (fun x : G => inner ℝ x h) (normal_equation_expanded A lam hlam v)
  simpa only [inner_add_left, real_inner_smul_left,
    ContinuousLinearMap.adjoint_inner_left, inner_zero_left] using he

 theorem objective_increment (hlam : 0 < lam) (v : V) (h : G) :
    objective A lam v (regularized A lam hlam v+h) =
      objective A lam v (regularized A lam hlam v) + ‖A h‖^2 + lam * ‖h‖^2 := by
  have hz := residual_pairing A lam hlam v h
  unfold objective
  rw [map_add, show A (regularized A lam hlam v)+A h-v =
      (A (regularized A lam hlam v)-v)+A h by abel]
  rw [norm_add_sq_real, norm_add_sq_real]
  nlinarith

 theorem objective_gap (hlam : 0 < lam) (v : V) (x : G) :
    objective A lam v x = objective A lam v (regularized A lam hlam v) +
      ‖A (x-regularized A lam hlam v)‖^2 + lam * ‖x-regularized A lam hlam v‖^2 := by
  have h := objective_increment A lam hlam v (x-regularized A lam hlam v)
  simpa only [add_sub_cancel] using h

 theorem minimizes (hlam : 0 < lam) (v : V) (x : G) :
    objective A lam v (regularized A lam hlam v) ≤ objective A lam v x := by
  rw [objective_gap A lam hlam v x]
  have hn := mul_nonneg hlam.le (sq_nonneg ‖x-regularized A lam hlam v‖)
  nlinarith [sq_nonneg ‖A (x-regularized A lam hlam v)‖]

 theorem objective_equal_iff (hlam : 0 < lam) (v : V) (x : G) :
    objective A lam v x = objective A lam v (regularized A lam hlam v) ↔
      x = regularized A lam hlam v := by
  constructor
  · intro he
    have hg := objective_gap A lam hlam v x
    have hn : ‖x-regularized A lam hlam v‖^2 = 0 := by
      nlinarith [sq_nonneg ‖A (x-regularized A lam hlam v)‖,
        sq_nonneg ‖x-regularized A lam hlam v‖]
    exact sub_eq_zero.mp (norm_eq_zero.mp (sq_eq_zero_iff.mp hn))
  · rintro rfl
    rfl

 theorem unique_minimizer (hlam : 0 < lam) (v : V) (x : G) :
    (∀ y, objective A lam v x ≤ objective A lam v y) ↔
      x = regularized A lam hlam v := by
  constructor
  · intro h
    apply (objective_equal_iff A lam hlam v x).mp
    exact le_antisymm (h _) (minimizes A lam hlam v x)
  · rintro rfl
    exact minimizes A lam hlam v

 theorem normal_iff_minimizer (hlam : 0 < lam) (v : V) (x : G) :
    normal A lam x = A.adjoint v ↔
      ∀ y, objective A lam v x ≤ objective A lam v y := by
  rw [normal_equation_iff A lam hlam, unique_minimizer A lam hlam]

 theorem exists_unique_minimizer (hlam : 0 < lam) (v : V) :
    ∃! x, ∀ y, objective A lam v x ≤ objective A lam v y := by
  refine ⟨regularized A lam hlam v, minimizes A lam hlam v, ?_⟩
  intro x hx
  exact (unique_minimizer A lam hlam v x).mp hx

 theorem objective_zero_comparison (hlam : 0 < lam) (v : V) :
    objective A lam v (regularized A lam hlam v) ≤ ‖v‖^2 := by
  simpa only [objective, map_zero, zero_sub, norm_neg, norm_zero, zero_pow,
    ne_eq, OfNat.ofNat_ne_zero, not_false_eq_true, mul_zero, add_zero] using
      minimizes A lam hlam v 0

 theorem source_objective_certificate (hlam : 0 < lam) (v : V) (x : G) :
    lam * ‖x-regularized A lam hlam v‖^2 ≤
      objective A lam v x-objective A lam v (regularized A lam hlam v) := by
  rw [objective_gap A lam hlam v x]
  nlinarith [sq_nonneg ‖A (x-regularized A lam hlam v)‖]

end Komorebi.SufficientResolution.TikhonovOptimality
