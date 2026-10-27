import Komorebi.Multiverse.LogicalResidual
import Komorebi.Foundation.KZFCTheory

/-!
# Interface between abstract world networks and ZFC models

The class of all ZFC models is not packaged as a set.  Instead this interface
works with an externally indexed collection of ZFC models and a user-supplied
reflexive/transitive reachability relation.  A future forcing/geology layer may
instantiate that relation by a formally defined forcing-extension or ground map.
-/

universe u v

namespace Komorebi.Multiverse

open FirstOrder FirstOrder.Language
open Komorebi.MembershipFormula Komorebi.ZFCAxiomSyntax

/-- One membership structure together with a proof that it satisfies the explicit
ZFC theory developed in the predecessor branch. -/
structure ZFCWorld where
  Carrier : Type u
  struc : Komorebi.MembershipFormula.language.Structure Carrier
  modelsZFC : @Theory.Model Komorebi.MembershipFormula.language Carrier struc
    Komorebi.ZFCAxiomSyntax.zfcTheory

/-- An indexed multiverse of ZFC worlds.  `reach` is intentionally abstract at
this stage; no forcing theorem is smuggled into the interface. -/
structure ZFCWorldNetwork where
  Index : Type v
  world : Index → ZFCWorld.{u}
  reach : Index → Index → Prop
  refl : ∀ i, reach i i
  trans : ∀ {i j k}, reach i j → reach j k → reach i k

namespace ZFCWorldNetwork

variable (M : ZFCWorldNetwork.{u,v})

/-- Forget model payloads and retain only multiverse reachability geometry. -/
def network : WorldNetwork where
  World := M.Index
  reach := M.reach
  refl := M.refl
  trans := M.trans

/-- Truth semantics of membership-language sentences in each indexed ZFC world. -/
def sentenceSemantics :
    WorldSemantics M.network Komorebi.MembershipFormula.language.Sentence where
  Holds := fun i φ =>
    @Sentence.Realize Komorebi.MembershipFormula.language
      (M.world i).Carrier (M.world i).struc φ

/-- Every indexed world satisfies the explicit ZFC theory by construction. -/
theorem each_models_zfc (i : M.Index) :
    @Theory.Model Komorebi.MembershipFormula.language
      (M.world i).Carrier (M.world i).struc Komorebi.ZFCAxiomSyntax.zfcTheory :=
  (M.world i).modelsZFC


/-- Every pair of indexed ZFC worlds agrees on every sentence belonging to the
encoded ZFC axiom theory.  Independent sentences may still contribute residuals. -/
theorem worlds_agree_on_zfc (i j : M.Index) :
    M.sentenceSemantics.AgreeOn Komorebi.ZFCAxiomSyntax.zfcTheory i j := by
  intro φ hφ
  constructor
  · intro _
    exact (M.each_models_zfc j).realize_of_mem φ hφ
  · intro _
    exact (M.each_models_zfc i).realize_of_mem φ hφ

/-- The encoded ZFC axioms lie in the common logical core of every indexed ZFC
world network. -/
theorem zfc_subset_commonCore :
    Komorebi.ZFCAxiomSyntax.zfcTheory ⊆ M.sentenceSemantics.CommonCore := by
  intro φ hφ i
  exact (M.each_models_zfc i).realize_of_mem φ hφ

/-- `Γ`-agreement is the precise zero logical residual relation for the indexed
ZFC worlds. -/
def AgreeOn (Γ : Set Komorebi.MembershipFormula.language.Sentence) (i j : M.Index) : Prop :=
  M.sentenceSemantics.AgreeOn Γ i j

end ZFCWorldNetwork
end Komorebi.Multiverse
