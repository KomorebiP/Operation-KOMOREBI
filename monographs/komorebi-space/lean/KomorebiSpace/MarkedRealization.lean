import Mathlib.CategoryTheory.Equivalence
import Mathlib.CategoryTheory.Groupoid

set_option autoImplicit false

/-!
# Realizations with an identified boundary

For a functor between groupoids, a realization over b is an object together
with an actual arrow identifying its image with b. Every such arrow is an
isomorphism. Morphisms must commute with the chosen identification. This is
the explicit groupoid homotopy fiber, not the naive equality fiber.
-/
universe u₁ u₂ u₃ u₄ v₁ v₂ v₃ v₄
namespace KomorebiSpace
open CategoryTheory

structure MarkedRealization {C : Type u₁} [Groupoid.{v₁} C]
    {D : Type u₂} [Groupoid.{v₂} D] (F : C ⥤ D) (b : D) where
  obj : C
  identify : F.obj obj ⟶ b

namespace MarkedRealization
variable {C : Type u₁} [Groupoid.{v₁} C]
variable {D : Type u₂} [Groupoid.{v₂} D]
variable {F : C ⥤ D} {b : D}

structure Hom (x y : MarkedRealization F b) where
  val : x.obj ⟶ y.obj
  comm : F.map val ≫ y.identify = x.identify

@[ext] theorem Hom.ext {x y : MarkedRealization F b} {f g : Hom x y}
    (h : f.val = g.val) : f = g := by cases f; cases g; cases h; rfl

def identity (x : MarkedRealization F b) : Hom x x :=
  ⟨𝟙 x.obj, by simp⟩

def compose {x y z : MarkedRealization F b} (f : Hom x y) (g : Hom y z) : Hom x z :=
  ⟨f.val ≫ g.val, by rw [F.map_comp, Category.assoc, g.comm, f.comm]⟩

def reverse {x y : MarkedRealization F b} (f : Hom x y) : Hom y x :=
  ⟨Groupoid.inv f.val, by rw [← f.comm, ← Category.assoc, ← F.map_comp]; simp⟩

instance : Groupoid (MarkedRealization F b) where
  Hom := Hom
  id := identity
  comp := compose
  id_comp := by intros; apply Hom.ext; exact Category.id_comp _
  comp_id := by intros; apply Hom.ext; exact Category.comp_id _
  assoc := by intros; apply Hom.ext; exact Category.assoc _ _ _
  inv := reverse
  inv_comp := by intros; apply Hom.ext; exact Groupoid.inv_comp _
  comp_inv := by intros; apply Hom.ext; exact Groupoid.comp_inv _

@[simp] theorem comp_val {x y z : MarkedRealization F b} (f : x ⟶ y) (g : y ⟶ z) :
    (f ≫ g).val = f.val ≫ g.val := rfl

/-- Forget the boundary identification, but retain the actual underlying morphism. -/
def forget (F : C ⥤ D) (b : D) : MarkedRealization F b ⥤ C where
  obj x := x.obj
  map f := f.val

/-- Nonemptiness means actual membership in the essential image. -/
theorem nonempty_iff (F : C ⥤ D) (b : D) :
    Nonempty (MarkedRealization F b) ↔ ∃ x : C, Nonempty (F.obj x ≅ b) := by
  constructor
  · rintro ⟨x⟩
    exact ⟨x.obj, ⟨(Groupoid.isoEquivHom _ _).symm x.identify⟩⟩
  · rintro ⟨x, ⟨i⟩⟩
    exact ⟨⟨x,i.hom⟩⟩

/-- The identification forces automorphisms to be invisible at the boundary. -/
theorem endomorphism_condition (x : MarkedRealization F b) (a : x.obj ⟶ x.obj) :
    F.map a ≫ x.identify = x.identify ↔ F.map a = 𝟙 (F.obj x.obj) := by
  constructor
  · intro h
    apply (cancel_mono x.identify).mp
    simpa using h
  · intro h
    rw [h, Category.id_comp]

/-- For fixed underlying objects, all allowable comparison witnesses are retained. -/
def homEquiv (x y : MarkedRealization F b) :
    (x ⟶ y) ≃ {a : x.obj ⟶ y.obj // F.map a ≫ y.identify = x.identify} where
  toFun a := ⟨a.val,a.comm⟩
  invFun a := ⟨a.val,a.property⟩
  left_inv _ := rfl
  right_inv _ := rfl

end MarkedRealization
end KomorebiSpace
