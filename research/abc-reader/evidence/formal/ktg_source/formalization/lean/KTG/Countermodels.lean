import KTG.CertifiedBound

namespace KTG
namespace Countermodels

/-- A tiny equality-ordered context used only to separate the logical gates in
    the transport-bound pipeline. -/
def boolEqContext : KContext where
  Obj := Bool
  MeasureObj := Bool
  le := Eq
  le_refl := fun _ => rfl
  le_trans := fun h₁ h₂ => Eq.trans h₁ h₂

/-- Every object pair is structurally related. -/
def universalBoolTransport : KTransport boolEqContext boolEqContext where
  Carrier := Unit
  leftRep := fun _ => ()
  rightRep := fun _ => ()
  related := fun _ _ => True
  Obstruction := Unit

/-- A certification interface with no realizable certificates. -/
def emptyBoolCertification : KTransportCertification universalBoolTransport where
  Certificate := fun _ _ => Empty
  obstruction := fun certificate => nomatch certificate
  controlled := fun _ => True
  related_of_controlled := fun certificate _ => nomatch certificate

/-- Structural relatedness does not imply transported realizability. -/
theorem structural_relation_does_not_imply_realizability :
    universalBoolTransport.Related false true ∧
      ¬ TransportedRealizable emptyBoolCertification false true := by
  constructor
  · trivial
  · intro h
    cases h with
    | intro r => exact nomatch r.certificate

/-- A certification interface in which every object pair has a controlled unit
    certificate. -/
def unitBoolCertification : KTransportCertification universalBoolTransport where
  Certificate := fun _ _ => Unit
  obstruction := fun _ => ()
  controlled := fun _ => True
  related_of_controlled := fun _ _ => trivial

/-- Trivial normalization data certify every pair, without asserting anything
    about measurement-level hull membership. -/
def trivialBoolNormalization : KNormalization boolEqContext boolEqContext where
  GradeA := Unit
  GradeB := Unit
  gradeA := fun _ => ()
  gradeB := fun _ => ()
  sigma := fun _ => ()
  compatible := fun _ _ => True
  preserves := fun _ => rfl

/-- Identity measurement map. -/
def boolMeasurement : KMeasurementMap boolEqContext where
  measure := fun b => b

/-- Identity hull for the equality comparison relation. -/
def boolIdentityHull : KHull boolEqContext where
  hull := fun b => b
  extensive := fun _ => rfl
  monotone := fun h => h
  idempotent := fun _ => rfl

/-- Even structural relation, controlled realization, and normalization together
    do not imply the measurement-level hull witness.  A separate witness bridge
    is therefore logically necessary. -/
theorem prewitness_gates_do_not_imply_hull_witness :
    universalBoolTransport.Related false true ∧
      TransportedRealizable unitBoolCertification false true ∧
      NormalizationWitness trivialBoolNormalization false true ∧
      ¬ HullWitness boolEqContext boolIdentityHull
          (boolMeasurement.measure true) false := by
  constructor
  · trivial
  constructor
  · exact ⟨{ certificate := (), obstructionControlled := trivial }⟩
  constructor
  · trivial
  · intro h
    simp [HullWitness, Witness, boolEqContext, boolIdentityHull, boolMeasurement] at h

end Countermodels
end KTG
