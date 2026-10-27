import KomorebiSpace.SiteDescent
import Mathlib.CategoryTheory.Sites.Descent.IsStack

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Comparison with mathlib's standard descent-data interface

All standard pullbacks are the actual restriction functors on gauge
families. The lemmas below expose their coordinate actions before invoking
any standard stack interface.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory Opposite Bicategory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem V G)
namespace StandardDescent
open Pseudofunctor.LocallyDiscreteOpToCat

/-- Coordinate formula for the standard pseudofunctor pullback of a gauge arrow. -/
theorem pullHom_value {X₁ X₂ Y Y' : Set V}
    {M₁ : (F.onPatch X₁).GaugeObject ∅} {M₂ : (F.onPatch X₂).GaugeObject ∅}
    {f₁ : Y ⟶ X₁} {f₂ : Y ⟶ X₂}
    (a : (F.patchRestrict (leOfHom f₁)).obj M₁ ⟶
      (F.patchRestrict (leOfHom f₂)).obj M₂)
    (g : Y' ⟶ Y) (gf₁ : Y' ⟶ X₁) (gf₂ : Y' ⟶ X₂)
    (x : PatchViews Y') :
    (pullHom (F := F.patchPseudofunctor) (f₁ := f₁) (f₂ := f₂) a g gf₁ gf₂
      (Subsingleton.elim _ _) (Subsingleton.elim _ _)).change.val x =
      a.change.val ⟨x.val, leOfHom g x.property⟩ := by
  simp [pullHom, Pseudofunctor.mapComp', patchPseudofunctor,
    LocallyDiscrete.mkPseudofunctor, pseudofunctorOfIsLocallyDiscrete]
  dsimp [patchDiagram, patchRestrict]
  simp

variable {I : Type z} {W : Set V} {U : I → Set V} (hU : ∀ i, U i ⊆ W)

abbrev Data := F.patchPseudofunctor.DescentData (fun i => homOfLE (hU i))

/-- Canonical descent of a global object has identity comparison gauges. -/
theorem ofObj_hom_value (c : (F.onPatch W).GaugeObject ∅)
    {Y : Set V} (q : Y ⟶ W) {i j : I} (fi : Y ⟶ U i) (fj : Y ⟶ U j)
    (x : PatchViews Y) :
    ((Pseudofunctor.DescentData.ofObj (F := F.patchPseudofunctor)
      (f := fun i => homOfLE (hU i)) c).hom q fi fj
        (Subsingleton.elim _ _) (Subsingleton.elim _ _)).change.val x = 1 := by
  simp [Pseudofunctor.DescentData.ofObj, Pseudofunctor.mapComp',
    patchPseudofunctor, LocallyDiscrete.mkPseudofunctor,
    pseudofunctorOfIsLocallyDiscrete]
  dsimp [patchDiagram, patchRestrict]
  simp

/-- A singleton inclusion for a known membership. -/
def singletonInclusion {Z : Set V} {x : V} (h : x ∈ Z) : ({x} : Set V) ⟶ Z :=
  homOfLE (by intro y hy; rw [Set.mem_singleton_iff.mp hy]; exact h)

/-- The comparison value at a view, extracted from standard descent on its singleton. -/
def label (D : Data F hU) (i j : I) (x : V) (hi : x ∈ U i) (hj : x ∈ U j) : G x :=
  (D.hom (singletonInclusion (hU i hi)) (singletonInclusion hi)
    (singletonInclusion hj) (Subsingleton.elim _ _) (Subsingleton.elim _ _)).change.val
      ⟨x, Set.mem_singleton x⟩

/-- Naturality makes the singleton label agree with evaluation on every common subpatch. -/
theorem hom_value (D : Data F hU) {Y : Set V} (q : Y ⟶ W) {i j : I}
    (fi : Y ⟶ U i) (fj : Y ⟶ U j) (x : PatchViews Y) :
    (D.hom q fi fj (Subsingleton.elim _ _) (Subsingleton.elim _ _)).change.val x =
      label F hU D i j x.val (leOfHom fi x.property) (leOfHom fj x.property) := by
  let g := singletonInclusion x.property
  let gi := singletonInclusion (leOfHom fi x.property)
  let gj := singletonInclusion (leOfHom fj x.property)
  have hp := D.pullHom_hom g q (singletonInclusion (leOfHom q x.property))
    (Subsingleton.elim _ _) fi fj (Subsingleton.elim _ _) (Subsingleton.elim _ _)
    gi gj (Subsingleton.elim _ _) (Subsingleton.elim _ _)
  have hv := congrArg (fun a => a.change.val ⟨x.val, Set.mem_singleton x.val⟩) hp
  have he := pullHom_value F (f₁ := fi) (f₂ := fj)
    (D.hom q fi fj (Subsingleton.elim _ _) (Subsingleton.elim _ _))
    g gi gj ⟨x.val, Set.mem_singleton x.val⟩
  exact he.symm.trans hv

/-- The standard triple-overlap equation is the noncommutative label equation. -/
theorem label_comp (D : Data F hU) (i j k : I) (x : V)
    (hi : x ∈ U i) (hj : x ∈ U j) (hk : x ∈ U k) :
    label F hU D i k x hi hk =
      label F hU D j k x hj hk * label F hU D i j x hi hj := by
  have hc := D.hom_comp (singletonInclusion (hU i hi))
    (singletonInclusion hi) (singletonInclusion hj) (singletonInclusion hk)
    (Subsingleton.elim _ _) (Subsingleton.elim _ _) (Subsingleton.elim _ _)
  have hv := congrArg (fun a => a.change.val ⟨x, Set.mem_singleton x⟩) hc
  exact hv.symm

/-- Standard overlap maps give the required relation between every pair of local labels. -/
theorem label_edge (D : Data F hU) (i j : I) (x y : V)
    (hxi : x ∈ U i) (hyi : y ∈ U i) (hxj : x ∈ U j) (hyj : y ∈ U j)
    (f : x ⟶ y) :
    label F hU D i j x hxi hxj *
        (D.obj i).labels.edge (a := ⟨x,hxi⟩) (b := ⟨y,hyi⟩) (InducedCategory.homMk f) *
        (F.pull f (label F hU D i j y hyi hyj))⁻¹ =
      (D.obj j).labels.edge (a := ⟨x,hxj⟩) (b := ⟨y,hyj⟩) (InducedCategory.homMk f) := by
  let qi : (U i ∩ U j) ⟶ U i := homOfLE Set.inter_subset_left
  let qj : (U i ∩ U j) ⟶ U j := homOfLE Set.inter_subset_right
  let q : (U i ∩ U j) ⟶ W := homOfLE (Set.inter_subset_left.trans (hU i))
  let a := D.hom q qi qj (Subsingleton.elim _ _) (Subsingleton.elim _ _)
  have he := congrArg (fun c => c.edge
    (a := (⟨x, hxi, hxj⟩ : PatchViews (U i ∩ U j)))
    (b := (⟨y, hyi, hyj⟩ : PatchViews (U i ∩ U j)))
    (InducedCategory.homMk f)) a.target
  change a.change.val ⟨x,hxi,hxj⟩ * _ * (F.pull f (a.change.val ⟨y,hyi,hyj⟩))⁻¹ = _ at he
  have hx := hom_value F hU D q qi qj ⟨x,hxi,hxj⟩
  have hy := hom_value F hU D q qi qj ⟨y,hyi,hyj⟩
  change a.change.val ⟨x,hxi,hxj⟩ = _ at hx
  change a.change.val ⟨y,hyi,hyj⟩ = _ at hy
  rw [hx, hy] at he
  exact he

/-- Standard descent data retain exactly the previously implemented overlap labels. -/
def toConcrete (D : Data F hU) :
    (F.onPatch W).CocycleDescentData (CompositionSite.inside W U) where
  patch i :=
    { edge := fun {a b} f => (D.obj i).labels.edge
        (a := ⟨a.val.val,a.property⟩) (b := ⟨b.val.val,b.property⟩)
        (InducedCategory.homMk f.hom)
      edge_id := fun a => (D.obj i).labels.edge_id ⟨a.val.val,a.property⟩
      edge_comp := by
        intro a b c f g
        exact (D.obj i).labels.edge_comp
          (a := ⟨a.val.val,a.property⟩) (b := ⟨b.val.val,b.property⟩)
          (c := ⟨c.val.val,c.property⟩)
          (InducedCategory.homMk f.hom) (InducedCategory.homMk g.hom) }
  change := fun i j x hi hj => label F hU D i j x.val hi hj
  change_edge := fun i j x y hxi hyi hxj hyj f =>
    label_edge F hU D i j x.val y.val hxi hyi hxj hyj f.hom
  change_comp := fun i j k x hi hj hk => label_comp F hU D i j k x.val hi hj hk

end StandardDescent
end GroupViewSystem
end KomorebiSpace
