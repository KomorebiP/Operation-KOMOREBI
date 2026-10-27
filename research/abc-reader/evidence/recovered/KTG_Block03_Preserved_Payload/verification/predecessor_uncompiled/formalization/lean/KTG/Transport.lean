import KTG.Basic

namespace KTG

universe uA vA uB vB w x

/-- Transport is represented by two maps into a common carrier plus a relation,
    rather than being forced to be an ordinary function between object types. -/
structure KTransport
    (A : KContext.{uA, vA}) (B : KContext.{uB, vB}) where
  Carrier : Type w
  leftRep : A.Obj → Carrier
  rightRep : B.Obj → Carrier
  related : Carrier → Carrier → Prop
  Obstruction : Type x

/-- The set of target objects related to a source object by a transport. -/
def KTransport.out
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport A B) (a : A.Obj) : Set B.Obj :=
  { b | T.related (T.leftRep a) (T.rightRep b) }

/-- A generic binary relation used to discuss path composition independently of
    a particular carrier implementation. -/
def KRel (X : Type uA) (Y : Type uB) := X → Y → Prop

/-- Relational composition. -/
def KRel.comp
    {X : Type uA} {Y : Type uB} {Z : Type w}
    (R : KRel X Y) (S : KRel Y Z) : KRel X Z :=
  fun x z => ∃ y, R x y ∧ S y z

end KTG
