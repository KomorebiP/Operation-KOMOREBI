import KomorebiSpace.SectionObstruction
import Mathlib.CategoryTheory.Category.Preorder
import Mathlib.Order.Fin.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# A prescribed local integer extends exactly when its parity permits it

There are two views 0 -> 1, with integer fibers. Restriction from view 1 to
view 0 is multiplication by two. A prescribed value k at view 0 has a coherent
extension iff k is even. This is checked through the actual extension class.
-/
namespace KomorebiSpace
open CategoryTheory
namespace SectionExtensionExample

def doubleMap : ℤ →+ ℤ where
  toFun x := 2 * x
  map_zero' := by simp
  map_add' := by intro x y; exact mul_add 2 x y

def integerViews : AdditiveViewSystem (Fin 2) (fun _ => ℤ) where
  pull := fun {a b} _ => if a = b then AddMonoidHom.id ℤ else doubleMap
  pull_id := by intro a x; simp
  pull_comp := by
    intro a b c f g x
    have hab := leOfHom f
    have hbc := leOfHom g
    fin_cases a <;> fin_cases b <;> fin_cases c
    all_goals simp_all [doubleMap]

def prescribedView : Set (Fin 2) := {0}

def localInteger (k : ℤ) : integerViews.views.Partial prescribedView :=
  ⟨fun _ => k, by
    intro a b f
    have ha : a.val = 0 := a.property
    have hb : b.val = 0 := b.property
    have hab : a.val = b.val := ha.trans hb.symm
    change (if a.val = b.val then AddMonoidHom.id ℤ else doubleMap) k = k
    simp [hab]⟩

def globalInteger (m : ℤ) : integerViews.views.Ambient :=
  ⟨fun a => if a = 0 then 2*m else m, by
    intro a b f
    have hab := leOfHom f
    fin_cases a <;> fin_cases b
    all_goals simp_all [AdditiveViewSystem.views, integerViews, doubleMap]⟩

@[simp] theorem globalInteger_zero (m : ℤ) : (globalInteger m).val 0 = 2*m := rfl
@[simp] theorem globalInteger_one (m : ℤ) : (globalInteger m).val 1 = m := rfl

theorem globalInteger_restrict (m : ℤ) :
    integerViews.views.restrict prescribedView (globalInteger m) = localInteger (2*m) := by
  apply ViewSystem.Partial.ext
  intro a
  have ha : a.val = 0 := a.property
  change (if a.val = 0 then 2*m else m) = 2*m
  simp [ha]

/-- A genuine congruence obstruction to extending a coherent partial section. -/
theorem extensionClass_zero_iff_even (k : ℤ) :
    integerViews.extensionClass prescribedView (localInteger k) = 0 ↔
      ∃ m : ℤ, k = 2*m := by
  rw [integerViews.extensionClass_zero_iff]
  constructor
  · rintro ⟨⟨s, hs⟩⟩
    have h0 : s.val 0 = k :=
      congrArg (fun x : integerViews.views.Partial prescribedView => x.val ⟨0, rfl⟩) hs
    have hc := s.property 0 1 (homOfLE (by decide))
    change (2 : ℤ) * (show ℤ from s.val 1) = (show ℤ from s.val 0) at hc
    exact ⟨s.val 1, h0.symm.trans hc.symm⟩
  · rintro ⟨m, rfl⟩
    exact ⟨⟨globalInteger m, globalInteger_restrict m⟩⟩

theorem odd_seed_obstructed :
    integerViews.extensionClass prescribedView (localInteger 1) ≠ 0 := by
  intro h
  obtain ⟨m, hm⟩ := (extensionClass_zero_iff_even 1).mp h
  omega

theorem nonzero_seed_extends :
    Nonempty (integerViews.views.Extensions prescribedView (localInteger 2)) :=
  ⟨⟨globalInteger 1, globalInteger_restrict 1⟩⟩

end SectionExtensionExample
end KomorebiSpace
