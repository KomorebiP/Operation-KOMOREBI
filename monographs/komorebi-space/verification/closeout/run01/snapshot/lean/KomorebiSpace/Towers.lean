import Mathlib.CategoryTheory.Preadditive.Basic
import Mathlib.Tactic.Abel

set_option autoImplicit false

/-!
# Sequential resolution towers and strict levelwise transports

Bonding arrows point from finer to coarser levels. Exact transports are natural
levelwise maps on the fixed schedule. No identification with all pro-morphisms
is asserted: reindexing and eventual-equality localization are separate work.
-/

universe u v
namespace KomorebiSpace
open CategoryTheory

structure Tower (C : Type u) [Category.{v} C] where
  obj : ℕ → C
  down : ∀ n, obj (n + 1) ⟶ obj n

namespace Tower
variable {C : Type u} [Category.{v} C]

structure PreHom (X Y : Tower C) where
  app : ∀ n, X.obj n ⟶ Y.obj n

namespace PreHom
variable {X Y Z W : Tower C}

@[ext] theorem ext {f g : PreHom X Y} (h : ∀ n, f.app n = g.app n) : f = g := by
  cases f with
  | mk f => cases g with
    | mk g => congr; exact funext h

def id (X : Tower C) : PreHom X X := ⟨fun n => 𝟙 (X.obj n)⟩
def comp (f : PreHom X Y) (g : PreHom Y Z) : PreHom X Z :=
  ⟨fun n => f.app n ≫ g.app n⟩

def Exact (f : PreHom X Y) : Prop :=
  ∀ n, f.app (n + 1) ≫ Y.down n = X.down n ≫ f.app n

@[simp] theorem id_comp (f : PreHom X Y) : comp (id X) f = f := by
  ext n; simp [comp, id]
@[simp] theorem comp_id (f : PreHom X Y) : comp f (id Y) = f := by
  ext n; simp [comp, id]
theorem comp_assoc (f : PreHom X Y) (g : PreHom Y Z) (h : PreHom Z W) :
    comp (comp f g) h = comp f (comp g h) := by
  ext n; simp [comp, Category.assoc]

theorem exact_id (X : Tower C) : Exact (id X) := by
  intro n; simp [id]

theorem exact_comp {f : PreHom X Y} {g : PreHom Y Z}
    (hf : Exact f) (hg : Exact g) : Exact (comp f g) := by
  intro n
  change (f.app (n+1) ≫ g.app (n+1)) ≫ Z.down n =
    X.down n ≫ (f.app n ≫ g.app n)
  rw [Category.assoc, hg n, ← Category.assoc, hf n, Category.assoc]

section Additive
variable [Preadditive C]

def defect (f : PreHom X Y) (n : ℕ) : X.obj (n+1) ⟶ Y.obj n :=
  f.app (n+1) ≫ Y.down n - X.down n ≫ f.app n

theorem exact_iff_defect_zero (f : PreHom X Y) :
    Exact f ↔ ∀ n, defect f n = 0 := by
  simp [Exact, defect, sub_eq_zero]

@[simp] theorem defect_id (X : Tower C) (n : ℕ) : defect (id X) n = 0 := by
  simp [defect, id]

/-- The exact Leibniz law; there is no additional mixed-error term. -/
theorem defect_comp (f : PreHom X Y) (g : PreHom Y Z) (n : ℕ) :
    defect (comp f g) n =
      f.app (n+1) ≫ defect g n + defect f n ≫ g.app n := by
  simp only [defect, comp, Preadditive.comp_sub, Preadditive.sub_comp, Category.assoc]
  abel

def zero (X Y : Tower C) : PreHom X Y := ⟨fun _ => 0⟩

/-- Compatibility residual alone cannot exclude the zero transport. -/
theorem exact_zero (X Y : Tower C) : Exact (zero X Y) := by
  intro n; simp [zero]

@[simp] theorem defect_zero (X Y : Tower C) (n : ℕ) :
    defect (zero X Y) n = 0 := by
  simp [defect, zero]

end Additive
end PreHom

structure ExactHom (X Y : Tower C) where
  toPreHom : PreHom X Y
  exact : toPreHom.Exact

namespace ExactHom
variable {X Y Z W : Tower C}
@[ext] theorem ext {f g : ExactHom X Y}
    (h : ∀ n, f.toPreHom.app n = g.toPreHom.app n) : f = g := by
  have hg : f.toPreHom = g.toPreHom := PreHom.ext h
  cases f; cases g; simp_all

def id (X : Tower C) : ExactHom X X := ⟨PreHom.id X, PreHom.exact_id X⟩
def comp (f : ExactHom X Y) (g : ExactHom Y Z) : ExactHom X Z :=
  ⟨f.toPreHom.comp g.toPreHom, PreHom.exact_comp f.exact g.exact⟩
end ExactHom

/-- The exact core is the category of strict natural levelwise transports. -/
instance : Category (Tower C) where
  Hom := ExactHom
  id := ExactHom.id
  comp := ExactHom.comp
  id_comp := by intros; ext n; simp [ExactHom.comp, ExactHom.id, PreHom.comp, PreHom.id]
  comp_id := by intros; ext n; simp [ExactHom.comp, ExactHom.id, PreHom.comp, PreHom.id]
  assoc := by intros; ext n; simp [ExactHom.comp, PreHom.comp, Category.assoc]

end Tower
end KomorebiSpace
