import KomorebiSpace.SectionGluing
import KomorebiSpace.Cofinal
import KomorebiSpace.AdjacentResolution
import Mathlib.CategoryTheory.Category.Preorder

set_option autoImplicit false

/-!
# Existing resolution points are coherent view sections

This connects the new language to the existing all-pairs resolution and its
cofinal equivalence. No original mathematical object is identified with the
section space without a separate realization theorem.
-/
universe u v
namespace KomorebiSpace
open CategoryTheory
namespace Resolution

def views (X : Resolution.{u}) : ViewSystem ℕ where
  Obj := X.Obj
  pull := fun f => X.restrict (leOfHom f)
  pull_id := X.restrict_refl
  pull_comp := fun f g x => (X.restrict_trans (leOfHom f) (leOfHom g) x).symm

/-- A literal bridge to the previously checked inverse-limit point type. -/
def ambientEquiv (X : Resolution.{u}) : X.views.Ambient ≃ X.Point where
  toFun := fun x => ⟨x.val, fun i j h => x.property i j (homOfLE h)⟩
  invFun := fun x => ⟨x.val, fun i j f => x.property i j (leOfHom f)⟩
  left_inv := by intro x; rfl
  right_inv := by intro x; rfl

@[simp] theorem ambientEquiv_coordinate (X : Resolution.{u})
    (x : X.views.Ambient) (n : ℕ) : (X.ambientEquiv x).val n = x.val n := rfl

def Map.viewMorphism {X : Resolution.{u}} {Y : Resolution.{v}} (f : Map X Y) :
    ViewSystem.Morphism X.views Y.views where
  app := f.app
  natural := fun e x => f.exact _ _ (leOfHom e) x

@[simp] theorem Map.viewMorphism_onAmbient {X : Resolution.{u}} {Y : Resolution.{v}}
    (f : Map X Y) (x : X.views.Ambient) :
    Y.ambientEquiv (f.viewMorphism.onAmbient x) = f.onLimit (X.ambientEquiv x) := rfl

noncomputable def cofinalAmbientEquiv (X : Resolution.{u})
    (φ : ℕ → ℕ) (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    X.views.Ambient ≃ (X.reindex φ hφ).views.Ambient :=
  X.ambientEquiv.trans ((cofinalEquiv X φ hφ hcof).trans
    (X.reindex φ hφ).ambientEquiv.symm)

@[simp] theorem cofinalAmbient_coordinate (X : Resolution.{u})
    (φ : ℕ → ℕ) (hφ : Monotone φ) (hcof : UnboundedSchedule φ)
    (x : X.views.Ambient) (n : ℕ) :
    (cofinalAmbientEquiv X φ hφ hcof x).val n = x.val (φ n) := rfl

/-- These patches include every transition, not only every natural-number view. -/
def prefixViews (N : ℕ) : Set ℕ := {n | n ≤ N}

theorem prefixViews_transitionCover : ViewSystem.TransitionCover prefixViews := by
  intro a b f
  exact ⟨b, leOfHom f, Nat.le_refl b⟩

/-- A global section is equivalent to a matching family of finite-prefix sections. -/
noncomputable def prefixSectionEquiv (X : Resolution.{u}) :
    X.views.Ambient ≃ ViewSystem.Matching X.views prefixViews :=
  X.views.gluingEquiv prefixViews prefixViews_transitionCover

theorem prefixes_determine_point (X : Resolution.{u}) {x y : X.Point}
    (h : ∀ N, X.views.restrict (prefixViews N) (X.ambientEquiv.symm x) =
      X.views.restrict (prefixViews N) (X.ambientEquiv.symm y)) : x = y := by
  have he := X.views.restrict_jointly_injective prefixViews
    (ViewSystem.TransitionCover.objectCover prefixViews prefixViews_transitionCover) h
  have hh := congrArg X.ambientEquiv he
  simpa only [Equiv.apply_symm_apply] using hh

end Resolution
end KomorebiSpace
