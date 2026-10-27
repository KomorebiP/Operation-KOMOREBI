import KTG.Basic

namespace KTG

universe u v

/-- Closure/enclosure operator on the measurement objects of an ambient context. -/
structure KHull (A : KContext.{u, v}) where
  hull : A.MeasureObj → A.MeasureObj
  extensive : ∀ x, A.le x (hull x)
  monotone : ∀ {x y}, A.le x y → A.le (hull x) (hull y)
  idempotent : ∀ x, hull (hull x) = hull x

/-- A hull output is fixed by another application of the same hull. -/
theorem KHull.closed
    {A : KContext.{u, v}} (H : KHull A) (x : A.MeasureObj) :
    H.hull (H.hull x) = H.hull x :=
  H.idempotent x

end KTG
