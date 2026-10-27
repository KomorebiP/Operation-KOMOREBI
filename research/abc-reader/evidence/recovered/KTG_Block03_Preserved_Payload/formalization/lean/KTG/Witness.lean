import KTG.Hull
import KTG.Observable

namespace KTG

universe u v w

/-- The load-bearing certificate: the reference measurement lies below / inside
    the transported output in the context's comparison relation. -/
def Witness (A : KContext.{u, v}) (reference output : A.MeasureObj) : Prop :=
  A.le reference output

/-- Explicit hull-membership witness.  This is a measurement-level proposition,
    distinct from object-level structural relatedness and from scalar order. -/
def HullWitness
    (A : KContext.{u, v}) (H : KHull A)
    (reference raw : A.MeasureObj) : Prop :=
  Witness A reference (H.hull raw)

/-- A witness plus observable monotonicity yields the scalar bound. -/
theorem witness_bound
    {A : KContext.{u, v}} {Λ : Type w} [KPreorder Λ]
    (Φ : KObservable A Λ)
    {reference output : A.MeasureObj}
    (hW : Witness A reference output) :
    Φ.value reference ≼ Φ.value output :=
  Φ.monotone hW

/-- The standard hull-based certified bound. -/
theorem hull_witness_bound
    {A : KContext.{u, v}} {Λ : Type w} [KPreorder Λ]
    (H : KHull A) (Φ : KObservable A Λ)
    {reference raw : A.MeasureObj}
    (hW : HullWitness A H reference raw) :
    Φ.value reference ≼ Φ.value (H.hull raw) :=
  witness_bound Φ hW

/-- Every measurement object is a witness for its own hull. -/
theorem self_witness_hull
    {A : KContext.{u, v}} (H : KHull A) (x : A.MeasureObj) :
    HullWitness A H x x :=
  H.extensive x

end KTG
