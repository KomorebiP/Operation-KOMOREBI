import SplitTargetFiltration
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic.Ring

/-! Exact boundary tests. Residual syzygies are not necessarily constant
nonlinear identities. Ambient divisibility need not be internal divisibility
in a nonsplit compatible submodule. -/

namespace Komorebi.StrongArtin.SyzygyBoundaryExamples

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.SplitTargetFiltration

section Nonlinear
variable {R : Type*} [CommRing R]

/-- The second equation is genuinely redundant, but with variable coefficient x. -/
def redundantSystem (x : R) : R × R := (x, x * x)

def redundantJacobian (x : R) : R →ₗ[R] (R × R) :=
  (LinearMap.id : R →ₗ[R] R).prod ((2 * x) • (LinearMap.id : R →ₗ[R] R))

theorem redundantSystem_exact_syzygy (x : R) :
    -x * (redundantSystem x).1 + (redundantSystem x).2 = 0 := by
  simp [redundantSystem]

/-- The actual nonlinear remainder, computed without approximation. -/
theorem redundantSystem_taylor (x delta : R) :
    redundantSystem (x + delta) - redundantSystem x - redundantJacobian x delta =
      (0, delta * delta) := by
  apply Prod.ext
  · simp [redundantSystem, redundantJacobian]
  · simp [redundantSystem, redundantJacobian]
    ring

/-- At the origin the derivative lies entirely in the horizontal target. -/
theorem redundantJacobian_zero (delta : R) :
    redundantJacobian (0 : R) delta = (delta, 0) := by
  simp [redundantJacobian]

end Nonlinear

/-- The residual syzygy (0,1) fails as a constant nonlinear identity already
on the residual fibre x=2 in Z/8Z. The exact syzygy is (-x,1). -/
theorem nonlinear_error_escapes_residual_target :
    (redundantSystem (2 : ZMod 8)).2 = 4 ∧
    (redundantSystem (2 : ZMod 8)).2 ≠ 0 := by
  decide

/-- Even the Taylor remainder can leave that same horizontal target. -/
theorem nonlinear_remainder_escapes_residual_target :
    (redundantSystem (0 + 2 : ZMod 8) - redundantSystem 0 -
      redundantJacobian 0 2).2 ≠ 0 := by
  rw [redundantSystem_taylor]
  decide

/-- The submodule 2R inside R=Z/4Z, expressed as the kernel of multiplication by 2. -/
def twoTorsion : Submodule (ZMod 4) (ZMod 4) :=
  LinearMap.ker ((2 : ZMod 4) • (LinearMap.id : ZMod 4 →ₗ[ZMod 4] ZMod 4))

def twoInTarget : twoTorsion := ⟨2, by
  change (2 : ZMod 4) * 2 = 0
  decide⟩

theorem two_is_ambient_divisible :
    PowDivisible (2 : ZMod 4) 1 ((twoInTarget : twoTorsion) : ZMod 4) := by
  exact ⟨1, by decide⟩

/-- 2 belongs to C and to 2R, but does not belong to 2C. -/
theorem two_not_internally_divisible :
    ¬ PowDivisible (2 : ZMod 4) 1 twoInTarget := by
  rintro ⟨y, hy⟩
  have hzero : (2 : ZMod 4) * (y : ZMod 4) = 0 := by
    exact y.property
  have htwo : (2 : ZMod 4) * (y : ZMod 4) = 2 := by
    have h := congrArg (fun z : twoTorsion => (z : ZMod 4)) hy
    simpa [twoInTarget] using h
  have hbad : (2 : ZMod 4) = 0 := htwo.symm.trans hzero
  exact (by decide : (2 : ZMod 4) ≠ 0) hbad

/-- In particular, this compatible submodule has no integral retraction. -/
theorem twoTorsion_has_no_retraction : ¬ Nonempty (Retraction twoTorsion) := by
  rintro ⟨r⟩
  exact two_not_internally_divisible
    ((r.powDivisible_iff 2 1 twoInTarget).mpr two_is_ambient_divisible)

end Komorebi.StrongArtin.SyzygyBoundaryExamples

#print axioms Komorebi.StrongArtin.SyzygyBoundaryExamples.redundantSystem_taylor
#print axioms Komorebi.StrongArtin.SyzygyBoundaryExamples.nonlinear_error_escapes_residual_target
#print axioms Komorebi.StrongArtin.SyzygyBoundaryExamples.two_not_internally_divisible
#print axioms Komorebi.StrongArtin.SyzygyBoundaryExamples.twoTorsion_has_no_retraction
