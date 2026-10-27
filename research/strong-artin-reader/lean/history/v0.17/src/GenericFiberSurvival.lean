import Mathlib.Algebra.Module.LocalizedModule.Basic
import Mathlib.LinearAlgebra.Quotient.Basic

/-!
# Generic-fibre survival from residual occurrence

This module isolates the commutative-algebra bridge needed by the relative
Strong Artin support route.  A nonzero special fibre proves that the module
itself is nonzero.  If multiplication by the uniformizer is injective, then
localization at its powers is injective, so the generic fibre is nonzero.

No automorphic occurrence, flatness, Cohen--Macaulay property, or patching
statement is asserted here.
-/

namespace Komorebi.StrongArtin.GenericFiberSurvival

section

variable (R M : Type*) [CommRing R] [AddCommGroup M] [Module R M]

/-- Multiplication by one scalar, regarded as an `R`-linear endomorphism. -/
def scalarMulLinear (π : R) : M →ₗ[R] M where
  toFun m := π • m
  map_add' m n := smul_add π m n
  map_smul' r m := by
    simp only [RingHom.id_apply, smul_smul, mul_comm]

/-- The submodule `π M`. -/
def piMultiple (π : R) : Submodule R M :=
  (scalarMulLinear R M π).range

/-- The special fibre `M / π M`. -/
abbrev specialFiber (π : R) := M ⧸ piMultiple R M π

/-- The localization of `M` at the powers of `π`. -/
abbrev genericFiber (π : R) := LocalizedModule (Submonoid.powers π) M

/-- The canonical map from a module to its localization at powers of `π`. -/
noncomputable def localizationMap (π : R) : M →ₗ[R] genericFiber R M π :=
  LocalizedModule.mkLinearMap (Submonoid.powers π) M

/-- Regularity of `π` propagates to every element of the powers submonoid. -/
theorem powers_smul_regular (π : R) (hπ : IsSMulRegular M π) :
    ∀ c : Submonoid.powers π, IsSMulRegular M c := by
  intro c
  rcases (Submonoid.mem_powers_iff c.1 π).mp c.2 with ⟨n, hn⟩
  show IsSMulRegular M c.1
  exact hn ▸ hπ.pow n

/-- If `π` is regular on `M`, the canonical localization map is injective. -/
theorem localizationMap_injective (π : R) (hπ : IsSMulRegular M π) :
    Function.Injective (localizationMap R M π) := by
  unfold localizationMap
  exact
    (IsLocalizedModule.injective_iff_isRegular (Submonoid.powers π)
      (LocalizedModule.mkLinearMap (Submonoid.powers π) M)).2
      (powers_smul_regular R M π hπ)

/-- A nonzero special fibre forces the original module to be nonzero. -/
theorem module_nontrivial_of_specialFiber (π : R)
    [Nontrivial (specialFiber R M π)] : Nontrivial M :=
  (Submodule.mkQ_surjective (piMultiple R M π)).nontrivial

/-- A nonzero module with regular `π` has nonzero generic fibre. -/
theorem genericFiber_nontrivial (π : R) [Nontrivial M]
    (hπ : IsSMulRegular M π) : Nontrivial (genericFiber R M π) :=
  (localizationMap_injective R M π hπ).nontrivial

/--
A nonzero special fibre together with `π`-torsion-freeness forces a nonzero
generic fibre.
-/
theorem genericFiber_nontrivial_of_specialFiber (π : R)
    [Nontrivial (specialFiber R M π)]
    (hπ : IsSMulRegular M π) : Nontrivial (genericFiber R M π) := by
  have hM : Nontrivial M := module_nontrivial_of_specialFiber R M π
  exact @genericFiber_nontrivial R M _ _ _ π hM hπ

/-- Any element nonzero modulo `π M` remains nonzero in the generic fibre. -/
theorem localizationMap_ne_zero_of_not_mem_piMultiple (π : R)
    (hπ : IsSMulRegular M π) {m : M}
    (hm : m ∉ piMultiple R M π) : localizationMap R M π m ≠ 0 := by
  intro hz
  have hm0 : m = 0 := localizationMap_injective R M π hπ (by simpa using hz)
  subst m
  exact hm (Submodule.zero_mem _)

end

end Komorebi.StrongArtin.GenericFiberSurvival

#print axioms Komorebi.StrongArtin.GenericFiberSurvival.localizationMap_injective
#print axioms Komorebi.StrongArtin.GenericFiberSurvival.genericFiber_nontrivial_of_specialFiber
#print axioms Komorebi.StrongArtin.GenericFiberSurvival.localizationMap_ne_zero_of_not_mem_piMultiple
