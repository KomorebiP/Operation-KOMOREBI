import Std

namespace KTG

universe u v

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
