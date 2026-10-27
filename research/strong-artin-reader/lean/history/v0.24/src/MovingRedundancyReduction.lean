import VariableJacobianHensel
import Mathlib.LinearAlgebra.Prod

/-! A noncircular repair for variable-dependent redundant equations. If the
extra equations are known exact linear combinations of a retained subsystem,
a state-dependent invertible triangular row operation removes them. No
assertion is made that arbitrary first-jet syzygies have this exact form. -/

namespace Komorebi.StrongArtin.MovingRedundancyReduction

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel

noncomputable section

variable {R X W Z : Type*} [CommRing R]
  [AddCommGroup W] [Module R W]
  [AddCommGroup Z] [Module R Z]

/-- An invertible row operation subtracting the known redundant equation block. -/
def straighten (B : W →ₗ[R] Z) : (W × Z) ≃ₗ[R] (W × Z) where
  toFun v := (v.1, v.2 - B v.1)
  invFun v := (v.1, v.2 + B v.1)
  left_inv v := by simp
  right_inv v := by simp
  map_add' v w := by
    apply Prod.ext
    · rfl
    · simp [sub_eq_add_neg, add_assoc, add_left_comm, add_comm]
  map_smul' a v := by
    apply Prod.ext
    · rfl
    · simp [smul_sub]

/-- A nonlinear system together with a block of genuinely redundant equations. -/
def redundantGraph (F : X → W) (B : X → (W →ₗ[R] Z)) (x : X) : W × Z :=
  (F x, B x (F x))

@[simp] theorem straighten_redundantGraph
    (F : X → W) (B : X → (W →ₗ[R] Z)) (x : X) :
    straighten (B x) (redundantGraph F B x) = (F x, 0) := by
  simp [straighten, redundantGraph]

/-- Variable-dependent redundant equations have exactly the same zero set. -/
theorem redundantGraph_eq_zero_iff
    (F : X → W) (B : X → (W →ₗ[R] Z)) (x : X) :
    redundantGraph F B x = 0 ↔ F x = 0 := by
  constructor
  · exact fun h => congrArg Prod.fst h
  · intro h
    simp [redundantGraph, h]

variable [AddCommGroup X] [Module R X]

/-- The derivative block from varying redundancy is retained, not discarded. -/
theorem straighten_derivative_blocks
    (B : W →ₗ[R] Z) (D : X →ₗ[R] W) (E : X →ₗ[R] Z) :
    (straighten B).toLinearMap.comp (D.prod (B.comp D + E)) = D.prod E := by
  apply LinearMap.ext
  intro x
  apply Prod.ext
  · rfl
  · simp [straighten]

/-- When the extra derivative block vanishes, the tangent kernels agree. -/
theorem ker_graph_derivative (B : W →ₗ[R] Z) (D : X →ₗ[R] W) :
    LinearMap.ker (D.prod (B.comp D)) = LinearMap.ker D := by
  ext x
  change (D x, B (D x)) = (0, 0) ↔ D x = 0
  constructor
  · exact fun h => congrArg Prod.fst h
  · intro h
    simp [h]

/-- Nonlinear Hensel lifting of the retained subsystem solves all exactly
redundant equations, even when their coefficients vary with the state. -/
theorem exists_exact_solution_with_moving_redundancy
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (rightInv : W →ₗ[R] X) (E : X → Module.End R W) (x0 : X)
    (B : X → (W →ₗ[R] Z))
    (happrox : ∀ x, SameResidual pi x0 x →
      (D x).comp rightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    (hres : PowDivisible pi 1 (F x0)) :
    ∃ x, SameResidual pi x0 x ∧ redundantGraph F B x = 0 := by
  obtain ⟨x, hx, hroot⟩ := exists_exact_solution_variableJacobian
    pi F D rightInv E x0 happrox hpi hgain hres
  exact ⟨x, hx, (redundantGraph_eq_zero_iff F B x).mpr hroot⟩

end
end Komorebi.StrongArtin.MovingRedundancyReduction

#print axioms Komorebi.StrongArtin.MovingRedundancyReduction.straighten_redundantGraph
#print axioms Komorebi.StrongArtin.MovingRedundancyReduction.straighten_derivative_blocks
#print axioms Komorebi.StrongArtin.MovingRedundancyReduction.exists_exact_solution_with_moving_redundancy
