import MvPowerSeriesNilpotentSubstitution
import SurjectiveResidueHomPolynomialHensel

/-!
# Formal-power-series presentations over finite Artin thickenings

A finite system of multivariate formal power series over a principal nilpotent
thickening is evaluated canonically by Mathlib substitution.  Since nilpotent
coordinates kill every monomial above a finite total degree, the system reduces
exactly to the finite polynomial syntax covered by v0.20.  Surjectivity of the
residual Jacobian of that finite truncation therefore gives an exact solution of
the original formal system.
-/

namespace Komorebi.StrongArtin.FormalPowerSeriesSystemHensel

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ScalarPowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.SurjectiveResidueHomPolynomialHensel
open Komorebi.StrongArtin.MvPowerSeriesArtinTruncation
open Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution

noncomputable section

variable {R k ι κ : Type*} [CommRing R] [Field k]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]

/-- A finite coordinate system of formal power-series equations. -/
abbrev FormalSystem (ι κ R : Type*) := κ → MvPowerSeries ι R

/-- Canonical evaluation of a formal system by nilpotent substitution. -/
def formalEvalSystem (system : FormalSystem ι κ R) (x : ι → R) : κ → R :=
  fun j => formalEval (system j) x

/-- Total-degree truncation compiled into the v0.20 finite expression syntax. -/
def compileSystemAt (N : ℕ) (system : FormalSystem ι κ R) : System ι κ R :=
  fun j => compileAt N (system j)

omit [DecidableEq ι] [Fintype κ] [DecidableEq κ] in
@[simp] theorem eval_compileSystemAt_apply
    (N : ℕ) (system : FormalSystem ι κ R) (x : ι → R) (j : κ) :
    evalSystem (compileSystemAt N system) x j = artinEval N (system j) x := by
  simp [compileSystemAt, evalSystem]

omit [DecidableEq ι] [Fintype κ] [DecidableEq κ] in
/-- At nilpotent coordinates, the compiled truncation and canonical formal
substitution give exactly the same system value. -/
theorem eval_compileSystemAt_eq_formalEvalSystem
    (pi : R) (N : ℕ) (hpi : pi ^ N = 0)
    (system : FormalSystem ι κ R) (x : ι → R)
    (hx : ∀ i, PowDivisible pi 1 (x i)) :
    evalSystem (compileSystemAt N system) x = formalEvalSystem system x := by
  funext j
  rw [eval_compileSystemAt_apply]
  symm
  exact formalEval_eq_artinEval pi N hpi x hx (system j)

omit [Fintype ι] [DecidableEq ι] in
/-- Remaining in the residual fibre of a point whose coordinates lie in `(pi)`
preserves coordinatewise divisibility by `pi`. -/
theorem coordinatewise_powDivisible_of_sameResidual
    (pi : R) (x₀ x : ι → R)
    (hx₀ : ∀ i, PowDivisible pi 1 (x₀ i))
    (hres : SameResidual pi x₀ x) :
    ∀ i, PowDivisible pi 1 (x i) := by
  intro i
  have hdiff : PowDivisible pi 1 ((x - x₀) i) :=
    powDivisible_apply hres i
  have hsum := hdiff.add (hx₀ i)
  simpa using hsum

/--
**Formal-presentation Hensel theorem.** A finite formal power-series system over
a principal nilpotent thickening is completely controlled by one finite
truncation.  If its compiled truncation has a surjective residual Jacobian and
the base point solves the canonical formal equations modulo `pi`, then the
original untruncated formal equations have an exact solution in the same
residual fibre.
-/
theorem exists_exact_formal_solution_of_surjective_truncation_jacobian
    (pi : R) (N : ℕ) (hpiN : pi ^ N = 0)
    (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : FormalSystem ι κ R) (x₀ : ι → R)
    (hx₀coord : ∀ i, PowDivisible pi 1 (x₀ i))
    (hJ : Function.Surjective
      (matrixLinear
        ((jacobianMatrix (compileSystemAt N system) x₀).map q)))
    (hx₀eq : PowDivisible pi 1 (formalEvalSystem system x₀)) :
    ∃ x : ι → R,
      SameResidual pi x₀ x ∧ formalEvalSystem system x = 0 := by
  have hbase : PowDivisible pi 1
      (evalSystem (compileSystemAt N system) x₀) := by
    rw [eval_compileSystemAt_eq_formalEvalSystem pi N hpiN system x₀ hx₀coord]
    exact hx₀eq
  have hnil : IsNilpotent pi := ⟨N, hpiN⟩
  obtain ⟨x, hres, hpoly⟩ :=
    exists_exact_solution_of_surjective_residue_jacobian
      pi q hq hker (compileSystemAt N system) x₀ hJ hnil hbase
  have hxcoord : ∀ i, PowDivisible pi 1 (x i) :=
    coordinatewise_powDivisible_of_sameResidual pi x₀ x hx₀coord hres
  refine ⟨x, hres, ?_⟩
  rw [← eval_compileSystemAt_eq_formalEvalSystem pi N hpiN system x hxcoord]
  exact hpoly

/-- Centered version for completed local presentations whose variables are
chosen as deviations from the residual point. -/
theorem exists_exact_formal_solution_at_zero
    (pi : R) (N : ℕ) (hpiN : pi ^ N = 0)
    (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : FormalSystem ι κ R)
    (hJ : Function.Surjective
      (matrixLinear
        ((jacobianMatrix (compileSystemAt N system) (0 : ι → R)).map q)))
    (hconst : PowDivisible pi 1
      (formalEvalSystem system (0 : ι → R))) :
    ∃ x : ι → R,
      (∀ i, PowDivisible pi 1 (x i)) ∧
      formalEvalSystem system x = 0 := by
  have hzero : ∀ i, PowDivisible pi 1 ((0 : ι → R) i) := by
    intro i
    simp
  obtain ⟨x, hres, hsol⟩ :=
    exists_exact_formal_solution_of_surjective_truncation_jacobian
      pi N hpiN q hq hker system (0 : ι → R) hzero hJ hconst
  refine ⟨x, coordinatewise_powDivisible_of_sameResidual
      pi (0 : ι → R) x hzero hres, hsol⟩

end

end Komorebi.StrongArtin.FormalPowerSeriesSystemHensel

#print axioms Komorebi.StrongArtin.FormalPowerSeriesSystemHensel.exists_exact_formal_solution_of_surjective_truncation_jacobian
#print axioms Komorebi.StrongArtin.FormalPowerSeriesSystemHensel.exists_exact_formal_solution_at_zero
