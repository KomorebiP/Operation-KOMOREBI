import PresentationJacobianCoordinates
import PresentationObstructionRank

/-!
# Intrinsic obstruction capstone

The displayed transpose-Jacobian kernel of a presentation is intrinsic exactly
when the chosen relation generators are independent in the conormal module.
In general it maps onto cotangent H1 with kernel equal to relation syzygies.
-/

namespace Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone

open Module
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.PresentationJacobianCoordinates
open Komorebi.StrongArtin.PresentationObstructionRank

noncomputable section

universe u v w t

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [CommRing S] [Algebra R S]

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- If the canonical map from the presentation kernel to cotangent H1 is
injective, then the selected relation generators were already independent in
the conormal module. -/
theorem relationIndependent_of_toH1Cotangent_injective
    (P : Algebra.Presentation R S ι σ)
    (hinj : Function.Injective (toH1Cotangent P)) :
    Function.Injective (Algebra.Presentation.differentials.hom₁ P) := by
  intro x y hxy
  have hdiff : Algebra.Presentation.differentials.hom₁ P (x - y) = 0 := by
    rw [map_sub, hxy, sub_self]
  have hker : x - y ∈ LinearMap.ker (relationDifferentialMap P) := by
    rw [mem_presentationObstructionDual_iff_cotangentComplex_eq_zero]
    simp [hdiff]
  let z : presentationObstructionDual P := ⟨x - y, hker⟩
  have hzmap : toH1Cotangent P z = 0 := by
    apply Subtype.ext
    exact hdiff
  have hz : z = 0 := hinj (by simpa using hzmap)
  have hzero : x - y = 0 := congrArg Subtype.val hz
  exact sub_eq_zero.mp hzero

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- The presentation obstruction agrees injectively with intrinsic cotangent
H1 if and only if the relation generators are independent in the conormal
module. -/
theorem toH1Cotangent_injective_iff_relationIndependent
    (P : Algebra.Presentation R S ι σ) :
    Function.Injective (toH1Cotangent P) ↔
      Function.Injective (Algebra.Presentation.differentials.hom₁ P) := by
  constructor
  · exact relationIndependent_of_toH1Cotangent_injective P
  · exact toH1Cotangent_injective_of_relationIndependent P

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- Vanishing of relation syzygies is equivalent to conormal independence. -/
theorem relationSyzygies_eq_bot_iff_relationIndependent
    (P : Algebra.Presentation R S ι σ) :
    relationSyzygies P = ⊥ ↔
      Function.Injective (Algebra.Presentation.differentials.hom₁ P) := by
  constructor
  · intro hsyz
    have hinj : Function.Injective (toH1Cotangent P) := by
      intro x y hxy
      have hd : x - y ∈ relationSyzygies P := by
        change toH1Cotangent P (x - y) = 0
        calc
          toH1Cotangent P (x - y) =
              toH1Cotangent P x - toH1Cotangent P y :=
            (toH1Cotangent P).map_sub x y
          _ = 0 := sub_eq_zero.mpr hxy
      have hd0 : x - y ∈ (⊥ : Submodule S (presentationObstructionDual P)) := by
        rw [← hsyz]
        exact hd
      have hzero : x - y = 0 := by simpa using hd0
      exact sub_eq_zero.mp hzero
    exact (toH1Cotangent_injective_iff_relationIndependent P).mp hinj
  · intro hrel
    have hinj : Function.Injective (toH1Cotangent P) :=
      (toH1Cotangent_injective_iff_relationIndependent P).mpr hrel
    apply le_antisymm
    · intro x hx
      have hx0 : toH1Cotangent P x = 0 := by
        exact hx
      have hxeq : x = 0 := hinj (by simpa using hx0)
      rw [hxeq]
      exact Submodule.zero_mem _
    · exact bot_le

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- Complete intrinsic-obstruction criterion: under conormal independence the
Jacobian-transpose kernel is linearly equivalent to cotangent H1, while in
general relation syzygies are the exact kernel of the canonical surjection. -/
theorem intrinsic_obstruction_criterion
    (P : Algebra.Presentation R S ι σ) :
    Function.Surjective (toH1Cotangent P) ∧
      Function.Exact (Submodule.subtype (relationSyzygies P))
        (toH1Cotangent P) ∧
      (Function.Injective (toH1Cotangent P) ↔
        Function.Injective (Algebra.Presentation.differentials.hom₁ P)) := by
  exact ⟨toH1Cotangent_surjective P,
    exact_syzygy_to_obstruction_to_h1 P,
    toH1Cotangent_injective_iff_relationIndependent P⟩

end

end Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone

#print axioms Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone.relationIndependent_of_toH1Cotangent_injective
#print axioms Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone.relationSyzygies_eq_bot_iff_relationIndependent
#print axioms Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone.intrinsic_obstruction_criterion
