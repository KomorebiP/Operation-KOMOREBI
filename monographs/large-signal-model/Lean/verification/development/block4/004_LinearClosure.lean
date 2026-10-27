import KomorebiLSM.PredictiveClosure
import Mathlib.Algebra.Module.Submodule.LinearMap
import Mathlib.Tactic.Abel

/-! Algebraic P7, with actual linear maps. Orthogonality is not needed;
idempotence is required precisely where a retained projection is used.
-/
set_option autoImplicit false
namespace Komorebi.LSM
universe u v
variable {R : Type u} [Ring R]
variable {X : Type v} [AddCommGroup X] [Module R X]

def unresolved (P : X →ₗ[R] X) : X →ₗ[R] X := LinearMap.id - P

def closureDefect (P L : X →ₗ[R] X) : X →ₗ[R] X :=
  P.comp (L.comp (unresolved P))

theorem unresolved_apply (P : X →ₗ[R] X) (x : X) :
    unresolved P x = x - P x := rfl

theorem unresolved_idempotent (P : X →ₗ[R] X) (idem : ∀ x, P (P x) = P x)
    (x : X) : unresolved P (unresolved P x) = unresolved P x := by
  simp only [unresolved_apply, map_sub, idem, sub_self, sub_zero]

theorem closure_defect_apply (P L : X →ₗ[R] X) (x : X) :
    closureDefect P L x = P (L x) - P (L (P x)) := by
  simp only [closureDefect, LinearMap.comp_apply, unresolved_apply, map_sub]

theorem retained_dynamics_split (P L : X →ₗ[R] X) (x : X) :
    P (L x) = P (L (P x)) + closureDefect P L x := by
  rw [closure_defect_apply]
  abel

theorem closure_iff_zero_defect (P L : X →ₗ[R] X)
    (idem : ∀ x, P (P x) = P x) :
    FiberConstant P (fun x => P (L x)) ↔ closureDefect P L = 0 := by
  constructor
  · intro h
    ext x
    simp only [LinearMap.zero_apply, closure_defect_apply]
    exact sub_eq_zero.mpr (h x (P x) (idem x).symm)
  · intro h x y hxy
    have hx := congrArg (fun f : X →ₗ[R] X => f x) h
    have hy := congrArg (fun f : X →ₗ[R] X => f y) h
    simp only [LinearMap.zero_apply, closure_defect_apply, sub_eq_zero] at hx hy
    exact hx.trans ((congrArg (fun z => P (L z)) hxy).trans hy.symm)

/-- The exact omitted return path PLQMP, with Q = I-P. -/
theorem composition_defect (P L M : X →ₗ[R] X)
    (idem : ∀ x, P (P x) = P x) :
    P.comp (L.comp (M.comp P)) -
        (P.comp (L.comp P)).comp (P.comp (M.comp P)) =
      P.comp (L.comp ((unresolved P).comp (M.comp P))) := by
  ext x
  simp only [LinearMap.sub_apply, LinearMap.comp_apply, unresolved_apply,
    map_sub, idem]

theorem zero_defect_exact_composition (P L M : X →ₗ[R] X)
    (idem : ∀ x, P (P x) = P x) (closed : closureDefect P L = 0) :
    P.comp (L.comp (M.comp P)) =
      (P.comp (L.comp P)).comp (P.comp (M.comp P)) := by
  apply sub_eq_zero.mp
  rw [composition_defect P L M idem]
  ext x
  have h := congrArg (fun f : X →ₗ[R] X => f (M (P x))) closed
  simpa only [closureDefect, LinearMap.comp_apply, LinearMap.zero_apply] using h

end Komorebi.LSM
