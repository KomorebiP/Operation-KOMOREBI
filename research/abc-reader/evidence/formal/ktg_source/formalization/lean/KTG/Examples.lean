import KTG.Countermodels

namespace KTG
namespace Examples

open Countermodels

/-- Equality transport on the finite Boolean context. -/
def equalityBoolTransport : KTransport boolEqContext boolEqContext where
  Carrier := Bool
  leftRep := fun b => b
  rightRep := fun b => b
  related := Eq
  Obstruction := Unit

/-- Realization certificates carry an actual equality proof. -/
def equalityBoolCertification :
    KTransportCertification equalityBoolTransport where
  Certificate := fun a b => PLift (a = b)
  obstruction := fun _ => ()
  controlled := fun _ => True
  related_of_controlled := fun certificate _ => certificate.down

/-- Identity normalization whose compatibility proposition is equality. -/
def identityBoolNormalization :
    KNormalization boolEqContext boolEqContext where
  GradeA := Bool
  GradeB := Bool
  gradeA := fun b => b
  gradeB := fun b => b
  sigma := fun b => b
  compatible := Eq
  preserves := fun h => Eq.symm h

/-- The identity witness bridge: normalization equality identifies the reference
    object with the raw transported output. -/
def identityBoolWitnessBridge :
    KWitnessBridge equalityBoolTransport equalityBoolCertification
      identityBoolNormalization boolMeasurement boolIdentityHull where
  rawOutput := fun a => a
  witness_preserved := by
    intro a b _ hNormalization
    exact Eq.symm hNormalization

/-- Equality gives a controlled realization for every object transported to
    itself. -/
def identityBoolRealization (b : Bool) :
    CertifiedRealization equalityBoolCertification b b where
  certificate := ⟨rfl⟩
  obstructionControlled := trivial

/-- A concrete monotone observable into the natural-number KTG preorder. -/
def boolNatObservable : KObservable boolEqContext Nat where
  value := fun b => match b with | false => 0 | true => 1
  monotone := by
    intro x y h
    cases h
    exact KPreorder.le_refl _

/-- Positive smoke theorem showing that the full certified transport pipeline is
    constructible and yields a scalar bound. -/
theorem identity_pipeline_scalar_bound (b : Bool) :
    boolNatObservable.value (boolMeasurement.measure b) ≼
      boolNatObservable.value
        (boolIdentityHull.hull (identityBoolWitnessBridge.rawOutput b)) := by
  exact certified_transport_bound
    identityBoolWitnessBridge
    boolNatObservable
    (identityBoolRealization b)
    rfl

end Examples
end KTG
