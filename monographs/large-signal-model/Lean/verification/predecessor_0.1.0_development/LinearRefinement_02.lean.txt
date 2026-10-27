import KomorebiLSM.PredictiveClosure
import Mathlib.Algebra.Module.Submodule.LinearMap

/-! P22 linear bridge: a finer summary can be initialized from a coarse
summary exactly when the coarse kernel is contained in the fine kernel.
The range-codomain version supplies surjectivity rather than assuming an
unjustified access to the full ambient coefficient space. -/
set_option autoImplicit false
namespace Komorebi.LSM
universe u v w t
variable {R : Type u} [Ring R]
variable {X : Type v} [AddCommGroup X] [Module R X]
variable {Z : Type w} [AddCommGroup Z] [Module R Z]
variable {Y : Type t} [AddCommGroup Y] [Module R Y]

theorem linear_fiber_iff_kernel (gamma : X →ₗ[R] Z) (eta : X →ₗ[R] Y) :
    FiberConstant gamma eta ↔ (∀ x, gamma x = 0 → eta x = 0) := by
  constructor
  · intro h x hx
    simpa only [map_zero] using h x 0 (hx.trans gamma.map_zero.symm)
  · intro h x y hxy
    have hg : gamma (x-y) = 0 := by rw [map_sub, hxy, sub_self]
    have he := h (x-y) hg
    rwa [map_sub, sub_eq_zero] at he

theorem linear_factor_iff_kernel
    (gamma : X →ₗ[R] Z) (onto : ∀ z, ∃ x, gamma x = z) (eta : X →ₗ[R] Y) :
    (∃ J : Z →ₗ[R] Y, J.comp gamma = eta) ↔
      (∀ x, gamma x = 0 → eta x = 0) := by
  constructor
  · rintro ⟨J, hj⟩ x hx
    have h := congrArg (fun f : X →ₗ[R] Y => f x) hj
    simpa only [LinearMap.comp_apply, hx, map_zero] using h.symm
  · intro h
    obtain ⟨J, hj, _⟩ := (factor_exists_unique_iff gamma onto eta).mpr
      ((linear_fiber_iff_kernel gamma eta).mpr h)
    let f : Z →ₗ[R] Y :=
      { toFun := J
        map_add' := by
          intro z w
          obtain ⟨x, rfl⟩ := onto z
          obtain ⟨y, rfl⟩ := onto w
          rw [← gamma.map_add, hj, eta.map_add, hj, hj]
        map_smul' := by
          intro a z
          obtain ⟨x, rfl⟩ := onto z
          simp only [RingHom.id_apply]
          rw [← gamma.map_smul, hj, eta.map_smul, hj] }
    exact ⟨f, LinearMap.ext hj⟩

theorem linear_factor_unique
    (gamma : X →ₗ[R] Z) (onto : ∀ z, ∃ x, gamma x = z)
    (eta : X →ₗ[R] Y) (J K : Z →ₗ[R] Y)
    (hj : J.comp gamma = eta) (hk : K.comp gamma = eta) : J = K := by
  ext z
  obtain ⟨x, rfl⟩ := onto z
  have h := congrArg (fun f : X →ₗ[R] Y => f x) (hj.trans hk.symm)
  exact h

end Komorebi.LSM
