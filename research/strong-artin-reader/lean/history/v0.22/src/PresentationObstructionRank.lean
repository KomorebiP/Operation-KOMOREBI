import PresentationObstructionExactSequence
import Mathlib.LinearAlgebra.Dimension.RankNullity

/-!
# Rank of presentation and intrinsic obstructions

The relation-differential kernel of a chosen presentation surjects onto the
intrinsic first homology of the naive cotangent complex.  Rank-nullity makes
the excess exactly the rank of relation syzygies.
-/

namespace Komorebi.StrongArtin.PresentationObstructionRank

open Module
open Komorebi.StrongArtin.PresentationObstructionExactSequence

noncomputable section

universe u v w t

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [CommRing S] [Algebra R S]

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- Rank-nullity for the exact presentation-obstruction sequence, with
cardinal lifts inserted because the relation module and cotangent H1 may live
in different universes. -/
theorem lift_rank_presentationObstructionDual
    [HasRankNullity.{max t v} S] (P : Algebra.Presentation R S ι σ) :
    Cardinal.lift.{max u w} (Module.rank S (presentationObstructionDual P)) =
      Cardinal.lift.{max t v} (Module.rank S P.toExtension.H1Cotangent) +
        Cardinal.lift.{max u w} (Module.rank S (relationSyzygies P)) := by
  simpa [relationSyzygies] using
    (LinearMap.lift_rank_eq_of_surjective
      (R := S) (M := presentationObstructionDual P)
      (M' := P.toExtension.H1Cotangent)
      (f := toH1Cotangent P) (toH1Cotangent_surjective P))

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- Under conormal independence, the presentation obstruction has exactly the
intrinsic cotangent-H1 rank, up to the unavoidable universe lifts. -/
theorem lift_rank_eq_of_relationIndependent
    [HasRankNullity.{max t v} S] (P : Algebra.Presentation R S ι σ)
    (hrel : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P)) :
    Cardinal.lift.{max u w} (Module.rank S (presentationObstructionDual P)) =
      Cardinal.lift.{max t v} (Module.rank S P.toExtension.H1Cotangent) := by
  exact (obstructionDualEquivH1_of_relationIndependent P hrel).lift_rank_eq

end

end Komorebi.StrongArtin.PresentationObstructionRank

#print axioms Komorebi.StrongArtin.PresentationObstructionRank.lift_rank_presentationObstructionDual
#print axioms Komorebi.StrongArtin.PresentationObstructionRank.lift_rank_eq_of_relationIndependent
