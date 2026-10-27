import KomorebiSpace.DescentComparison
import Mathlib.CategoryTheory.Equivalence

set_option autoImplicit false

/-!
# The groupoid of nonabelian descent data

Objects carry local cocycles and specified coherent overlap isomorphisms.
Morphisms are local gauges commuting with those overlap isomorphisms.
Restriction is a genuine functor from the existing global gauge groupoid.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable {I : Type z} {F : GroupViewSystem V G} {U : I → Set V}
namespace CocycleDescentData

/-- The overlap square for a morphism retains its noncommutative order. -/
structure Hom (D E : F.CocycleDescentData U) where
  value : ∀ i, ∀ x : U i, G x.val
  local_eq : ∀ (i : I) (x y : U i) (f : x.val ⟶ y.val),
    value i x * (D.patch i).edge f * (F.pull f (value i y))⁻¹ = (E.patch i).edge f
  overlap : ∀ (i j : I) (x : V) (hi : x ∈ U i) (hj : x ∈ U j),
    value j ⟨x,hj⟩ * D.change i j x hi hj = E.change i j x hi hj * value i ⟨x,hi⟩

@[ext] theorem Hom.ext {D E : F.CocycleDescentData U} {a b : Hom D E}
    (h : ∀ i x, a.value i x = b.value i x) : a = b := by
  cases a with
  | mk av al ao =>
    cases b with
    | mk bv bl bo =>
      have he : av = bv := by funext i x; exact h i x
      cases he
      rfl

def identity (D : F.CocycleDescentData U) : Hom D D where
  value := fun _ _ => 1
  local_eq := by intros; simp
  overlap := by intros; simp

def compose {D E K : F.CocycleDescentData U} (a : Hom D E) (b : Hom E K) : Hom D K where
  value := fun i x => b.value i x * a.value i x
  local_eq := by
    intro i x y f
    rw [map_mul]
    calc
      _ = b.value i x * (a.value i x * (D.patch i).edge f *
          (F.pull f (a.value i y))⁻¹) * (F.pull f (b.value i y))⁻¹ := by group
      _ = _ := by rw [a.local_eq, b.local_eq]
  overlap := by
    intro i j x hi hj
    calc
      _ = b.value j ⟨x,hj⟩ * (a.value j ⟨x,hj⟩ * D.change i j x hi hj) := by group
      _ = b.value j ⟨x,hj⟩ * (E.change i j x hi hj * a.value i ⟨x,hi⟩) := by rw [a.overlap]
      _ = (b.value j ⟨x,hj⟩ * E.change i j x hi hj) * a.value i ⟨x,hi⟩ := by group
      _ = _ := by rw [b.overlap]; group

def reverse {D E : F.CocycleDescentData U} (a : Hom D E) : Hom E D where
  value := fun i x => (a.value i x)⁻¹
  local_eq := by
    intro i x y f
    rw [← a.local_eq i x y f, map_inv]
    group
  overlap := by
    intro i j x hi hj
    calc
      _ = (a.value j ⟨x,hj⟩)⁻¹ *
        (E.change i j x hi hj * a.value i ⟨x,hi⟩) * (a.value i ⟨x,hi⟩)⁻¹ := by group
      _ = _ := by rw [← a.overlap]; group

instance : Groupoid (F.CocycleDescentData U) where
  Hom := Hom
  id := identity
  comp := compose
  id_comp := by intro D E a; apply Hom.ext; intro i x; exact mul_one _
  comp_id := by intro D E a; apply Hom.ext; intro i x; exact one_mul _
  assoc := by intro D E K L a b c; apply Hom.ext; intro i x; exact (mul_assoc _ _ _).symm
  inv := reverse
  inv_comp := by intro D E a; apply Hom.ext; intro i x; exact mul_inv_cancel _
  comp_inv := by intro D E a; apply Hom.ext; intro i x; exact inv_mul_cancel _

@[simp] theorem composition_value {D E K : F.CocycleDescentData U}
    (a : D ⟶ E) (b : E ⟶ K) (i : I) (x : U i) :
    (a ≫ b).value i x = b.value i x * a.value i x := rfl

/-- The canonical descent datum of a global cocycle has identity overlap gauges. -/
def ofGlobal (c : F.Cocycle) : F.CocycleDescentData U where
  patch := fun i => F.restrictCocycle c (U i)
  change := fun _ _ _ _ _ => 1
  change_edge := by intros; simp [restrictCocycle]
  change_comp := by intros; simp

/-- Restrict an actual global gauge arrow to every patch. -/
def restrictHom {c d : F.GaugeObject (∅ : Set V)} (a : c ⟶ d) :
    ofGlobal (U := U) c.labels ⟶ ofGlobal d.labels where
  value := fun _ x => a.change.val x.val
  local_eq := by
    intro i x y f
    exact congrArg (fun c : F.Cocycle => c.edge f) a.target
  overlap := by intros; simp [ofGlobal]

/-- Restriction into the descent-data groupoid. -/
def restrictionFunctor (F : GroupViewSystem V G) (U : I → Set V) :
    F.GaugeObject (∅ : Set V) ⥤ F.CocycleDescentData U where
  obj := fun c => ofGlobal c.labels
  map := restrictHom
  map_id := by intro c; apply Hom.ext; intros; rfl
  map_comp := by intros; apply Hom.ext; intros; rfl

@[simp] theorem restriction_value {c d : F.GaugeObject (∅ : Set V)}
    (a : c ⟶ d) (i : I) (x : U i) :
    ((restrictionFunctor F U).map a).value i x = a.change.val x.val := rfl

/-- The chosen local comparisons give an isomorphism from restricted globalization to D. -/
def Effectuation.toDescentHom {D : F.CocycleDescentData U} (E : D.Effectuation) :
    ofGlobal (U := U) E.global ⟶ D where
  value := E.compare
  local_eq := E.local_eq
  overlap := by
    intro i j x hi hj
    change E.compare j ⟨x,hj⟩ * 1 = D.change i j x hi hj * E.compare i ⟨x,hi⟩
    rw [mul_one, E.overlap]

def Effectuation.toDescentIso {D : F.CocycleDescentData U} (E : D.Effectuation) :
    ofGlobal (U := U) E.global ≅ D :=
  (Groupoid.isoEquivHom _ _).symm E.toDescentHom

/-- Explicit essential-surjectivity witnesses: no global cocycle is assumed in the input. -/
theorem restriction_essentially_surjective (h : CompositionCover U)
    (D : F.CocycleDescentData U) :
    ∃ c : F.GaugeObject (∅ : Set V), Nonempty ((restrictionFunctor F U).obj c ≅ D) :=
  ⟨(D.effectuate h).object, ⟨(D.effectuate h).toDescentIso⟩⟩

end CocycleDescentData
end GroupViewSystem
end KomorebiSpace
