import KomorebiSpace.ReindexedTransports
import Mathlib.CategoryTheory.Types.Basic

set_option autoImplicit false

/-!
# A category of sequential resolutions modulo eventual equality

The quotient is defined by finite-stage agreement, not by equality after
realization. No equivalence with the full pro-category has yet been proved.
-/

universe u v w z
namespace KomorebiSpace
namespace Resolution

abbrev EventualHom (X : Resolution.{u}) (Y : Resolution.{v}) :=
  Quotient (ReindexedMap.eventualSetoid X Y)

namespace EventualHom
variable {X : Resolution.{u}} {Y : Resolution.{v}}
    {Z : Resolution.{w}} {W : Resolution.{z}}

def mk (f : ReindexedMap X Y) : EventualHom X Y := Quotient.mk' f

theorem mk_eq_iff (f g : ReindexedMap X Y) :
    mk f = mk g ↔ ReindexedMap.EventuallyEq f g := Quotient.eq

def id (X : Resolution.{u}) : EventualHom X X := mk (ReindexedMap.id X)

def comp (f : EventualHom X Y) (g : EventualHom Y Z) : EventualHom X Z :=
  Quotient.liftOn₂ f g (fun a b => mk (ReindexedMap.comp a b))
    (by intro a a' b b' ha hb; exact Quotient.sound (ReindexedMap.comp_congr ha hb))

@[simp] theorem mk_comp (f : ReindexedMap X Y) (g : ReindexedMap Y Z) :
    comp (mk f) (mk g) = mk (ReindexedMap.comp f g) := rfl

@[simp] theorem id_comp (f : EventualHom X Y) : comp (id X) f = f := by
  induction f using Quotient.inductionOn with
  | _ f => change mk (ReindexedMap.comp (ReindexedMap.id X) f) = mk f
           rw [ReindexedMap.id_comp]

@[simp] theorem comp_id (f : EventualHom X Y) : comp f (id Y) = f := by
  induction f using Quotient.inductionOn with
  | _ f => change mk (ReindexedMap.comp f (ReindexedMap.id Y)) = mk f
           rw [ReindexedMap.comp_id]

theorem comp_assoc (f : EventualHom X Y) (g : EventualHom Y Z)
    (h : EventualHom Z W) : comp (comp f g) h = comp f (comp g h) := by
  induction f using Quotient.inductionOn with
  | _ f => induction g using Quotient.inductionOn with
    | _ g => induction h using Quotient.inductionOn with
      | _ h => rfl

def onLimit (f : EventualHom X Y) : X.Point → Y.Point :=
  Quotient.liftOn f ReindexedMap.onLimit
    (by intro a b h; exact ReindexedMap.onLimit_congr h)

@[simp] theorem onLimit_mk (f : ReindexedMap X Y) :
    (mk f).onLimit = f.onLimit := rfl

@[simp] theorem onLimit_id (x : X.Point) : (id X).onLimit x = x := rfl

@[simp] theorem onLimit_comp (f : EventualHom X Y) (g : EventualHom Y Z)
    (x : X.Point) : (comp f g).onLimit x = g.onLimit (f.onLimit x) := by
  induction f using Quotient.inductionOn with
  | _ f => induction g using Quotient.inductionOn with
    | _ g => rfl

def ofMap (f : Map X Y) : EventualHom X Y := mk (ReindexedMap.ofMap f)

@[simp] theorem onLimit_ofMap (f : Map X Y) : (ofMap f).onLimit = f.onLimit := rfl

@[simp] theorem ofMap_id : ofMap (Map.id X) = id X := rfl

@[simp] theorem ofMap_comp (f : Map X Y) (g : Map Y Z) :
    ofMap (Map.comp f g) = comp (ofMap f) (ofMap g) := rfl

end EventualHom

/-- Same objects as the concrete resolutions; arrows are eventual classes. -/
instance : CategoryTheory.Category.{u} Resolution.{u} where
  Hom := EventualHom
  id := EventualHom.id
  comp := EventualHom.comp
  id_comp := EventualHom.id_comp
  comp_id := EventualHom.comp_id
  assoc := EventualHom.comp_assoc

open CategoryTheory

/-- Realization is a functor, without a claim that it is faithful or full. -/
def realizationFunctor : Resolution.{u} ⥤ Type u where
  obj := Point
  map := fun f => ↾f.onLimit
  map_id := by intro X; rfl
  map_comp := by
    intro X Y Z f g
    apply ConcreteCategory.hom_ext
    intro x
    exact EventualHom.onLimit_comp f g x

end Resolution
end KomorebiSpace
