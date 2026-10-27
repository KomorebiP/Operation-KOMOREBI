import Std

namespace KTG

universe u v

/-- A dependency-free preorder interface.  The first KTG checkpoint intentionally
    has no Mathlib dependency, so scalar comparison is carried explicitly rather
    than imported through Mathlib's `Preorder`. -/
class KPreorder (α : Type u) where
  le : α → α → Prop
  le_refl : ∀ x, le x x
  le_trans : ∀ {x y z}, le x y → le y z → le x z

/-- KTG comparison notation for a registered dependency-free preorder. -/
infix:50 " ≼ " => KPreorder.le

/-- The standard natural-number order is available to finite countermodels. -/
instance natKPreorder : KPreorder Nat where
  le := Nat.le
  le_refl := Nat.le_refl
  le_trans := Nat.le_trans

/-- A mathematical ambient context. Objects and measurement objects may live in
    different universes. The relation `le` is the enclosure/comparison order used
    by downstream monotone observables. -/
structure KContext where
  Obj : Type u
  MeasureObj : Type v
  le : MeasureObj → MeasureObj → Prop
  le_refl : ∀ x, le x x
  le_trans : ∀ {x y z}, le x y → le y z → le x z

/-- Equality always supplies a comparison witness. -/
theorem KContext.le_of_eq (A : KContext) {x y : A.MeasureObj} (h : x = y) :
    A.le x y := by
  cases h
  exact A.le_refl x

end KTG
