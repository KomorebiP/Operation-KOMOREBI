import KomorebiSpace.CocycleGaugeGroupoid
import Mathlib.CategoryTheory.InducedCategory
import Mathlib.CategoryTheory.Category.Cat
import Mathlib.CategoryTheory.Category.Preorder

set_option autoImplicit false

/-!
# Restriction of the existing cocycle groupoids to full view patches

The patch assignment is an actual contravariant functor to Cat. All fibers
are the previously defined unframed gauge groupoids, with unchanged
coefficient groups and maps. This is not an arbitrary category-valued system.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory Opposite

/-- Full view patches retain every original arrow between their objects. -/
abbrev PatchViews {V : Type u} [Category.{v} V] (W : Set V) :=
  InducedCategory V (fun x : W => x.val)

namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)

/-- Restrict the actual coefficient system, without altering the groups or transports. -/
def onPatch (W : Set V) : GroupViewSystem (PatchViews W) (fun x => G x.val) where
  pull := fun f => F.pull f.hom
  pull_id := fun x g => F.pull_id x.val g
  pull_comp := fun f g x => F.pull_comp f.hom g.hom x

/-- Restriction of a coherent cocycle to a smaller full patch. -/
def patchCocycleRestrict {U W : Set V} (h : U ⊆ W)
    (c : (F.onPatch W).Cocycle) : (F.onPatch U).Cocycle where
  edge := fun {a b} f =>
    c.edge (a := ⟨a.val, h a.property⟩) (b := ⟨b.val, h b.property⟩)
      (InducedCategory.homMk f.hom)
  edge_id := fun a => c.edge_id ⟨a.val, h a.property⟩
  edge_comp := by
    intro a b e f g
    exact c.edge_comp (a := ⟨a.val, h a.property⟩)
      (b := ⟨b.val, h b.property⟩) (c := ⟨e.val, h e.property⟩)
      (InducedCategory.homMk f.hom) (InducedCategory.homMk g.hom)

/-- The actual restriction functor on the existing unframed gauge groupoids. -/
def patchRestrict {U W : Set V} (h : U ⊆ W) :
    (F.onPatch W).GaugeObject ∅ ⥤ (F.onPatch U).GaugeObject ∅ where
  obj c := ⟨F.patchCocycleRestrict h c.labels⟩
  map a :=
    { change := ⟨fun x => a.change.val ⟨x.val, h x.property⟩, by
        intro x; exact False.elim x.property⟩
      target := by
        apply Cocycle.ext
        intro x y f
        have he := congrArg (fun c => c.edge
          (a := ⟨x.val, h x.property⟩) (b := ⟨y.val, h y.property⟩)
          (InducedCategory.homMk f.hom)) a.target
        exact he }
  map_id := by intro c; rfl
  map_comp := by intro c d e a b; rfl

@[simp] theorem patchRestrict_identity (W : Set V) :
    F.patchRestrict (Set.Subset.refl W) = 𝟭 ((F.onPatch W).GaugeObject ∅) := rfl

@[simp] theorem patchRestrict_comp {U W Z : Set V} (h : U ⊆ W) (k : W ⊆ Z) :
    F.patchRestrict k ⋙ F.patchRestrict h = F.patchRestrict (h.trans k) := rfl

/-- A strict category-valued presheaf on the patch poset. Each value is a groupoid. -/
def patchDiagram : (Set V)ᵒᵖ ⥤ Cat where
  obj W := Cat.of ((F.onPatch (unop W)).GaugeObject ∅)
  map h := (F.patchRestrict (leOfHom h.unop)).toCatHom
  map_id := by intro W; apply Cat.ext; rfl
  map_comp := by intro U W Z f g; apply Cat.ext; rfl

@[simp] theorem patchRestrict_edge {U W : Set V} (h : U ⊆ W)
    (c : (F.onPatch W).GaugeObject ∅) {a b : PatchViews U} (f : a ⟶ b) :
    ((F.patchRestrict h).obj c).labels.edge f =
      c.labels.edge (a := ⟨a.val, h a.property⟩) (b := ⟨b.val, h b.property⟩)
        (InducedCategory.homMk f.hom) := rfl

@[simp] theorem patchRestrict_gauge {U W : Set V} (h : U ⊆ W)
    {c d : (F.onPatch W).GaugeObject ∅} (a : c ⟶ d) (x : PatchViews U) :
    ((F.patchRestrict h).map a).change.val x =
      a.change.val ⟨x.val, h x.property⟩ := rfl

@[simp] theorem gauge_identity_value (B : Set V) (c : F.GaugeObject B) (x : V) :
    (𝟙 c : c ⟶ c).change.val x = 1 := rfl

@[simp] theorem gauge_composition_value {B : Set V} {c d e : F.GaugeObject B}
    (a : c ⟶ d) (b : d ⟶ e) (x : V) :
    (a ≫ b).change.val x = b.change.val x * a.change.val x := rfl

@[simp] theorem gauge_inverse_value {B : Set V} {c d : F.GaugeObject B}
    (a : c ⟶ d) (x : V) :
    (Groupoid.inv a).change.val x = (a.change.val x)⁻¹ := rfl

end GroupViewSystem
end KomorebiSpace
