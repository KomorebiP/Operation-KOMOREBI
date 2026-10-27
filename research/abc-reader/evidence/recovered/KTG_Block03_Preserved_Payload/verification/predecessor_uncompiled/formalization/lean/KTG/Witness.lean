import KTG.Hull
import KTG.Observable

namespace KTG

universe u v w

/-- The load-bearing certificate: the reference object lies below / inside the
    transported or hulled output in the comparison order. -/
def Witness (A : KContext.{u, v}) (reference output : A.MeasureObj) : Prop :=
  A.le reference output

/-- A witness plus monotonicity yields the scalar bound. -/
theorem witness_bound
    {A : KContext.{u, v}} {Λ : Type w} [Preorder Λ]
    (Φ : KObservable A Λ)
    {reference output : A.MeasureObj}
    (hW : Witness A reference output) :
    Φ.value reference ≤ Φ.value output :=
  Φ.monotone hW

/-- The standard hull-based certified transport bound. -/
theorem hull_witness_bound
    {A : KContext.{u, v}} {Λ : Type w} [Preorder Λ]
    (H : KHull A) (Φ : KObservable A Λ)
    {reference raw : A.MeasureObj}
    (hW : Witness A reference (H.hull raw)) :
    Φ.value reference ≤ Φ.value (H.hull raw) :=
  witness_bound Φ hW

/-- Every measurement object is a witness for its own hull. -/
theorem self_witness_hull
    {A : KContext.{u, v}} (H : KHull A) (x : A.MeasureObj) :
    Witness A x (H.hull x) :=
  H.extensive x

end KTG
