import KTG.Certification
import KTG.Normalization
import KTG.Witness

namespace KTG

universe uA vA uB vB w x c s

/-- A typed measurement map from mathematical objects to the measurement space
    in which hull membership is stated. -/
structure KMeasurementMap (A : KContext.{uA, vA}) where
  measure : A.Obj → A.MeasureObj

/-- The application-specific, load-bearing bridge from certified transport and
    normalization to hull membership.  Instantiating this structure is the exact
    obligation that may not be replaced by vague structural comparability. -/
structure KWitnessBridge
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport.{uA, vA, uB, vB, w, x} A B)
    (C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T)
    (N : KNormalization A B)
    (μ : KMeasurementMap B)
    (H : KHull B) where
  rawOutput : A.Obj → B.MeasureObj
  witness_preserved :
    ∀ {a b},
      CertifiedRealization C a b →
      NormalizationWitness N a b →
      HullWitness B H (μ.measure b) (rawOutput a)

/-- Complete certificate for one transport bound.  Its fields preserve the proof
    boundary between realization, obstruction control, normalization, and hull
    membership. -/
structure CertifiedTransportBound
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    (T : KTransport.{uA, vA, uB, vB, w, x} A B)
    (C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T)
    (N : KNormalization A B)
    (μ : KMeasurementMap B)
    (H : KHull B)
    (rawOutput : A.Obj → B.MeasureObj)
    (a : A.Obj) (b : B.Obj) where
  realization : CertifiedRealization C a b
  normalization : NormalizationWitness N a b
  hullWitness : HullWitness B H (μ.measure b) (rawOutput a)

/-- Build the complete certificate from an explicit witness-preservation bridge. -/
def CertifiedTransportBound.fromBridge
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {N : KNormalization A B}
    {μ : KMeasurementMap B}
    {H : KHull B}
    (bridge : KWitnessBridge T C N μ H)
    {a : A.Obj} {b : B.Obj}
    (r : CertifiedRealization C a b)
    (n : NormalizationWitness N a b) :
    CertifiedTransportBound T C N μ H bridge.rawOutput a b :=
  { realization := r
    normalization := n
    hullWitness := bridge.witness_preserved r n }

/-- A complete transport-bound certificate yields structural relatedness. -/
theorem CertifiedTransportBound.related
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {N : KNormalization A B}
    {μ : KMeasurementMap B}
    {H : KHull B}
    {rawOutput : A.Obj → B.MeasureObj}
    {a : A.Obj} {b : B.Obj}
    (cert : CertifiedTransportBound T C N μ H rawOutput a b) :
    T.Related a b :=
  cert.realization.related

/-- A complete transport-bound certificate exposes its grade equation. -/
theorem CertifiedTransportBound.normalization_eq
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {N : KNormalization A B}
    {μ : KMeasurementMap B}
    {H : KHull B}
    {rawOutput : A.Obj → B.MeasureObj}
    {a : A.Obj} {b : B.Obj}
    (cert : CertifiedTransportBound T C N μ H rawOutput a b) :
    N.gradeB b = N.sigma (N.gradeA a) :=
  normalization_grade_eq N cert.normalization

/-- Generic certified transport bound: only after all transport, obstruction,
    normalization, hull, and witness obligations have been packaged may scalar
    monotonicity be applied. -/
theorem CertifiedTransportBound.scalar_bound
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {N : KNormalization A B}
    {μ : KMeasurementMap B}
    {H : KHull B}
    {rawOutput : A.Obj → B.MeasureObj}
    {a : A.Obj} {b : B.Obj}
    {Λ : Type s} [KPreorder Λ]
    (cert : CertifiedTransportBound T C N μ H rawOutput a b)
    (Φ : KObservable B Λ) :
    Φ.value (μ.measure b) ≼ Φ.value (H.hull (rawOutput a)) :=
  hull_witness_bound H Φ cert.hullWitness

/-- One-line form of the full certified pipeline. -/
theorem certified_transport_bound
    {A : KContext.{uA, vA}} {B : KContext.{uB, vB}}
    {T : KTransport.{uA, vA, uB, vB, w, x} A B}
    {C : KTransportCertification.{uA, vA, uB, vB, w, x, c} T}
    {N : KNormalization A B}
    {μ : KMeasurementMap B}
    {H : KHull B}
    (bridge : KWitnessBridge T C N μ H)
    {a : A.Obj} {b : B.Obj}
    {Λ : Type s} [KPreorder Λ]
    (Φ : KObservable B Λ)
    (r : CertifiedRealization C a b)
    (n : NormalizationWitness N a b) :
    Φ.value (μ.measure b) ≼ Φ.value (H.hull (bridge.rawOutput a)) :=
  (CertifiedTransportBound.fromBridge bridge r n).scalar_bound Φ

end KTG
