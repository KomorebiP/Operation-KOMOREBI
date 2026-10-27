import KTG.IUT312Normalization

namespace KTG
namespace IUT312

universe u v s

/-- The exact open Step (xi-e) → Step (xi-f) theorem.  It asserts q-pilot hull
containment from a source-level IPL/SHE/APT realization and the explicit
normalization chain.  This proposition is not inhabited by the present file. -/
def StepXiEWitnessPreservation
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D) : Prop :=
  ∀ {out : D.MultiradialOutputPackage} {q : D.FixedQPilot},
    CertifiedRealization (certification D S) out q →
    NormalizationWitness (directNormalization D N) out q →
    QPilotHullContainment D out q

/-- A named source theorem wrapper.  Constructing this object is exactly the
remaining source-specific mathematical obligation. -/
structure SourceWitnessTheorem
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D) : Prop where
  witness_preserved : StepXiEWitnessPreservation D S N

/-- An actual source witness theorem instantiates the generic KTG witness bridge.
No bridge can be constructed here without supplying that theorem. -/
def witnessBridgeOfSourceTheorem
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D)
    (W : SourceWitnessTheorem D S N) :
    KWitnessBridge
      (transport D S)
      (certification D S)
      (directNormalization D N)
      (qPilotMeasurementMap D)
      (targetHull D) where
  rawOutput := rawOutputMeasurement D
  witness_preserved := by
    intro out q realization normalization
    exact W.witness_preserved realization normalization

/-- Source-faithful form of the scalar conclusion.  The only application-specific
premise not already packaged by realization and normalization is the named
source witness theorem. -/
theorem scalarBoundOfSourceWitness
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D)
    (W : SourceWitnessTheorem D S N)
    {Λ : Type s} [KPreorder Λ]
    (Φ : KObservable (targetContext D) Λ)
    {out : D.MultiradialOutputPackage}
    {q : D.FixedQPilot}
    (realization : CertifiedRealization (certification D S) out q)
    (normalization : NormalizationWitness (directNormalization D N) out q) :
    Φ.value (D.qPilotMeasurement q) ≼
      Φ.value (D.holomorphicHull (rawOutputMeasurement D out)) := by
  exact certified_transport_bound
    (witnessBridgeOfSourceTheorem D S N W)
    Φ realization normalization

/-- A complete source-specific certificate keeps the witness theorem visibly
separate from the pre-witness realization and normalization data. -/
structure SourceBoundCertificate
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D)
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) where
  realization : CertifiedRealization (certification D S) out q
  normalization : NormalizationWitness (directNormalization D N) out q
  witness : QPilotHullContainment D out q

/-- Once a concrete containment witness is supplied, the scalar bound follows
without postulating a global source theorem. -/
theorem scalarBoundOfConcreteCertificate
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D)
    {Λ : Type s} [KPreorder Λ]
    (Φ : KObservable (targetContext D) Λ)
    {out : D.MultiradialOutputPackage}
    {q : D.FixedQPilot}
    (certificate : SourceBoundCertificate D S N out q) :
    Φ.value (D.qPilotMeasurement q) ≼
      Φ.value (D.holomorphicHull (rawOutputMeasurement D out)) :=
  hull_witness_bound
    (targetHull D)
    Φ
    certificate.witness

end IUT312
end KTG
