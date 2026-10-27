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

/-- Structural relatedness induced by the common-carrier representation. -/
def KTransport.Related
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport A B) (a : A.Obj) (b : B.Obj) : Prop :=
  T.related (T.leftRep a) (T.rightRep b)

/-- The predicate of target objects structurally related to a source object.
    It is written as a predicate rather than Mathlib's `Set` so the core remains
    dependency-free. -/
def KTransport.out
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport A B) (a : A.Obj) : B.Obj → Prop :=
  fun b => T.Related a b

/-- Membership in the output predicate is exactly structural relatedness. -/
theorem KTransport.out_iff_related
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport A B) (a : A.Obj) (b : B.Obj) :
    T.out a b ↔ T.Related a b :=
  Iff.rfl

/-- A generic binary relation used to discuss path composition independently of
    a particular carrier implementation. -/
def KRel (X : Type uA) (Y : Type uB) := X → Y → Prop

/-- Relational composition. -/
def KRel.comp
    {X : Type uA} {Y : Type uB} {Z : Type w}
    (R : KRel X Y) (S : KRel Y Z) : KRel X Z :=
  fun x z => ∃ y, R x y ∧ S y z

end KTG
