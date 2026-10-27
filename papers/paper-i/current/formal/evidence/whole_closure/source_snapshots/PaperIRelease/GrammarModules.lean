import Mathlib.Algebra.Category.ModuleCat.Basic
import Mathlib.Algebra.Algebra.Tower
import Mathlib.CategoryTheory.Equivalence
import PaperIRelease.GrammarAlgebra

set_option autoImplicit false
set_option maxHeartbeats 2000000
set_option linter.unusedVariables false
set_option linter.unnecessarySimpa false

noncomputable section

namespace Komorebi.PaperIRelease.GrammarModules

open CategoryTheory
open scoped ModuleCat.Algebra

universe u
variable (K A : Type u) [Field K] [Ring A] [Algebra K A]

/-- A unital K-algebra action on a K-vector space. -/
structure ActionObject where
  space : ModuleCat.{u} K
  action : A →ₐ[K] Module.End K space

variable {K A}

/-- Algebra-action morphisms are the actual K-linear intertwiners. -/
structure ActionHom (X Y : ActionObject K A) where
  linearMap : X.space →ₗ[K] Y.space
  commute : ∀ a x, linearMap (X.action a x) = Y.action a (linearMap x)

@[ext] theorem ActionHom.ext {X Y : ActionObject K A}
    (f g : ActionHom X Y) (h : f.linearMap = g.linearMap) : f = g := by
  cases f
  cases g
  cases h
  rfl

instance actionCategory : Category (ActionObject K A) where
  Hom := ActionHom
  id X := ⟨LinearMap.id, fun _ _ => rfl⟩
  comp {X Y Z} f g := ⟨g.linearMap.comp f.linearMap, by
    intro a x
    change g.linearMap (f.linearMap (X.action a x)) = Z.action a (g.linearMap (f.linearMap x))
    rw [f.commute, g.commute]⟩
  id_comp f := by apply ActionHom.ext; rfl
  comp_id f := by apply ActionHom.ext; rfl
  assoc f g h := by apply ActionHom.ext; rfl

/-- Every algebra action induces a genuine unital left module. -/
abbrev ActionObject.module (X : ActionObject K A) : Module A X.space :=
  Module.compHom X.space X.action.toRingHom

abbrev ActionObject.moduleObject (X : ActionObject K A) : ModuleCat.{u} A := by
  letI := X.module
  exact ModuleCat.of A X.space

theorem ActionObject.module_smul (X : ActionObject K A) (a : A) (x : X.space) :
    @SMul.smul A X.space X.module.toSMul a x = X.action a x := rfl

/-- The algebra-action category maps to the ordinary category of all unital A-modules. -/
def toModules : ActionObject K A ⥤ ModuleCat.{u} A where
  obj := ActionObject.moduleObject
  map {X Y} f := by
    letI := X.module
    letI := Y.module
    exact ModuleCat.ofHom
      { toFun := f.linearMap
        map_add' := f.linearMap.map_add
        map_smul' := fun a x => f.commute a x }
  map_id X := by ext x; rfl
  map_comp f g := by ext x; rfl

instance toModules_faithful : (toModules (K := K) (A := A)).Faithful where
  map_injective {X Y} f g h := by
    apply ActionHom.ext
    ext x
    exact congrArg (fun f : X.moduleObject ⟶ Y.moduleObject => f x) h

theorem ActionObject.coefficient_action (X : ActionObject K A) (c : K) (x : X.space) :
    X.action (algebraMap K A c) x = c • x := by
  rw [X.action.commutes]
  rfl

/-- An A-linear map is K-linear because scalar coefficients act through algebraMap. -/
def fromModuleHom {X Y : ActionObject K A} (f : X.moduleObject ⟶ Y.moduleObject) :
    ActionHom X Y where
  linearMap :=
    { toFun := f
      map_add' := f.hom.map_add
      map_smul' := fun c x => by
        change f (c • x) = c • f x
        rw [← X.coefficient_action c x, ← Y.coefficient_action c (f x)]
        exact f.hom.map_smul (algebraMap K A c) x }
  commute a x := f.hom.map_smul a x

instance toModules_full : (toModules (K := K) (A := A)).Full where
  map_surjective f := ⟨fromModuleHom f, by ext x; rfl⟩

/-- The inverse construction starts from any unital A-module, with its canonical K-action. -/
def ofModule (M : ModuleCat.{u} A) : ActionObject K A where
  space := ModuleCat.of K M
  action := Algebra.lsmul K K M

def ofModuleIso (M : ModuleCat.{u} A) : (ofModule (K := K) M).moduleObject ≅ M := by
  letI := (ofModule (K := K) M).module
  exact LinearEquiv.toModuleIso
    { toFun := fun x => x
      invFun := fun x => x
      left_inv := fun _ => rfl
      right_inv := fun _ => rfl
      map_add' := fun _ _ => rfl
      map_smul' := fun _ _ => rfl }

instance toModules_essSurj : (toModules (K := K) (A := A)).EssSurj where
  mem_essImage M := ⟨ofModule M, ⟨ofModuleIso M⟩⟩

instance toModules_isEquivalence : (toModules (K := K) (A := A)).IsEquivalence where

/-- The complete category equivalence with ordinary unital left modules. -/
def actionModuleEquivalence : ActionObject K A ≌ ModuleCat.{u} A :=
  (toModules (K := K) (A := A)).asEquivalence

end Komorebi.PaperIRelease.GrammarModules
