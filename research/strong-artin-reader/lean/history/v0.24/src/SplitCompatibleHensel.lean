import SplitTargetFiltration
import VariableJacobianHensel

/-! Nonlinear lifting into a split compatible equation target. The equation
need only take values in the target on the residual fibre. This hypothesis
cannot be inferred from the residual Jacobian alone. -/

namespace Komorebi.StrongArtin.SplitCompatibleHensel

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.SplitTargetFiltration

noncomputable section

variable {R X W : Type*} [CommRing R]
  [AddCommGroup X] [Module R X]
  [AddCommGroup W] [Module R W]

/-- Linear projection commutes with the exact first-order remainder. -/
theorem projected_variableRemainder
    (C : Submodule R W) (r : Retraction C)
    (F : X → W) (D : X → (X →ₗ[R] W)) (x delta : X) :
    variableRemainder (fun z => r.project (F z))
      (fun z => r.project.comp (D z)) x delta =
    r.project (variableRemainder F D x delta) := by
  simp [variableRemainder]

/-- Ambient Taylor gain gives Taylor gain in the projected module. -/
theorem projected_remainder_raises_one
    (C : Submodule R W) (r : Retraction C)
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (hgain : VariableRemainderRaisesOne pi F D) :
    VariableRemainderRaisesOne pi
      (fun z => r.project (F z)) (fun z => r.project.comp (D z)) := by
  intro n hn x delta hdelta
  rw [projected_variableRemainder]
  exact (hgain n hn x delta hdelta).map r.project

/-- A compatible equation can be lifted without surjectivity onto its redundant
ambient codomain. The right inverse is required only after projection to C.
An actual integral retraction and nonlinear compatibility are explicit inputs. -/
theorem exists_exact_solution_in_split_compatible_target
    (C : Submodule R W) (r : Retraction C)
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (rightInv : C →ₗ[R] X) (E : X → Module.End R C) (x0 : X)
    (hcompatible : ∀ x, SameResidual pi x0 x → F x ∈ C)
    (happrox : ∀ x, SameResidual pi x0 x →
      (r.project.comp (D x)).comp rightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    (hres : PowDivisible pi 1 (F x0)) :
    ∃ x, SameResidual pi x0 x ∧ F x = 0 := by
  obtain ⟨x, hx, hroot⟩ := exists_exact_solution_variableJacobian
    pi (fun z => r.project (F z)) (fun z => r.project.comp (D z))
    rightInv E x0 happrox hpi
    (projected_remainder_raises_one C r pi F D hgain)
    (hres.map r.project)
  exact ⟨x, hx, (r.project_eq_zero_iff (F x) (hcompatible x hx)).mp hroot⟩

/-- The same construction provides an ambient compatible approximation tower. -/
theorem exists_split_compatible_approximation_tower
    (C : Submodule R W) (r : Retraction C)
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (rightInv : C →ₗ[R] X) (E : X → Module.End R C) (x0 : X)
    (hcompatible : ∀ x, SameResidual pi x0 x → F x ∈ C)
    (happrox : ∀ x, SameResidual pi x0 x →
      (r.project.comp (D x)).comp rightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    (hres : PowDivisible pi 1 (F x0)) :
    ∃ x : ℕ → X,
      x 0 = x0 ∧
      (∀ n, SameResidual pi x0 (x n)) ∧
      (∀ n, PowDivisible pi (n + 1) (F (x n))) ∧
      (∀ n, PowDivisible pi (n + 1) (x (n + 1) - x n)) := by
  obtain ⟨x, h0, hx, herror, hstep⟩ := exists_variable_approximation_tower
    pi (fun z => r.project (F z)) (fun z => r.project.comp (D z))
    rightInv E x0 happrox hpi
    (projected_remainder_raises_one C r pi F D hgain)
    (hres.map r.project)
  refine ⟨x, h0, hx, ?_, hstep⟩
  intro n
  have h := (herror n).map C.subtype
  have heq : ((r.project (F (x n)) : C) : W) = F (x n) :=
    congrArg (fun z : C => (z : W))
      (r.project_coe ⟨F (x n), hcompatible (x n) (hx n)⟩)
  simpa only [LinearMap.comp_apply, Submodule.subtype_apply, heq] using h

/-- Exact (not merely residual) linear relations supply target compatibility. -/
theorem exists_exact_solution_of_split_relation_kernel
    {Z : Type*} [AddCommGroup Z] [Module R Z]
    (relation : W →ₗ[R] Z) (r : Retraction (LinearMap.ker relation))
    (pi : R) (F : X → W) (D : X → (X →ₗ[R] W))
    (rightInv : LinearMap.ker relation →ₗ[R] X)
    (E : X → Module.End R (LinearMap.ker relation)) (x0 : X)
    (hrelations : ∀ x, SameResidual pi x0 x → relation (F x) = 0)
    (happrox : ∀ x, SameResidual pi x0 x →
      (r.project.comp (D x)).comp rightInv = LinearMap.id + pi • E x)
    (hpi : IsNilpotent pi)
    (hgain : VariableRemainderRaisesOne pi F D)
    (hres : PowDivisible pi 1 (F x0)) :
    ∃ x, SameResidual pi x0 x ∧ F x = 0 :=
  exists_exact_solution_in_split_compatible_target
    (LinearMap.ker relation) r pi F D rightInv E x0
    (fun x hx => LinearMap.mem_ker.mpr (hrelations x hx)) happrox hpi hgain hres

end
end Komorebi.StrongArtin.SplitCompatibleHensel

#print axioms Komorebi.StrongArtin.SplitCompatibleHensel.exists_exact_solution_in_split_compatible_target
#print axioms Komorebi.StrongArtin.SplitCompatibleHensel.exists_split_compatible_approximation_tower
#print axioms Komorebi.StrongArtin.SplitCompatibleHensel.exists_exact_solution_of_split_relation_kernel
