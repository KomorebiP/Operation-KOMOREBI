import NilpotentRightInverse
import NonlinearHenselTower

/-!
# Relative nonlinear Hensel capstone over nilpotent coefficient thickenings

This module combines two bridges:

1. a right inverse modulo a nilpotent scalar error corrects to an exact right
   inverse; and
2. an exact right inverse plus one-power Taylor remainder gain produces a
   compatible nonlinear Hensel tower and an exact solution once the coefficient
   power vanishes.

The result is suited to finite Artin quotients such as `O / pi^m`.  It does not
assert that a particular arithmetic deformation or Hecke presentation satisfies
its explicit hypotheses.
-/

namespace Komorebi.StrongArtin.RelativeNonlinearHenselCapstone

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.NilpotentRightInverse
open Komorebi.StrongArtin.NonlinearHenselStep
open Komorebi.StrongArtin.NonlinearHenselTower

noncomputable section

variable {R X W : Type*} [CommRing R]
  [AddCommGroup X] [Module R X]
  [AddCommGroup W] [Module R W]

/-- A nilpotent-error approximate right inverse produces compatible genuine
nonlinear approximations through every depth. -/
theorem exists_nonlinear_tower_of_nilpotent_approx_rightInverse
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (approxRightInv : W →ₗ[R] X) (E : Module.End R W)
    (happrox : J.comp approxRightInv = LinearMap.id + pi • E)
    (hpi : IsNilpotent pi)
    (hgain : RemainderRaisesOne pi F J)
    (x₀ : X) (hx₀ : PowDivisible pi 1 (F x₀)) :
    ∃ x : ℕ → X,
      x 0 = x₀ ∧
      (∀ n : ℕ, PowDivisible pi (n + 1) (F (x n))) ∧
      (∀ n : ℕ, PowDivisible pi (n + 1) (x (n + 1) - x n)) := by
  obtain ⟨rightInv, hRight⟩ :=
    exists_exact_rightInverse_of_scalar_nilpotent_error
      J approxRightInv pi E happrox hpi
  exact exists_approximation_tower pi F J rightInv hRight hgain x₀ hx₀

/--
**Finite nilpotent nonlinear Hensel theorem.** An initial solution modulo `pi`,
an augmented Jacobian with a right inverse modulo a nilpotent `pi`-error, and a
one-power Taylor remainder gain produce an exact solution of the nonlinear
equation.
-/
theorem exists_exact_solution_of_nilpotent_approx_rightInverse
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (approxRightInv : W →ₗ[R] X) (E : Module.End R W)
    (happrox : J.comp approxRightInv = LinearMap.id + pi • E)
    (hpi : IsNilpotent pi)
    (hgain : RemainderRaisesOne pi F J)
    (x₀ : X) (hx₀ : PowDivisible pi 1 (F x₀)) :
    ∃ x : X, F x = 0 := by
  obtain ⟨rightInv, hRight⟩ :=
    exists_exact_rightInverse_of_scalar_nilpotent_error
      J approxRightInv pi E happrox hpi
  obtain ⟨n, hn⟩ := hpi
  have hsucc : pi ^ (n + 1) = 0 := by
    rw [pow_succ, hn, zero_mul]
  exact exists_exact_solution_of_pow_eq_zero
    pi F J rightInv hRight hgain x₀ hx₀ n hsucc

/-- The same theorem stated with a prescribed nilpotence exponent. -/
theorem exists_exact_solution_of_finite_thickness
    (pi : R) (F : X → W) (J : X →ₗ[R] W)
    (approxRightInv : W →ₗ[R] X) (E : Module.End R W)
    (happrox : J.comp approxRightInv = LinearMap.id + pi • E)
    (n : ℕ) (hpi : pi ^ (n + 1) = 0)
    (hgain : RemainderRaisesOne pi F J)
    (x₀ : X) (hx₀ : PowDivisible pi 1 (F x₀)) :
    ∃ x : X, F x = 0 := by
  have hnil : IsNilpotent pi := ⟨n + 1, hpi⟩
  obtain ⟨rightInv, hRight⟩ :=
    exists_exact_rightInverse_of_scalar_nilpotent_error
      J approxRightInv pi E happrox hnil
  exact exists_exact_solution_of_pow_eq_zero
    pi F J rightInv hRight hgain x₀ hx₀ n hpi

end

end Komorebi.StrongArtin.RelativeNonlinearHenselCapstone

#print axioms Komorebi.StrongArtin.RelativeNonlinearHenselCapstone.exists_nonlinear_tower_of_nilpotent_approx_rightInverse
#print axioms Komorebi.StrongArtin.RelativeNonlinearHenselCapstone.exists_exact_solution_of_nilpotent_approx_rightInverse
#print axioms Komorebi.StrongArtin.RelativeNonlinearHenselCapstone.exists_exact_solution_of_finite_thickness
