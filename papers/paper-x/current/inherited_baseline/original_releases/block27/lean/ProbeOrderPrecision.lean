import PaperX.FiniteGroupAveraging
import Mathlib.RingTheory.DiscreteValuationRing.Basic

set_option autoImplicit false
namespace PaperX.OrderPrecision
open PaperX.RepresentationLimits PaperX.RepresentationClasses

variable {R Γ : Type*} [CommRing R] [IsDomain R]
  [IsDiscreteValuationRing R] [Group Γ] [Fintype Γ]

omit [Group Γ] in
/-- A nonzero group order has a finite uniformizer exponent.  The exponent is
chosen from the coefficient ring and group before any representations. -/
theorem exists_order_exponent (π : R) (hπ : Irreducible π)
    (hΓ : (Fintype.card Γ : R) ≠ 0) :
    ∃ e : ℕ, IsDiscreteValuationRing.addVal R (Fintype.card Γ : R) = e ∧
      (Fintype.card Γ : R) ∣ π^e := by
  obtain ⟨e, u, hu⟩ := IsDiscreteValuationRing.eq_unit_mul_pow_irreducible hΓ hπ
  refine ⟨e, ?_, ?_⟩
  · rw [hu, IsDiscreteValuationRing.addVal_def' u hπ]
  · refine ⟨(↑(u⁻¹) : R), ?_⟩
    rw [hu]
    rw [mul_right_comm, Units.mul_inv, one_mul]

omit [IsDomain R] [IsDiscreteValuationRing R] in
/-- Characteristic zero ensures that every finite group has a nonzero order
in the coefficient ring. -/
theorem order_ne_zero [CharZero R] : (Fintype.card Γ : R) ≠ 0 := by
  exact_mod_cast Fintype.card_ne_zero (α := Γ)

end PaperX.OrderPrecision
