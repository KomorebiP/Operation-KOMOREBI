import Mathlib.RepresentationTheory.Homological.GroupCohomology.Functoriality
import FiniteGroupH1Averaging

namespace Komorebi.StrongArtin.H1RestrictionInjective

open CategoryTheory
open Komorebi.StrongArtin.FiniteGroupH1Averaging

noncomputable section

universe u

variable {k G : Type u} [Field k] [Group G]

/-- **Prime-to-characteristic restriction injectivity in degree one.** For a
normal subgroup `S`, if the finite quotient `G ⧸ S` has nonzero order in the
coefficient field, then the explicit restriction map

`H¹(G,A) → H¹(S,A)`

is injective for every linear representation `A`. -/
theorem H1_restriction_map_injective_of_quotient_card_ne_zero
    (A : Rep.{u} k G)
    (S : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (hcard : (Fintype.card (G ⧸ S) : k) ≠ 0) :
    Function.Injective
      (groupCohomology.map S.subtype (𝟙 (Rep.res S.subtype A)) 1) := by
  have hsub : Subsingleton
      (groupCohomology.H1 (A.quotientToInvariants S)) :=
    H1_subsingleton_of_card_ne_zero (A.quotientToInvariants S) hcard
  have hf : (groupCohomology.H1InfRes A S).f = 0 := by
    ext x
    have hx : x = 0 := @Subsingleton.elim _ hsub x 0
    subst x
    simp
  have hmono : Mono (groupCohomology.H1InfRes A S).g :=
    (groupCohomology.H1InfRes_exact A S).mono_g hf
  rw [groupCohomology.H1InfRes_g] at hmono
  exact (ModuleCat.mono_iff_injective _).1 hmono

/-- The same injectivity statement in the bundled inflation--restriction short
complex notation. -/
theorem H1_restriction_injective_of_quotient_card_ne_zero
    (A : Rep.{u} k G)
    (S : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (hcard : (Fintype.card (G ⧸ S) : k) ≠ 0) :
    Function.Injective (groupCohomology.H1InfRes A S).g := by
  rw [groupCohomology.H1InfRes_g]
  exact H1_restriction_map_injective_of_quotient_card_ne_zero A S hcard

/-- Operational contrapositive: a nonzero degree-one cohomology class remains
nonzero after restriction across a finite prime-to-characteristic quotient. -/
theorem H1_restriction_map_ne_zero_of_ne_zero
    (A : Rep.{u} k G)
    (S : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (hcard : (Fintype.card (G ⧸ S) : k) ≠ 0)
    (x : groupCohomology.H1 A)
    (hx : x ≠ 0) :
    groupCohomology.map S.subtype (𝟙 (Rep.res S.subtype A)) 1 x ≠ 0 := by
  intro hzero
  have hinj := H1_restriction_map_injective_of_quotient_card_ne_zero A S hcard
  apply hx
  apply hinj
  have hzmap : groupCohomology.map S.subtype (𝟙 (Rep.res S.subtype A)) 1
      (0 : groupCohomology.H1 A) = 0 := by
    exact map_zero _
  exact hzero.trans hzmap.symm

/-- A nonzero `H¹` class represented by a cocycle has a nonzero cocycle value
on the normal subgroup whenever the quotient order is nonzero in the
coefficient field. This is the concrete kernel-element extraction used by the
pre-Chebotarev selector. -/
theorem exists_subgroup_element_with_nonzero_cocycle_value
    (A : Rep.{u} k G)
    (S : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (hcard : (Fintype.card (G ⧸ S) : k) ≠ 0)
    (f : groupCohomology.cocycles₁ A)
    (hclass : groupCohomology.H1π A f ≠ 0) :
    ∃ s : S, f s ≠ 0 := by
  have hresclass : groupCohomology.map S.subtype
      (𝟙 (Rep.res S.subtype A)) 1 (groupCohomology.H1π A f) ≠ 0 :=
    H1_restriction_map_ne_zero_of_ne_zero A S hcard
      (groupCohomology.H1π A f) hclass
  by_contra h
  push Not at h
  let rf : groupCohomology.cocycles₁ (Rep.res S.subtype A) :=
    groupCohomology.mapCocycles₁ S.subtype (𝟙 _) f
  have hrf : rf = 0 := by
    apply groupCohomology.cocycles₁_ext
    intro s
    change f s = 0
    exact h s
  apply hresclass
  rw [groupCohomology.H1π_comp_map_apply S.subtype (𝟙 _) f]
  change groupCohomology.H1π (Rep.res S.subtype A) rf = 0
  rw [hrf]
  exact map_zero _

end
end Komorebi.StrongArtin.H1RestrictionInjective

#print axioms Komorebi.StrongArtin.H1RestrictionInjective.H1_restriction_map_injective_of_quotient_card_ne_zero
#print axioms Komorebi.StrongArtin.H1RestrictionInjective.H1_restriction_injective_of_quotient_card_ne_zero
#print axioms Komorebi.StrongArtin.H1RestrictionInjective.H1_restriction_map_ne_zero_of_ne_zero
#print axioms Komorebi.StrongArtin.H1RestrictionInjective.exists_subgroup_element_with_nonzero_cocycle_value
