import KomorebiLSM.Transfer
import Mathlib.LinearAlgebra.Multilinear.Basic

/-! P5. All ordered cross-packet interactions of each multilinear term
are retained; no independent-packet approximation is inserted. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM
universe u v w
variable {R : Type u} [CommSemiring R]
variable {X : Type v} [AddCommMonoid X] [Module R X]
variable {Y : Type w} [AddCommMonoid Y] [Module R Y]

theorem multilinear_packet_expansion {I : Type*} [Fintype I] (m : ℕ)
    (P : I → X →ₗ[R] X) (complete : ∑ i, P i = LinearMap.id)
    (B : MultilinearMap R (fun _ : Fin m => X) Y) (x : X) :
    B (fun _ => x) = ∑ f : Fin m → I, B (fun k => P (f k) x) := by
  classical
  have h := B.map_sum (fun (_ : Fin m) (i : I) => P i x)
  simpa only [packet_reconstruction P complete x] using h

theorem polynomial_packet_expansion {I : Type*} [Fintype I] (n : ℕ)
    (P : I → X →ₗ[R] X) (complete : ∑ i, P i = LinearMap.id)
    (B : (m : Fin n) → MultilinearMap R (fun _ : Fin (m.val + 1) => X) Y)
    (Q : Y →ₗ[R] Y) (b : Y) (x : X) :
    Q (b + ∑ m, B m (fun _ => x)) =
      Q b + ∑ m : Fin n, ∑ f : Fin (m.val + 1) → I,
        Q (B m (fun k => P (f k) x)) := by
  classical
  rw [map_add, map_sum]
  congr 1
  apply Finset.sum_congr rfl
  intro m _
  rw [multilinear_packet_expansion (m.val + 1) P complete (B m) x, map_sum]

end Komorebi.LSM
