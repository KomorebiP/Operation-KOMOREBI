import Mathlib.GroupTheory.Finiteness
import Mathlib.Algebra.Group.Subgroup.Order
import Mathlib.GroupTheory.SpecificGroups.Cyclic
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.Ring

/-! # Finitely generated rational subgroups are cyclic -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries

/-- A finite family of rationals lies in one actual cyclic rational lattice,
using the product of its denominators as a common denominator. -/
theorem finite_rationals_common_cyclic_lattice (s : Finset ℚ) :
    ∃ d : ℕ, 0 < d ∧ (↑s : Set ℚ) ⊆ AddSubgroup.zmultiples (1 / (d : ℚ)) := by
  classical
  let d : ℕ := ∏ q ∈ s, q.den
  have hdpos : 0 < d := Finset.prod_pos (fun q _ => q.den_pos)
  have hd : (d : ℚ) ≠ 0 := by exact_mod_cast hdpos.ne'
  refine ⟨d, hdpos, ?_⟩
  intro q hq
  have hden : q.den ∣ d := Finset.dvd_prod_of_mem (fun q : ℚ => q.den) hq
  obtain ⟨k, hk⟩ := hden
  apply AddSubgroup.mem_zmultiples_iff.mpr
  refine ⟨q.num * (k : ℤ), ?_⟩
  rw [zsmul_eq_mul]
  push_cast
  rw [mul_one_div]
  apply (div_eq_iff hd).mpr
  rw [hk, Nat.cast_mul, ← Rat.den_mul_eq_num q]
  ring

/-- Every finitely generated additive subgroup of the actual rational numbers
is contained in a cyclic rational lattice, hence is itself cyclic. -/
theorem rational_subgroup_fg_isAddCyclic (H : AddSubgroup ℚ) (hH : H.FG) :
    IsAddCyclic H := by
  obtain ⟨s, hs⟩ := hH
  obtain ⟨d, _, hd⟩ := finite_rationals_common_cyclic_lattice s
  have hle : H ≤ AddSubgroup.zmultiples (1 / (d : ℚ)) := by
    rw [← hs]
    exact (AddSubgroup.closure_le _).mpr hd
  exact AddSubgroup.isAddCyclic_of_le hle

/-- Typeclass formulation for the rational image of a finitely generated group. -/
theorem rational_fg_isAddCyclic (H : AddSubgroup ℚ) [AddGroup.FG H] : IsAddCyclic H :=
  rational_subgroup_fg_isAddCyclic H ((AddGroup.fg_iff_addSubgroup_fg H).mp inferInstance)

/-- A nonzero finitely generated rational subgroup is additively isomorphic
to the integers. No generator of the surrounding rational vector space is assumed. -/
theorem rational_fg_equiv_int (H : AddSubgroup ℚ) [AddGroup.FG H] (hH : H ≠ ⊥) :
    Nonempty (H ≃+ ℤ) := by
  have : IsAddCyclic H := rational_fg_isAddCyclic H
  have : Nontrivial H := H.nontrivial_iff_ne_bot.mpr hH
  obtain ⟨e⟩ := (LinearOrderedAddCommGroup.isAddCyclic_iff_nonempty_equiv_int).mp
    (inferInstance : IsAddCyclic H)
  exact ⟨e.toAddEquiv⟩

/-- A generator and the exact integer-multiple enumeration are available even
in the zero subgroup case. -/
theorem rational_fg_generator (H : AddSubgroup ℚ) [AddGroup.FG H] :
    ∃ q : H, Function.Surjective (fun n : ℤ => n • q) :=
  (rational_fg_isAddCyclic H).exists_zsmul_surjective

end RealizationBoundaries
