import KomorebiSpace.PatchViewEquivalence
import KomorebiSpace.SectionViewEquivalence

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Redundant views and the failure of raw-patch invariance

Duplicating every view is a categorical equivalence, not an object bijection.
Its skeleton can miss a nonempty, nonsaturated patch. For nontrivial group
coefficients the resulting patch pullback is not even faithful on gauges.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace ViewDuplication
variable (V : Type u) [Category.{v} V]

/-- Two labelled, isomorphic copies of each view. -/
abbrev Duplicated := InducedCategory V (fun x : V × Bool => x.1)

/-- Keep only copy false when choosing a representative. -/
def embed : V ⥤ Duplicated V where
  obj x := (x, false)
  map f := InducedCategory.homMk f
  map_id := by intros; rfl
  map_comp := by intros; rfl

/-- Forget the redundant copy label, retaining all original arrows. -/
def forget : Duplicated V ⥤ V where
  obj x := x.1
  map f := f.hom
  map_id := by intros; rfl
  map_comp := by intros; rfl

/-- The two copies are related by the original identity morphism. -/
def copyIso (x : V) (a b : Bool) : Iso (C := Duplicated V) (x,a) (x,b) where
  hom := InducedCategory.homMk (𝟙 x)
  inv := InducedCategory.homMk (𝟙 x)
  hom_inv_id := by apply InducedCategory.hom_ext; simp
  inv_hom_id := by apply InducedCategory.hom_ext; simp

def counit : forget V ⋙ embed V ≅ 𝟭 (Duplicated V) :=
  NatIso.ofComponents (fun x => copyIso V x.1 false x.2) (by
    intro x y f
    apply InducedCategory.hom_ext
    change f.hom ≫ 𝟙 y.1 = 𝟙 x.1 ≫ f.hom
    simp)

/-- A genuine equivalence although the forward map is not onto on objects. -/
def equivalence : V ≌ Duplicated V :=
  CategoryTheory.Equivalence.mk (embed V) (forget V) (Iso.refl (𝟭 V)) (counit V)

theorem embed_not_surjective (x : V) : ¬ Function.Surjective (embed V).obj := by
  intro h
  obtain ⟨y,hy⟩ := h (x,true)
  have hb := congrArg (fun p : Duplicated V => p.2) hy
  change false = true at hb
  cases hb

/-- A raw patch can select only representatives omitted by the equivalence functor. -/
def missedPatch : Set (Duplicated V) := {x | x.2 = true}

@[simp] theorem missedPatch_preimage : (embed V).obj ⁻¹' missedPatch V = ∅ := by
  ext x
  change (false = true) ↔ False
  simp

omit [Category.{v} V] in
theorem missedPatch_nonempty (x : V) : (missedPatch V).Nonempty :=
  ⟨(x,true), rfl⟩

theorem missedPatch_not_isoClosed (x : V) :
    ¬ CompositionSite.IsoClosed (missedPatch V) := by
  intro h
  have hb := h (copyIso V x true false) (show (x,true) ∈ missedPatch V from rfl)
  change false = true at hb
  cases hb

/-- Constant coefficients for the gauge-level failure witness. -/
def constantGroups (H : Type w) [Group H] :
    GroupViewSystem (Duplicated V) (fun _ => H) where
  pull := fun _ => MonoidHom.id H
  pull_id := by intros; rfl
  pull_comp := by intros; rfl

def localObject (H : Type w) [Group H] :
    ((constantGroups V H).onPatch (missedPatch V)).GaugeObject ∅ :=
  ⟨((constantGroups V H).onPatch (missedPatch V)).trivial⟩

/-- Constant group elements are genuine automorphisms of the trivial local cocycle. -/
def localGauge {H : Type w} [Group H] (a : H) :
    localObject V H ⟶ localObject V H where
  change := ⟨fun _ => a, by intro x; exact False.elim x.property⟩
  target := by
    apply GroupViewSystem.Cocycle.ext
    intro x y f
    change a * 1 * a⁻¹ = 1
    group

/-- Restricting to the missed inverse-image patch erases all these automorphisms. -/
theorem localGauge_images {H : Type w} [Group H] (a b : H) :
    ((constantGroups V H).patchPullback (embed V) (missedPatch V)).map (localGauge V a) =
      ((constantGroups V H).patchPullback (embed V) (missedPatch V)).map (localGauge V b) := by
  apply GroupViewSystem.GaugeObject.Hom.ext
  apply Subtype.ext
  funext x
  have hb := x.property
  change false = true at hb
  cases hb

/-- On the original nonempty patch, different group elements are different gauge arrows. -/
theorem localGauge_ne {H : Type w} [Group H] (x : V) {a b : H} (hab : a ≠ b) :
    localGauge V a ≠ localGauge V b := by
  intro h
  have he := congrArg (fun k : localObject V H ⟶ localObject V H =>
    k.change.val ⟨(x,true),rfl⟩) h
  exact hab he

/-- Even an equivalence of view categories does not preserve arbitrary raw patch gauges. -/
theorem raw_patch_pullback_not_faithful {H : Type w} [Group H]
    (x : V) (a : H) (ha : a ≠ 1) :
    ¬ ((constantGroups V H).patchPullback (embed V) (missedPatch V)).Faithful := by
  intro hf
  let : ((constantGroups V H).patchPullback (embed V) (missedPatch V)).Faithful := hf
  have h := ((constantGroups V H).patchPullback (embed V) (missedPatch V)).map_injective
    (localGauge_images V a 1)
  exact localGauge_ne V x ha h

/-- Nevertheless, the entire cocycle groupoid is invariant under this duplication. -/
def cocycleEquivalence {G : V → Type w} [∀ a, Group (G a)] (F : GroupViewSystem V G) :
    (F.reindex (forget V)).GaugeObject ∅ ≌ F.GaugeObject ∅ :=
  (F.reindex (forget V)).reindexEquivalence (equivalence V)

/-- The original coherent section space is also recovered from duplicated appearances. -/
def sectionEquivalence (F : ViewSystem.{u,v,w} V) :
    (F.reindex (forget V)).Ambient ≃ F.Ambient :=
  (F.reindex (forget V)).viewEquivalence (equivalence V)

end ViewDuplication
end KomorebiSpace
