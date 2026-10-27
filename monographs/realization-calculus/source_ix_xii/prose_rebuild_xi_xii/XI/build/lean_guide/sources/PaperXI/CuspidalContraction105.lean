import Mathlib.RepresentationTheory.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-! Finite cuspidality excludes a map on which an actual radical contracts to
identity. The averaging sum and its vanishing are derived, not supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CuspidalContraction105
open Representation
variable {k U V W : Type*} [Field k]
  [Group U] [Fintype U] [AddCommGroup V] [Module k V]
  [AddCommGroup W] [Module k W]

def NoFixed (ρ : Representation k U V) : Prop :=
  ∀ v : V, (∀ u : U, ρ u v = v) → v = 0

theorem sum_fixed (ρ : Representation k U V) (v : V) (u : U) :
    ρ u (∑ x : U, ρ x v) = ∑ x : U, ρ x v := by
  simp only [map_sum, ← Module.End.mul_apply, ← map_mul]
  exact Fintype.sum_equiv (Equiv.mulLeft u) (fun x => ρ (u * x) v)
    (fun x => ρ x v) (fun _ => rfl)

theorem sum_eq_zero (ρ : Representation k U V) (hρ : NoFixed ρ) (v : V) :
    (∑ x : U, ρ x v) = 0 := hρ _ (sum_fixed ρ v)

theorem map_eq_zero [CharZero k] (ρ : Representation k U V) (hρ : NoFixed ρ)
    (T : V →ₗ[k] W) (hT : ∀ u v, T (ρ u v) = T v) : T = 0 := by
  ext v
  have hsum := congrArg T (sum_eq_zero ρ hρ v)
  simp only [map_sum, hT, Finset.sum_const, Finset.card_univ, map_zero] at hsum
  have hcard : (Fintype.card U : k) ≠ 0 :=
    Nat.cast_ne_zero.mpr Fintype.card_ne_zero
  have hmul : (Fintype.card U : k) • T v = 0 := by
    simpa only [Nat.cast_smul_eq_nsmul] using hsum
  exact (smul_eq_zero.mp hmul).resolve_left hcard

end PaperXI.CuspidalContraction105
