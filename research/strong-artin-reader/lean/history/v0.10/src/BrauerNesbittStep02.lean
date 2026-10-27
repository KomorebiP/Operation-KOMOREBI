module

public import BrauerNesbittStep01
public import Mathlib.RingTheory.FiniteLength

open scoped MonoidAlgebra

namespace Komorebi.StrongArtin.SemisimLift

universe uK uG uM uN uS
variable {K : Type uK} [Field K]
variable {G : Type uG} [Group G]
variable {M : Type uM} [AddCommGroup M] [Module K M] [Module K[G] M]
  [IsScalarTower K K[G] M] [FiniteDimensional K M]
variable {N : Type uN} [AddCommGroup N] [Module K N] [Module K[G] N]
  [IsScalarTower K K[G] N] [FiniteDimensional K N]
variable {T : Type uS} [AddCommGroup T] [Module K T] [Module K[G] T]
  [IsScalarTower K K[G] T] [FiniteDimensional K T]

set_option linter.style.haveILetI false in
/-- Finite isotypic modules of the same simple group-algebra type are determined,
up to group-algebra linear equivalence, by their underlying field dimension. -/
public theorem isotypic_equiv_of_finrank_eq
    [IsSemisimpleModule K[G] M] [IsSemisimpleModule K[G] N]
    [IsSimpleModule K[G] T]
    (hM : IsIsotypicOfType K[G] M T)
    (hN : IsIsotypicOfType K[G] N T)
    (hdim : Module.finrank K M = Module.finrank K N) :
    Nonempty (M ≃ₗ[K[G]] N) := by
  letI : Module.Finite K[G] M := Module.Finite.of_restrictScalars_finite K K[G] M
  letI : Module.Finite K[G] N := Module.Finite.of_restrictScalars_finite K K[G] N
  obtain ⟨m, ⟨eM⟩⟩ := hM.linearEquiv_fun
  obtain ⟨n, ⟨eN⟩⟩ := hN.linearEquiv_fun
  have hdT : 0 < Module.finrank K T := by
    haveI : Nontrivial T := IsSimpleModule.nontrivial K[G] T
    exact Module.finrank_pos
  have hm : Module.finrank K M = m * Module.finrank K T := by
    calc
      Module.finrank K M = Module.finrank K (Fin m → T) :=
        (eM.restrictScalars K).finrank_eq
      _ = ∑ _i : Fin m, Module.finrank K T := Module.finrank_pi_fintype K
      _ = m * Module.finrank K T := by simp
  have hn : Module.finrank K N = n * Module.finrank K T := by
    calc
      Module.finrank K N = Module.finrank K (Fin n → T) :=
        (eN.restrictScalars K).finrank_eq
      _ = ∑ _i : Fin n, Module.finrank K T := Module.finrank_pi_fintype K
      _ = n * Module.finrank K T := by simp
  have hmn_mul : m * Module.finrank K T = n * Module.finrank K T := by
    rw [← hm, ← hn]
    exact hdim
  have hmn : m = n := Nat.eq_of_mul_eq_mul_right hdT hmn_mul
  subst n
  exact ⟨eM.trans eN.symm⟩

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.isotypic_equiv_of_finrank_eq
