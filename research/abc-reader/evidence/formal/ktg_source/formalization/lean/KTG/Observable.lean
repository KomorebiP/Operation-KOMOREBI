import KTG.Basic

namespace KTG

universe u v w

/-- A scalar or ordered observable that is monotone for the context's enclosure
    relation.  Its codomain order is the dependency-free `KPreorder`. -/
structure KObservable
    (A : KContext.{u, v}) (Λ : Type w) [KPreorder Λ] where
  value : A.MeasureObj → Λ
  monotone : ∀ {x y}, A.le x y → value x ≼ value y

end KTG
