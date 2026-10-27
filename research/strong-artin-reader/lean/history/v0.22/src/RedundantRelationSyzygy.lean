import PresentationIntrinsicObstructionCapstone

/-!
# Redundant relations create spurious presentation obstructions

Two distinct chosen relation generators with the same conormal class produce a
nonzero relation syzygy.  Thus a raw transpose-Jacobian-kernel count can
strictly overcount intrinsic cotangent H1 when the presentation is redundant.
-/

namespace Komorebi.StrongArtin.RedundantRelationSyzygy

open Module
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.PresentationJacobianCoordinates
open Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone

noncomputable section

universe u v w t

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [CommRing S] [Algebra R S]

/-- Nonvanishing of the syzygy kernel is exactly failure of independence of the
chosen conormal relation generators. -/
theorem relationSyzygies_ne_bot_iff_not_relationIndependent
    (P : Algebra.Presentation R S ι σ) :
    relationSyzygies P ≠ ⊥ ↔
      ¬ Function.Injective (Algebra.Presentation.differentials.hom₁ P) := by
  exact not_congr (relationSyzygies_eq_bot_iff_relationIndependent P)

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- Two distinct relation-basis vectors with equal conormal images force a
nonzero relation syzygy. -/
theorem duplicate_conormal_relations_give_nontrivial_syzygy
    [Nontrivial S] [DecidableEq σ]
    (P : Algebra.Presentation R S ι σ) {r s : σ} (hrs : r ≠ s)
    (heq : Algebra.Presentation.differentials.hom₁ P
        (Finsupp.single r 1) =
      Algebra.Presentation.differentials.hom₁ P
        (Finsupp.single s 1)) :
    relationSyzygies P ≠ ⊥ := by
  rw [relationSyzygies_ne_bot_iff_not_relationIndependent]
  intro hinj
  have hrsingle : (Finsupp.single r (1 : S)) = Finsupp.single s 1 :=
    hinj heq
  have hat := congrArg (fun x : σ →₀ S => x r) hrsingle
  have h10 : (1 : S) = 0 := by
    simpa only [Finsupp.single_eq_same,
      Finsupp.single_eq_of_ne hrs] using hat
  exact one_ne_zero h10

/-- Equal conormal classes for two distinct selected relations prevent the raw
presentation obstruction from being intrinsically identified with cotangent
H1 by the canonical map. -/
theorem duplicate_conormal_relations_prevent_canonical_injectivity
    [Nontrivial S] [DecidableEq σ]
    (P : Algebra.Presentation R S ι σ) {r s : σ} (hrs : r ≠ s)
    (heq : Algebra.Presentation.differentials.hom₁ P
        (Finsupp.single r 1) =
      Algebra.Presentation.differentials.hom₁ P
        (Finsupp.single s 1)) :
    ¬ Function.Injective (toH1Cotangent P) := by
  intro hinj
  have hrel := relationIndependent_of_toH1Cotangent_injective P hinj
  exact (duplicate_conormal_relations_give_nontrivial_syzygy P hrs heq)
    ((relationSyzygies_eq_bot_iff_relationIndependent P).2 hrel)

end

end Komorebi.StrongArtin.RedundantRelationSyzygy

#print axioms Komorebi.StrongArtin.RedundantRelationSyzygy.duplicate_conormal_relations_give_nontrivial_syzygy
#print axioms Komorebi.StrongArtin.RedundantRelationSyzygy.duplicate_conormal_relations_prevent_canonical_injectivity
