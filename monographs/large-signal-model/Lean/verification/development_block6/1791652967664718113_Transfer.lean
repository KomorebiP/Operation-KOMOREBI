import Mathlib.Algebra.Module.Submodule.LinearMap
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma

/-! P4 with actual linear maps between possibly different spaces.
Completeness and the intermediate idempotence assumptions are explicit.
No orthogonality or finite-dimensionality is needed for these identities.
-/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM
universe u v w t
variable {R : Type u} [Semiring R]
variable {X : Type v} [AddCommMonoid X] [Module R X]
variable {Y : Type w} [AddCommMonoid Y] [Module R Y]
variable {Z : Type t} [AddCommMonoid Z] [Module R Z]

/-- A typed input-to-output transfer block. -/
def transferBlock (P : X →ₗ[R] X) (L : X →ₗ[R] Y) (Q : Y →ₗ[R] Y) :
    X →ₗ[R] Y := Q.comp (L.comp P)

theorem transfer_reconstruction {I J : Type*} [Fintype I] [Fintype J]
    (P : I → X →ₗ[R] X) (Q : J → Y →ₗ[R] Y) (L : X →ₗ[R] Y)
    (hP : ∑ i, P i = LinearMap.id) (hQ : ∑ j, Q j = LinearMap.id) :
    L = ∑ j, ∑ i, transferBlock (P i) L (Q j) := by
  calc
    L = (∑ j, Q j).comp (L.comp (∑ i, P i)) := by rw [hP, hQ]; simp
    _ = _ := by
      ext x
      simp only [transferBlock, LinearMap.comp_apply, LinearMap.sum_apply, map_sum]
      exact Finset.sum_comm

theorem transfer_refinement {I J : Type*} [Fintype I] [Fintype J]
    (P : X →ₗ[R] X) (Q : Y →ₗ[R] Y)
    (p : I → X →ₗ[R] X) (q : J → Y →ₗ[R] Y) (L : X →ₗ[R] Y)
    (hp : P = ∑ i, p i) (hq : Q = ∑ j, q j) :
    transferBlock P L Q = ∑ j, ∑ i, transferBlock (p i) L (q j) := by
  rw [hp, hq]
  ext x
  simp only [transferBlock, LinearMap.comp_apply, LinearMap.sum_apply, map_sum]
  exact Finset.sum_comm

theorem transfer_composition {J : Type*} [Fintype J]
    (P : X →ₗ[R] X) (Q : J → Y →ₗ[R] Y) (S : Z →ₗ[R] Z)
    (L : X →ₗ[R] Y) (M : Y →ₗ[R] Z)
    (hQ : ∑ j, Q j = LinearMap.id)
    (idem : ∀ j y, Q j (Q j y) = Q j y) :
    transferBlock P (M.comp L) S =
      ∑ j, (transferBlock (Q j) M S).comp (transferBlock P L (Q j)) := by
  ext x
  simp only [transferBlock, LinearMap.comp_apply, LinearMap.sum_apply, idem]
  have h (y : Y) : (∑ j, Q j y) = y := by
    simpa only [LinearMap.sum_apply, LinearMap.id_apply] using
      congrArg (fun f : Y →ₗ[R] Y => f y) hQ
  rw [← map_sum, ← map_sum, h]

/-- One layer of complete refinement preserves the operator sum.
This is not the full tree/antichain or Pythagoras theorem of P3. -/
theorem refinement_sum {I J : Type*} [Fintype I] [Fintype J]
    (P : I → X →ₗ[R] X) (p : I → J → X →ₗ[R] X)
    (complete : ∑ i, P i = LinearMap.id)
    (split : ∀ i, ∑ j, p i j = P i) :
    (∑ i, ∑ j, p i j) = LinearMap.id := by
  simp only [split, complete]

theorem packet_reconstruction {I : Type*} [Fintype I]
    (P : I → X →ₗ[R] X) (complete : ∑ i, P i = LinearMap.id) (x : X) :
    (∑ i, P i x) = x := by
  simpa only [LinearMap.sum_apply, LinearMap.id_apply] using
    congrArg (fun f : X →ₗ[R] X => f x) complete

end Komorebi.LSM
