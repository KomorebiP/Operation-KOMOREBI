import Mathlib.CategoryTheory.Preadditive.Basic
import Mathlib.Tactic.Abel

set_option autoImplicit false

/-! Typed compatibility defects in a preadditive category. -/
universe u v
namespace KomorebiSpace
open CategoryTheory
namespace Squares
variable {C : Type u} [Category.{v} C] [Preadditive C]

def defect {A B A' B' : C} (f : A ⟶ B) (f' : A' ⟶ B')
    (u : A ⟶ A') (v : B ⟶ B') : A ⟶ B' := f ≫ v - u ≫ f'

theorem zero_iff {A B A' B' : C} (f : A ⟶ B) (f' : A' ⟶ B')
    (u : A ⟶ A') (v : B ⟶ B') :
    defect f f' u v = 0 ↔ f ≫ v = u ≫ f' := sub_eq_zero

/-- Horizontal pasting, with all defects transported into a common Hom group. -/
theorem horizontal {A B D A' B' D' : C}
    (f : A ⟶ B) (g : B ⟶ D) (f' : A' ⟶ B') (g' : B' ⟶ D')
    (u : A ⟶ A') (v : B ⟶ B') (w : D ⟶ D') :
    defect (f ≫ g) (f' ≫ g') u w =
      f ≫ defect g g' v w + defect f f' u v ≫ g' := by
  simp only [defect, Preadditive.comp_sub, Preadditive.sub_comp, Category.assoc]
  abel

/-- Vertical pasting. -/
theorem vertical {A B A' B' A'' B'' : C}
    (f : A ⟶ B) (f' : A' ⟶ B') (f'' : A'' ⟶ B'')
    (u : A ⟶ A') (v : B ⟶ B') (u' : A' ⟶ A'') (v' : B' ⟶ B'') :
    defect f f'' (u ≫ u') (v ≫ v') =
      defect f f' u v ≫ v' + u ≫ defect f' f'' u' v' := by
  simp only [defect, Preadditive.comp_sub, Preadditive.sub_comp, Category.assoc]
  abel

theorem horizontal_flat {A B D A' B' D' : C}
    (f : A ⟶ B) (g : B ⟶ D) (f' : A' ⟶ B') (g' : B' ⟶ D')
    (u : A ⟶ A') (v : B ⟶ B') (w : D ⟶ D')
    (hf : defect f f' u v = 0) (hg : defect g g' v w = 0) :
    defect (f ≫ g) (f' ≫ g') u w = 0 := by
  rw [horizontal, hf, hg]; simp

theorem vertical_flat {A B A' B' A'' B'' : C}
    (f : A ⟶ B) (f' : A' ⟶ B') (f'' : A'' ⟶ B'')
    (u : A ⟶ A') (v : B ⟶ B') (u' : A' ⟶ A'') (v' : B' ⟶ B'')
    (h₁ : defect f f' u v = 0) (h₂ : defect f' f'' u' v' = 0) :
    defect f f'' (u ≫ u') (v ≫ v') = 0 := by
  rw [vertical, h₁, h₂]; simp
end Squares
end KomorebiSpace
