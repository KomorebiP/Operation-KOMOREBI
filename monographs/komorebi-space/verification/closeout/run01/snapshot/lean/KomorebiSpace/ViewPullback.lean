import KomorebiSpace.CocycleGaugeGroupoid
import Mathlib.CategoryTheory.Equivalence

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Pullback along a functor of view categories

The coefficient groups are pulled back, not silently identified. The induced
functor uses the original cocycles and unframed gauge groupoids.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]

/-- Pull back the specified group coefficients along an actual view functor. -/
def reindex (F : GroupViewSystem W G) (H : V ⥤ W) :
    GroupViewSystem V (fun a => G (H.obj a)) where
  pull := fun f => F.pull (H.map f)
  pull_id := by intro a x; rw [H.map_id, F.pull_id]
  pull_comp := by intro a b c f g x; rw [H.map_comp, F.pull_comp]

/-- Pullback retains the labels on the image arrows. -/
def reindexCocycle (F : GroupViewSystem W G) (H : V ⥤ W) (c : F.Cocycle) :
    (F.reindex H).Cocycle where
  edge := fun f => c.edge (H.map f)
  edge_id := by intro a; rw [H.map_id, c.edge_id]
  edge_comp := by intro a b d f g; rw [H.map_comp, c.edge_comp]; rfl

@[simp] theorem reindexCocycle_edge (F : GroupViewSystem W G) (H : V ⥤ W)
    (c : F.Cocycle) {a b : V} (f : a ⟶ b) :
    (F.reindexCocycle H c).edge f = c.edge (H.map f) := rfl

/-- The pullback is a functor on the actual symmetry-retaining groupoids. -/
def reindexFunctor (F : GroupViewSystem W G) (H : V ⥤ W) :
    F.GaugeObject ∅ ⥤ (F.reindex H).GaugeObject ∅ where
  obj c := ⟨F.reindexCocycle H c.labels⟩
  map a :=
    { change := ⟨fun v => a.change.val (H.obj v), by
        intro v; exact False.elim v.property⟩
      target := by
        apply Cocycle.ext
        intro v w f
        exact congrArg (fun c => c.edge (H.map f)) a.target }
  map_id := by intro c; rfl
  map_comp := by intro c d e a b; rfl

@[simp] theorem reindexFunctor_gauge (F : GroupViewSystem W G) (H : V ⥤ W)
    {c d : F.GaugeObject ∅} (a : c ⟶ d) (v : V) :
    ((F.reindexFunctor H).map a).change.val v = a.change.val (H.obj v) := rfl

@[simp] theorem reindex_trivial (F : GroupViewSystem W G) (H : V ⥤ W) :
    F.reindexCocycle H F.trivial = (F.reindex H).trivial := rfl

/-- Cocycle compatibility along a natural transformation supplies a gauge comparison.
No invertibility of the transformation's components is needed for this identity. -/
theorem natural_comparison (F : GroupViewSystem W G) (T : W ⥤ W)
    (σ : ∀ a, a ⟶ T.obj a)
    (hn : ∀ {a b} (f : a ⟶ b), σ a ≫ T.map f = f ≫ σ b)
    (c : F.Cocycle) {a b : W} (f : a ⟶ b) :
    c.edge (σ a) * F.pull (σ a) (c.edge (T.map f)) *
      (F.pull f (c.edge (σ b)))⁻¹ = c.edge f := by
  have h := congrArg (fun k => c.edge k) (hn f)
  simp only [c.edge_comp] at h
  rw [h]
  group

/-- A gauge equation on an arrow is the naturality equation for its comparison. -/
theorem gauge_comparison_naturality (F : GroupViewSystem W G)
    {c d : F.GaugeObject ∅} (a : c ⟶ d) {v w : W} (f : v ⟶ w) :
    d.labels.edge f * F.pull f (a.change.val w) =
      a.change.val v * c.labels.edge f := by
  have h := congrArg (fun k => k.edge f) a.target
  change a.change.val v * c.labels.edge f * (F.pull f (a.change.val w))⁻¹ =
    d.labels.edge f at h
  rw [← h]
  group

end GroupViewSystem
end KomorebiSpace
