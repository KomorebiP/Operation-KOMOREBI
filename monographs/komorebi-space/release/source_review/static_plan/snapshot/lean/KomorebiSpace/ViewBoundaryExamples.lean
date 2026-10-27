import KomorebiSpace.ViewCorrespondence
import Mathlib.CategoryTheory.Category.Preorder
import Mathlib.Order.Fin.Basic

set_option autoImplicit false

/-!
# Boundary examples for ambient sections and local correspondence

(1) Covering the objects, without their transitions, need not permit gluing.
(2) Every fiber can be nonempty and every transport invertible, while there is
    no coherent global section.
(3) An invertible transport need not be the identity.
-/
namespace KomorebiSpace
open CategoryTheory ViewSystem
namespace ViewBoundaryExamples

/-- Two separate singleton patches fail to include the arrow 0 -> 1. -/
def singletonPatches : Fin 2 → Set (Fin 2) := fun i => {i}

theorem singleton_objectCover : ObjectCover singletonPatches := by
  intro a
  exact ⟨a, rfl⟩

def separatedLocals : Matching (ViewSystem.constant (Fin 2) Bool) singletonPatches where
  localSection i := ⟨fun _ => decide (i = 1), by intros; rfl⟩
  agree := by
    intro i j a hi hj
    have hi' : a = i := hi
    have hj' : a = j := hj
    have hij : i = j := hi'.symm.trans hj'
    change decide (i = 1) = decide (j = 1)
    rw [hij]

theorem singleton_matching_not_gluable :
    ¬ ∃ s : (ViewSystem.constant (Fin 2) Bool).Ambient,
      ∀ i, (ViewSystem.constant (Fin 2) Bool).restrict (singletonPatches i) s =
        separatedLocals.localSection i := by
  rintro ⟨s, hs⟩
  have h0 : s.val 0 = false :=
    congrArg (fun t : (ViewSystem.constant (Fin 2) Bool).Partial (singletonPatches 0) =>
      t.val ⟨0, rfl⟩) (hs 0)
  have h1 : s.val 1 = true :=
    congrArg (fun t : (ViewSystem.constant (Fin 2) Bool).Partial (singletonPatches 1) =>
      t.val ⟨1, rfl⟩) (hs 1)
  have he := s.property 0 1 (homOfLE (by decide))
  change s.val 1 = s.val 0 at he
  rw [h0, h1] at he
  cases he

theorem singleton_not_transitionCover : ¬ TransitionCover singletonPatches := by
  intro h
  obtain ⟨s, hs, _⟩ := separatedLocals.exists_unique_glue h
  exact singleton_matching_not_gluable ⟨s, hs⟩

inductive LoopView where
  | only
  deriving DecidableEq

/-- The one-object category with the group of order two as its arrows. -/
instance : Category LoopView where
  Hom _ _ := Bool
  id _ := false
  comp f g := Bool.xor f g
  id_comp := by intro a b f; cases f <;> rfl
  comp_id := by intro a b f; cases f <;> rfl
  assoc := by intro a b c d f g h; cases f <;> cases g <;> cases h <;> rfl

/-- The nonidentity loop swaps the two available local realizations. -/
def swapViews : ViewSystem LoopView where
  Obj _ := Bool
  pull := fun f x => Bool.xor f x
  pull_id := by intro a x; cases x <;> rfl
  pull_comp := by intro a b c f g x; cases f <;> cases g <;> cases x <;> rfl

theorem swap_fibers_nonempty (a : LoopView) : Nonempty (swapViews.Obj a) := ⟨false⟩

theorem xor_bijective (f : Bool) : Function.Bijective (fun x : Bool => Bool.xor f x) := by
  constructor
  · intro x y h
    cases f <;> cases x <;> cases y <;> simp_all
  · intro y
    refine ⟨Bool.xor f y, ?_⟩
    cases f <;> cases y <;> rfl

theorem swap_transports_bijective (a b : LoopView) (f : a ⟶ b) :
    Function.Bijective (swapViews.pull f) := xor_bijective f

theorem swap_no_ambient : ¬ Nonempty swapViews.Ambient := by
  rintro ⟨s⟩
  have h := s.property LoopView.only LoopView.only true
  change Bool.xor true (s.val LoopView.only) = s.val LoopView.only at h
  cases he : s.val LoopView.only <;> simp [he] at h

theorem bijective_not_identity :
    Function.Bijective (fun x : Bool => Bool.xor true x) ∧
      (fun x : Bool => Bool.xor true x) ≠ _root_.id := by
  constructor
  · exact xor_bijective true
  · intro h
    have he := congrFun h false
    cases he

def unitProjection : Morphism swapViews (ViewSystem.constant LoopView Unit) where
  app := fun _ _ => ()
  natural := by intros; rfl

def unitAmbient : (ViewSystem.constant LoopView Unit).Ambient :=
  ViewSystem.constantSection LoopView ()

theorem local_bridges_nonempty (a : LoopView) :
    Nonempty ((bridgeSystem unitProjection unitProjection unitAmbient unitAmbient).Obj a) :=
  ⟨⟨false, rfl, rfl⟩⟩

theorem no_global_bridge :
    ¬ Nonempty (GlobalBridge unitProjection unitProjection unitAmbient unitAmbient) := by
  rintro ⟨s⟩
  exact swap_no_ambient ⟨s.val⟩

end ViewBoundaryExamples
end KomorebiSpace
