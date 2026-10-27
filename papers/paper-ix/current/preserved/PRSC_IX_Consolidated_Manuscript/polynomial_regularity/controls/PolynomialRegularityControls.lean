module
public import PolynomialJointSystem
public import PolynomialAnalyticInverse
public import PolynomialAnalyticImplicit

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRegularityControls

open MvPolynomial Matrix
open Komorebi.PolynomialParameterSystem

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜]

/-- A genuine mixed solved/parameter equation, with nonzero parameter derivative. -/
def linearSystem : Fin 1 → MvPolynomial (Fin (1 + 1)) 𝕜 :=
  fun _ => X (Fin.castAdd 1 0) + X (Fin.natAdd 1 0)

theorem linear_solvedJacobian (a : Fin (1 + 1) → 𝕜) :
    Komorebi.PolynomialJointSystem.solvedJacobian linearSystem a = 1 := by
  ext i j
  have hi : i = 0 := Fin.eq_zero i
  have hj : j = 0 := Fin.eq_zero j
  subst i
  subst j
  simp [Komorebi.PolynomialJointSystem.solvedJacobian, linearSystem, pderiv_X]

theorem linear_parameterJacobian (a : Fin (1 + 1) → 𝕜) :
    Komorebi.PolynomialJointSystem.parameterJacobian linearSystem a = 1 := by
  ext i j
  have hi : i = 0 := Fin.eq_zero i
  have hj : j = 0 := Fin.eq_zero j
  subst i
  subst j
  simp [Komorebi.PolynomialJointSystem.parameterJacobian, linearSystem, pderiv_X]

/-- The explicit global branch is analytic at every parameter, including p = 2. -/
theorem linear_analytic (t : Fin 1 → 𝕜) :
    AnalyticAt 𝕜 (fun u : Fin 1 → 𝕜 => -u) t := by
  exact analyticAt_id.neg

/-- The actual root equation forces precisely the explicit branch. -/
theorem linear_root_graph (y t : Fin 1 → 𝕜) :
    (∀ i, eval (join y t) (linearSystem i) = 0) ↔ y = -t := by
  constructor
  · intro h
    ext i
    have hi : i = 0 := Fin.eq_zero i
    subst i
    have h0 := h 0
    simp only [linearSystem, map_add, eval_X, join_solved, join_free] at h0
    exact eq_neg_of_add_eq_zero_left h0
  · intro h i
    subst y
    simp only [linearSystem, map_add, eval_X, join_solved, join_free, Pi.neg_apply,
      neg_add_cancel]

/-- The sign in the implicit derivative is negative. -/
theorem linear_strict_derivative (t : Fin 1 → 𝕜) :
    HasStrictFDerivAt (fun u : Fin 1 → 𝕜 => -u)
      (-ContinuousLinearMap.id 𝕜 (Fin 1 → 𝕜)) t := by
  exact (hasStrictFDerivAt_id t).neg

/-- In characteristic zero, the positive derivative is incompatible with this root graph. -/
theorem linear_derivative_not_positive [CharZero 𝕜] (t : Fin 1 → 𝕜) :
    ¬ HasStrictFDerivAt (fun u : Fin 1 → 𝕜 => -u)
      (ContinuousLinearMap.id 𝕜 (Fin 1 → 𝕜)) t := by
  intro h
  have hd := h.hasFDerivAt.unique (linear_strict_derivative t).hasFDerivAt
  have h1 := congrArg (fun L : (Fin 1 → 𝕜) →L[𝕜] (Fin 1 → 𝕜) => L (fun _ => 1) 0) hd
  norm_num at h1

/-- A nonlinear equation whose local branch is selected by the actual implicit theorem. -/
def quadraticSystem : Fin 1 → MvPolynomial (Fin (1 + 1)) 𝕜 :=
  fun _ => X (Fin.castAdd 1 0) + X (Fin.castAdd 1 0) ^ 2 + X (Fin.natAdd 1 0)

theorem quadratic_root :
    ∀ i, eval (0 : Fin (1 + 1) → 𝕜) (quadraticSystem i) = 0 := by
  intro i
  simp [quadraticSystem]

theorem quadratic_solvedJacobian :
    Komorebi.PolynomialJointSystem.solvedJacobian quadraticSystem
      (0 : Fin (1 + 1) → 𝕜) = 1 := by
  ext i j
  have hi : i = 0 := Fin.eq_zero i
  have hj : j = 0 := Fin.eq_zero j
  subst i
  subst j
  simp [Komorebi.PolynomialJointSystem.solvedJacobian, quadraticSystem, pderiv_X]

theorem quadratic_parameterJacobian :
    Komorebi.PolynomialJointSystem.parameterJacobian quadraticSystem
      (0 : Fin (1 + 1) → 𝕜) = 1 := by
  ext i j
  have hi : i = 0 := Fin.eq_zero i
  have hj : j = 0 := Fin.eq_zero j
  subst i
  subst j
  simp [Komorebi.PolynomialJointSystem.parameterJacobian, quadraticSystem, pderiv_X]

/-- A nonlinear invocation of the complete polynomial theorem, with the correct negative slope.
This control remains valid over every complete nontrivially normed field, including Q₂. -/
theorem quadratic_analytic_branch [CompleteSpace 𝕜] :
    ∃ (ψ : (Fin 1 → 𝕜) → (Fin 1 → 𝕜)) (U V : Set (Fin 1 → 𝕜)),
      IsOpen U ∧ IsOpen V ∧ (0 : Fin 1 → 𝕜) ∈ U ∧ (0 : Fin 1 → 𝕜) ∈ V ∧
      ψ 0 = 0 ∧ AnalyticOnNhd 𝕜 ψ U ∧ (∀ t ∈ U, ψ t ∈ V) ∧
      (∀ t ∈ U, ∀ y ∈ V,
        (∀ i, eval (join y t) (quadraticSystem i) = 0) ↔ y = ψ t) ∧
      HasStrictFDerivAt ψ (-ContinuousLinearMap.id 𝕜 (Fin 1 → 𝕜)) 0 := by
  have hroot : Komorebi.PolynomialAnalyticEvaluation.evalSystem quadraticSystem
      (0 : Fin (1 + 1) → 𝕜) = 0 := by
    ext i
    exact quadratic_root i
  have hunit : IsUnit (Komorebi.PolynomialJointSystem.solvedJacobian quadraticSystem
      (0 : Fin (1 + 1) → 𝕜)) := by
    rw [quadratic_solvedJacobian]
    exact isUnit_one
  obtain ⟨ψ, U, V, hU, hV, ht, hy, hψa, hψan, hψV, hgraph, hder⟩ :=
    Komorebi.PolynomialAnalyticImplicit.exists_analytic_implicit quadraticSystem
      (0 : Fin (1 + 1) → 𝕜) hroot hunit
  refine ⟨ψ, U, V, hU, hV, ht, hy, hψa, hψan, hψV, ?_, ?_⟩
  · intro t ht' y hy'
    simpa only [Komorebi.PolynomialAnalyticEvaluation.evalSystem,
      funext_iff, Pi.zero_apply] using hgraph t ht' y hy'
  · have heq : Komorebi.PolynomialAnalyticEvaluation.matrixCLM
        (-(1 : Matrix (Fin 1) (Fin 1) 𝕜)) =
        -ContinuousLinearMap.id 𝕜 (Fin 1 → 𝕜) := by
      ext v i
      simp [Matrix.neg_mulVec]
    have hz : freePart (0 : Fin (1 + 1) → 𝕜) = (0 : Fin 1 → 𝕜) := rfl
    rw [hz] at hder
    simpa only [quadratic_solvedJacobian, quadratic_parameterJacobian,
      inv_one, one_mul, heq] using hder

end Komorebi.PolynomialRegularityControls
