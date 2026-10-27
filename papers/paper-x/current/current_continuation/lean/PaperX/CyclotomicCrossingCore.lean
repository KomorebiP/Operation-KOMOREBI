import Mathlib.FieldTheory.Galois.Basic
import Mathlib.GroupTheory.SpecificGroups.Cyclic.Basic
import Mathlib.GroupTheory.OrderOfElement

/-!
# The fixed-field step in cyclotomic field crossing

The auxiliary field and the automorphism are supplied. No auxiliary-field existence,
prime occurrence, or distribution assertion is included in these statements.
-/

set_option autoImplicit false

noncomputable section

namespace PaperX.CyclotomicCrossing

open IntermediateField

section Groups

variable {G H : Type*} [Group G] [Group H]

/-- Preservation of the order of one element makes the homomorphism faithful
on its cyclic subgroup. -/
theorem eq_one_of_mem_zpowers_of_map_eq_one (f : G →* H) (g : G)
    (horder : orderOf (f g) = orderOf g) {x : G}
    (hx : x ∈ Subgroup.zpowers g) (hfx : f x = 1) : x = 1 := by
  obtain ⟨n, rfl⟩ := Subgroup.mem_zpowers_iff.mp hx
  apply orderOf_dvd_iff_zpow_eq_one.mp
  rw [← horder]
  exact orderOf_dvd_iff_zpow_eq_one.mpr (by simpa only [map_zpow] using hfx)

/-- An order-preserving restriction is injective on the cyclic subgroup. -/
theorem injective_on_zpowers_of_orderOf_eq (f : G →* H) (g : G)
    (horder : orderOf (f g) = orderOf g) :
    Function.Injective (f.comp (Subgroup.zpowers g).subtype) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  apply le_antisymm
  · intro x hx
    apply Subgroup.mem_bot.mpr
    apply Subtype.ext
    exact eq_one_of_mem_zpowers_of_map_eq_one f g horder x.property hx
  · exact bot_le

end Groups

section Fields

variable {K T : Type*} [Field K] [Field T] [Algebra K T]
variable [FiniteDimensional K T] [IsGalois K T]

/-- If restriction to `A` preserves the order of `rho`, adjoining `A` to the
fixed field of `rho` recovers the entire ambient field. -/
theorem fixedField_zpowers_sup_eq_top
    (A : IntermediateField K T) [Normal K A] (rho : T ≃ₐ[K] T)
    (horder : orderOf (AlgEquiv.restrictNormalHom A rho) = orderOf rho) :
    fixedField (Subgroup.zpowers rho) ⊔ A = ⊤ := by
  have hinf : Subgroup.zpowers rho ⊓ A.fixingSubgroup = ⊥ := by
    apply le_antisymm
    · intro x hx
      apply Subgroup.mem_bot.mpr
      apply eq_one_of_mem_zpowers_of_map_eq_one (AlgEquiv.restrictNormalHom A)
        rho horder hx.1
      exact show x ∈ (AlgEquiv.restrictNormalHom A).ker from
        (A.restrictNormalHom_ker.symm ▸ hx.2)
    · exact bot_le
  calc
    fixedField (Subgroup.zpowers rho) ⊔ A =
        fixedField (fixingSubgroup (fixedField (Subgroup.zpowers rho) ⊔ A)) :=
      (IsGalois.fixedField_fixingSubgroup _).symm
    _ = ⊤ := by
      rw [fixingSubgroup_sup, fixingSubgroup_fixedField, hinf, fixedField_bot]

omit [FiniteDimensional K T] in
/-- The extension over the fixed field of one automorphism is Galois. -/
theorem isGalois_fixedField_zpowers (rho : T ≃ₐ[K] T) :
    IsGalois (fixedField (Subgroup.zpowers rho)) T := inferInstance

omit [IsGalois K T] in
/-- Its actual automorphism group is cyclic. -/
theorem isCyclic_fixedField_zpowers (rho : T ≃ₐ[K] T) :
    IsCyclic (T ≃ₐ[fixedField (Subgroup.zpowers rho)] T) := by
  exact isCyclic_of_surjective (subgroupEquivAlgEquiv (Subgroup.zpowers rho))
    (subgroupEquivAlgEquiv (Subgroup.zpowers rho)).surjective

omit [IsGalois K T] in
/-- The relative degree over the cyclic fixed field is the automorphism's order. -/
theorem finrank_fixedField_zpowers (rho : T ≃ₐ[K] T) :
    Module.finrank (fixedField (Subgroup.zpowers rho)) T = orderOf rho := by
  rw [finrank_fixedField_eq_card, Nat.card_zpowers]

/-- Any intermediate field containing both the fixed field and the auxiliary
field is already the entire ambient extension. -/
theorem eq_top_of_contains_crossing
    (A : IntermediateField K T) [Normal K A] (rho : T ≃ₐ[K] T)
    (horder : orderOf (AlgEquiv.restrictNormalHom A rho) = orderOf rho)
    (C : IntermediateField K T)
    (hE : fixedField (Subgroup.zpowers rho) ≤ C) (hA : A ≤ C) : C = ⊤ := by
  apply top_unique
  rw [← fixedField_zpowers_sup_eq_top A rho horder]
  exact sup_le hE hA

end Fields

end PaperX.CyclotomicCrossing
