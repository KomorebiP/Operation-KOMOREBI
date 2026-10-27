import KomorebiSpace.Towers
import KomorebiSpace.Correction

set_option autoImplicit false

/-!
# The obstruction quotient for actual resolution-tower defects

This module connects the categorical and additive cores. The residual operator
is constructed from the bonding arrows, not supplied as an unrelated map.
A semantic observable restricts corrections and prevents trivial zero-map repair.
-/
universe u v w
namespace KomorebiSpace
namespace TowerCorrection
open CategoryTheory
variable {C : Type u} [Category.{v} C] [Preadditive C]

abbrev Candidates (X Y : Tower C) := ∀ n, X.obj n ⟶ Y.obj n
abbrev Residuals (X Y : Tower C) := ∀ n, X.obj (n+1) ⟶ Y.obj n

def asPreHom {X Y : Tower C} (f : Candidates X Y) : Tower.PreHom X Y := ⟨f⟩

/-- The linear naturality differential on a fixed resolution schedule. -/
def differential (X Y : Tower C) : Candidates X Y →+ Residuals X Y where
  toFun f n := f (n+1) ≫ Y.down n - X.down n ≫ f n
  map_zero' := by
    funext n
    simp
  map_add' := by
    intro f g
    funext n
    simp only [Pi.add_apply, Preadditive.add_comp, Preadditive.comp_add]
    abel

@[simp] theorem differential_apply (X Y : Tower C) (f : Candidates X Y) (n : ℕ) :
    differential X Y f n = Tower.PreHom.defect (asPreHom f) n := rfl

theorem exact_iff_differential_zero (X Y : Tower C) (f : Candidates X Y) :
    (asPreHom f).Exact ↔ differential X Y f = 0 := by
  rw [Tower.PreHom.exact_iff_defect_zero]
  constructor
  · intro h
    funext n
    exact h n
  · intro h n
    exact congrFun h n

variable {S : Type w} [AddCommGroup S]

def problem (X Y : Tower C) (p : Candidates X Y →+ S) :
    CorrectionProblem (Candidates X Y) (Residuals X Y) S :=
  ⟨differential X Y, p⟩

/-- A genuine obstruction criterion for semantic-preserving tower repair. -/
theorem obstruction_zero_iff_exact (X Y : Tower C) (p : Candidates X Y →+ S)
    (f : Candidates X Y) :
    (problem X Y p).obstruction f = 0 ↔
      ∃ g : Candidates X Y, (asPreHom g).Exact ∧ p g = p f := by
  rw [(problem X Y p).flatten_iff]
  constructor
  · rintro ⟨g, hd, hp⟩
    exact ⟨g, (exact_iff_differential_zero X Y g).2 hd, hp⟩
  · rintro ⟨g, hg, hp⟩
    exact ⟨g, (exact_iff_differential_zero X Y g).1 hg, hp⟩

/-- Exact repair descends to a real map on inverse-limit points in a realization model;
this theorem packages the categorical exact transport itself, before realization. -/
theorem obstruction_zero_iff_exactHom (X Y : Tower C) (p : Candidates X Y →+ S)
    (f : Candidates X Y) :
    (problem X Y p).obstruction f = 0 ↔
      ∃ g : Tower.ExactHom X Y, p g.toPreHom.app = p f := by
  rw [obstruction_zero_iff_exact]
  constructor
  · rintro ⟨g, hg, hp⟩
    exact ⟨⟨asPreHom g, hg⟩, hp⟩
  · rintro ⟨g, hp⟩
    exact ⟨g.toPreHom.app, g.exact, hp⟩

end TowerCorrection
end KomorebiSpace
