import KTG.IUT312WitnessObligation
import KTG.IUT312Model

namespace KTG
namespace IUT312

universe u v s

/-- Refine the Block 02 logical `Cor312Interface` by the typed Block 03 model. -/
def cor312Interface
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D)
    {Λ : Type s} [KPreorder Λ]
    (Φ : KObservable (targetContext D) Λ)
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) : Cor312Interface Λ where
  qVolume := Φ.value (D.qPilotMeasurement q)
  thetaBound := Φ.value (D.holomorphicHull (rawOutputMeasurement D out))
  structuralLinked := (transport D S).Related out q
  transportedRealizable := TransportedRealizable (certification D S) out q
  normalizationPreserved := NormalizationWitness (directNormalization D N) out q
  hullWitness := QPilotHullContainment D out q
  hullWitness_sound := by
    intro containment
    exact hull_witness_bound (targetHull D) Φ containment

/-- In the refined interface, `Witness312` is exactly q-pilot hull containment. -/
theorem witness312_iff_qPilotHullContainment
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (N : NormalizationData D)
    {Λ : Type s} [KPreorder Λ]
    (Φ : KObservable (targetContext D) Λ)
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) :
    Witness312 (cor312Interface D S N Φ out q) ↔
      QPilotHullContainment D out q :=
  Iff.rfl

/-- A source witness theorem upgrades a typed realization and normalization into
the complete Block 02 abstract certificate. -/
theorem cor312CertificateOfSourceWitness
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
    Cor312Certificate (cor312Interface D S N Φ out q) where
  structural := realization.related
  realization := ⟨realization⟩
  normalization := normalization
  witness := W.witness_preserved realization normalization

/-- The typed source route and the abstract Block 02 route produce the same
scalar target once the open witness theorem is supplied. -/
theorem cor312ScalarBoundOfSourceWitness
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
      Φ.value (D.holomorphicHull (rawOutputMeasurement D out)) :=
  cor312_scalar_of_certificate
    (cor312CertificateOfSourceWitness D S N W Φ realization normalization)

end IUT312
end KTG
