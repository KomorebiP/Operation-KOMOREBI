import KomorebiSpace.CompositionSite
import KomorebiSpace.PatchViewSystem
import KomorebiSpace.DescentEquivalence
import Mathlib.CategoryTheory.Bicategory.Functor.LocallyDiscrete

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Effective descent over every patch and every composition-covering sieve

The topology and the restricted groupoids are constructed independently.
This file proves their cover condition agrees with the existing descent
hypothesis, then applies the actual groupoid equivalence on any patch.
It does not identify our explicit descent-data type with mathlib's
Pseudofunctor.DescentData. That comparison is a separate formal interface.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory Opposite Bicategory
namespace CompositionSite
variable {V : Type u} [Category.{v} V]

/-- A subpatch expressed in the full category on the ambient patch W. -/
def inside {I : Type z} (W : Set V) (U : I → Set V) : I → Set (PatchViews W) :=
  fun i => {x | x.val ∈ U i}

/-- The relative family condition is precisely the old full-patch composition cover. -/
theorem familyCovers_iff_compositionCover {I : Type z} (W : Set V) (U : I → Set V) :
    FamilyCovers W U ↔ GroupViewSystem.CompositionCover (inside W U) := by
  constructor
  · intro h a b c f g
    let q : Triangle V := ⟨a.val, b.val, c.val, f.hom, g.hom⟩
    have hq : q.support ⊆ W := (q.support_le_iff W).mpr
      ⟨a.property, b.property, c.property⟩
    obtain ⟨i, hi⟩ := h q hq
    exact ⟨i, hi q.a_mem, hi q.b_mem, hi q.c_mem⟩
  · intro h q hq
    let a : PatchViews W := ⟨q.a, hq q.a_mem⟩
    let b : PatchViews W := ⟨q.b, hq q.b_mem⟩
    let c : PatchViews W := ⟨q.c, hq q.c_mem⟩
    obtain ⟨i, hi, hj, hk⟩ := h a b c
      (InducedCategory.homMk q.first) (InducedCategory.homMk q.second)
    exact ⟨i, (q.support_le_iff (U i)).mpr ⟨hi, hj, hk⟩⟩

end CompositionSite

namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)

/-- The strict restriction diagram supplies the standard pseudofunctor interface. -/
def patchPseudofunctor : Pseudofunctor (LocallyDiscrete (Set V)ᵒᵖ) Cat :=
  LocallyDiscrete.mkPseudofunctor
    (fun W => F.patchDiagram.obj W)
    (fun h => F.patchDiagram.map h)
    (fun _ => Iso.refl _) (fun _ _ => Iso.refl _)
    (by intros; ext c; apply GaugeObject.Hom.ext; apply Subtype.ext; funext x
        dsimp [patchDiagram, patchRestrict, GaugeObject.compose, GaugeObject.identity]
        simp)
    (by intros; ext c; apply GaugeObject.Hom.ext; apply Subtype.ext; funext x
        dsimp [patchDiagram, patchRestrict, GaugeObject.compose, GaugeObject.identity]
        simp)
    (by intros; ext c; apply GaugeObject.Hom.ext; apply Subtype.ext; funext x
        dsimp [patchDiagram, patchRestrict, GaugeObject.compose, GaugeObject.identity]
        simp)

/-- Every covering family on every ambient patch admits effective groupoid descent. -/
noncomputable def siteDescent {I : Type z} (W : Set V) (U : I → Set V)
    (h : CompositionSite.FamilyCovers W U) :
    (F.onPatch W).GaugeObject ∅ ≌
      (F.onPatch W).CocycleDescentData (CompositionSite.inside W U) :=
  CocycleDescentData.descentEquivalence (F.onPatch W) (CompositionSite.inside W U)
    ((CompositionSite.familyCovers_iff_compositionCover W U).mp h)

/-- The equivalence uses the actual restriction functor, not an arbitrary equivalent map. -/
@[simp] theorem siteDescent_functor {I : Type z} (W : Set V) (U : I → Set V)
    (h : CompositionSite.FamilyCovers W U) :
    (F.siteDescent W U h).functor =
      CocycleDescentData.restrictionFunctor (F.onPatch W) (CompositionSite.inside W U) := rfl

/-- In particular, the theorem applies to every covering sieve of the constructed topology. -/
noncomputable def coveringSieveDescent (W : Set V) (s : Sieve W)
    (hs : s ∈ CompositionSite.topology V W) :
    (F.onPatch W).GaugeObject ∅ ≌
      (F.onPatch W).CocycleDescentData
        (CompositionSite.inside W (fun Z : CompositionSite.sievePatches s => Z.val)) :=
  F.siteDescent W _ (CompositionSite.sieve_family_covers hs)

/-- After any base change, the same coefficients admit descent for the intersected cover. -/
noncomputable def baseChangeDescent {I : Type z} {W Z : Set V} (hZW : Z ⊆ W)
    (U : I → Set V) (h : CompositionSite.FamilyCovers W U) :
    (F.onPatch Z).GaugeObject ∅ ≌
      (F.onPatch Z).CocycleDescentData
        (CompositionSite.inside Z (fun i => U i ∩ Z)) :=
  F.siteDescent Z _ (CompositionSite.intersection_cover hZW h)

/-- A cover refined by covers has the same effective reconstruction theorem. -/
noncomputable def compositeDescent {I : Type z} {J : I → Type z} (W : Set V)
    (U : I → Set V) (T : ∀ i, J i → Set V)
    (h : CompositionSite.FamilyCovers W U)
    (k : ∀ i, CompositionSite.FamilyCovers (U i) (T i)) :
    (F.onPatch W).GaugeObject ∅ ≌
      (F.onPatch W).CocycleDescentData
        (CompositionSite.inside W (fun ij : Sigma J => T ij.1 ij.2)) :=
  F.siteDescent W _ (CompositionSite.composite_cover h k)

end GroupViewSystem
end KomorebiSpace
