import KTG.Transport

namespace KTG

universe uA vA uB vB w x c

/-- Application-specific proof objects certifying that a transport relation is
    genuinely realized.  A certificate carries an obstruction value; only a
    controlled obstruction may be converted into structural relatedness. -/
structure KTransportCertification
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport.{uA, vA, uB, vB, w, x} A B) where
  Certificate : A.Obj → B.Obj → Type c
  obstruction : ∀ {a b}, Certificate a b → T.Obstruction
  controlled : T.Obstruction → Prop
  related_of_controlled :
    ∀ {a b} (certificate : Certificate a b),
      controlled (obstruction certificate) → T.Related a b

/-- A realized source/target pair together with explicit obstruction control. -/
structure CertifiedRealization
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    (C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T)
    (a : A.Obj) (b : B.Obj) where
  certificate : C.Certificate a b
  obstructionControlled : C.controlled (C.obstruction certificate)

/-- Propositional form of transported realizability. -/
def TransportedRealizable
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    (C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T)
    (a : A.Obj) (b : B.Obj) : Prop :=
  Nonempty (CertifiedRealization C a b)

/-- A certified realization induces structural relatedness.  The converse is
    intentionally absent. -/
theorem CertifiedRealization.related
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {a : A.Obj} {b : B.Obj}
    (r : CertifiedRealization C a b) :
    T.Related a b :=
  C.related_of_controlled r.certificate r.obstructionControlled

/-- Propositional transported realizability also implies relatedness. -/
theorem transportedRealizable_related
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {a : A.Obj} {b : B.Obj}
    (h : TransportedRealizable C a b) :
    T.Related a b := by
  cases h with
  | intro r => exact r.related

end KTG
