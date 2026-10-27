import Mathlib.FieldTheory.Galois.Abelian
import Mathlib.GroupTheory.SpecificGroups.Cyclic
import Mathlib.NumberTheory.NumberField.Cyclotomic.Galois

/-! Construct a cyclic intermediate field of any degree dividing a finite
cyclic extension. The construction uses the fixed field of nth powers. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AuxiliaryCyclotomicDegree
open IntermediateField

section Cyclic
variable (K C : Type*) [Field K] [Field C] [Algebra K C]
  [FiniteDimensional K C] [IsGalois K C] [IsCyclic Gal(C/K)]

/-- Every divisor of the degree of a finite cyclic extension occurs as the
degree of an actual cyclic intermediate field. -/
theorem exists_cyclic_subfield (n : ℕ) (hn : n ∣ Module.finrank K C) :
    ∃ A : IntermediateField K C, Module.finrank K A = n ∧
      IsGalois K A ∧ IsCyclic Gal(A/K) := by
  let : CommGroup Gal(C/K) := IsCyclic.commGroup
  let H : Subgroup Gal(C/K) := (powMonoidHom n : Gal(C/K) →* Gal(C/K)).range
  let A : IntermediateField K C := fixedField H
  have hA : IsGalois K A := inferInstance
  have hcyc : IsCyclic Gal(A/K) :=
    isCyclic_of_surjective (AlgEquiv.restrictNormalHom A)
      (AlgEquiv.restrictNormalHom_surjective C)
  refine ⟨A, ?_, hA, hcyc⟩
  rw [IntermediateField.finrank_eq_fixingSubgroup_index,
    IntermediateField.fixingSubgroup_fixedField,
    IsCyclic.index_powMonoidHom_range, IsGalois.card_aut_eq_finrank,
    Nat.gcd_eq_right hn]

end Cyclic

section PrimeCyclotomic
variable (q : ℕ) [Fact q.Prime] (C : Type*) [Field C] [NumberField C]
  [IsCyclotomicExtension {q} ℚ C]

include q in
/-- The prime-conductor cyclotomic Galois group is cyclic. -/
theorem prime_cyclotomic_galois_isCyclic : IsCyclic Gal(C/ℚ) := by
  have : NeZero q := ⟨(Fact.out : q.Prime).ne_zero⟩
  exact isCyclic_of_injective (IsCyclotomicExtension.Rat.galEquivZMod q C).toMonoidHom
    (IsCyclotomicExtension.Rat.galEquivZMod q C).injective

/-- Prime conductors yield an actual cyclic subfield of each degree dividing q-1. -/
theorem exists_prime_cyclotomic_subfield (n : ℕ) (hn : n ∣ q - 1) :
    ∃ A : IntermediateField ℚ C, Module.finrank ℚ A = n ∧
      IsGalois ℚ A ∧ IsCyclic Gal(A/ℚ) := by
  have : NeZero q := ⟨(Fact.out : q.Prime).ne_zero⟩
  have : IsCyclic Gal(C/ℚ) := prime_cyclotomic_galois_isCyclic q C
  have : IsGalois ℚ C := IsCyclotomicExtension.isGalois {q} ℚ C
  apply exists_cyclic_subfield ℚ C n
  simpa only [IsCyclotomicExtension.Rat.finrank q, Nat.totient_prime (Fact.out : q.Prime)]
    using hn

end PrimeCyclotomic
end PaperX.AuxiliaryCyclotomicDegree
