import GenericFiberSurvival
import Mathlib.RingTheory.Flat.TorsionFree

/-!
# Flatness forces generic-fibre survival

Flatness over the coefficient ring makes every coefficient nonzerodivisor act
regularly.  Consequently a nonzero special fibre cannot disappear after
localizing at powers of the uniformizer.

This is the module-theoretic support bridge needed by a relative patched module.
It does not prove flatness of any arithmetic patched module.
-/

namespace Komorebi.StrongArtin.FlatGenericFiberSurvival

open Komorebi.StrongArtin.GenericFiberSurvival
open scoped nonZeroDivisors

noncomputable section

variable {R M : Type*} [CommRing R]
  [AddCommGroup M] [Module R M]

/-- On a flat module, a ring nonzerodivisor acts regularly. -/
theorem uniformizer_smul_regular_of_flat
    [Module.Flat R M] {π : R} (hπ : π ∈ R⁰) :
    IsSMulRegular M π :=
  Module.Flat.isSMulRegular_of_nonZeroDivisors hπ

/-- The localization map of a flat module at a nonzerodivisor is injective. -/
theorem localizationMap_injective_of_flat
    [Module.Flat R M] {π : R} (hπ : π ∈ R⁰) :
    Function.Injective (localizationMap R M π) :=
  localizationMap_injective R M π
    (uniformizer_smul_regular_of_flat hπ)

/--
**Flat generic-survival capstone.** A flat module with nonzero special fibre has
nonzero generic fibre after inverting any ring nonzerodivisor.
-/
theorem genericFiber_nontrivial_of_flat_specialFiber
    [Module.Flat R M] {π : R} (hπ : π ∈ R⁰)
    [Nontrivial (specialFiber R M π)] :
    Nontrivial (genericFiber R M π) :=
  genericFiber_nontrivial_of_specialFiber R M π
    (uniformizer_smul_regular_of_flat hπ)

/-- Every class nonzero modulo `πM` survives in the generic fibre of a flat
module. -/
theorem localizationMap_ne_zero_of_flat_not_mem_piMultiple
    [Module.Flat R M] {π : R} (hπ : π ∈ R⁰) {m : M}
    (hm : m ∉ piMultiple R M π) :
    localizationMap R M π m ≠ 0 :=
  localizationMap_ne_zero_of_not_mem_piMultiple R M π
    (uniformizer_smul_regular_of_flat hπ) hm

end

end Komorebi.StrongArtin.FlatGenericFiberSurvival

#print axioms Komorebi.StrongArtin.FlatGenericFiberSurvival.localizationMap_injective_of_flat
#print axioms Komorebi.StrongArtin.FlatGenericFiberSurvival.genericFiber_nontrivial_of_flat_specialFiber
#print axioms Komorebi.StrongArtin.FlatGenericFiberSurvival.localizationMap_ne_zero_of_flat_not_mem_piMultiple
