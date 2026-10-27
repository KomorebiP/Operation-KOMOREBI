import KTG.IUT312WitnessObligation

namespace KTG
namespace IUT312
namespace SourceCountermodel

/-- Equality-ordered Boolean measurement model. -/
def data : TypedData where
  MultiradialOutputPackage := Bool
  FixedQPilot := Bool
  HolomorphicHullInput := Bool
  ComparableLineObject := Unit
  PrimeStrip := Unit
  AlgorithmTrace := Unit
  ArithmeticHolomorphicStructure := Bool
  LogVolumeMeasurement := Bool

  domainStructure := false
  codomainStructure := true

  outputPrimeStrip := fun _ => ()
  qPilotPrimeStrip := fun _ => ()
  FullPolyIso := fun _ _ => Unit

  outputHullInput := fun out => out
  hullInputMeasurement := fun input => input
  qPilotMeasurement := fun q => q

  measurementLe := Eq
  measurementLeRefl := fun _ => rfl
  measurementLeTrans := fun h₁ h₂ => Eq.trans h₁ h₂

  holomorphicHull := fun value => value
  hullExtensive := fun _ => rfl
  hullMonotone := fun h => h
  hullIdempotent := fun _ => rfl

/-- Every obstruction state is present but trivially controlled in the finite
logical model. -/
def obstructionSemantics : ObstructionSemantics where
  Ind1State := Unit
  Ind2State := Unit
  Ind3State := Unit
  UnitMultipleState := Unit
  TensorPowerTwistState := Unit
  VerticalShiftState := Unit
  LogLinkIterateState := Unit
  LogarithmicConjugateState := Unit
  ApproximationState := Unit

  ind1Controlled := fun _ => True
  ind2Controlled := fun _ => True
  ind3Controlled := fun _ => True
  unitMultipleControlled := fun _ => True
  tensorPowerTwistControlled := fun _ => True
  verticalShiftControlled := fun _ => True
  logLinkIterateControlled := fun _ => True
  logarithmicConjugateControlled := fun _ => True
  approximationControlled := fun _ => True

/-- All algorithm-trace predicates hold.  This realizes the complete typed
IPL/SHE/APT interface without encoding containment. -/
def semantics : CertificateSemantics data where
  ProducesOutput := fun _ _ => True
  UsesInput := fun _ _ => True
  ExecutableIn := fun _ _ => True
  InputHeldFixed := fun _ _ => True
  obstructions := obstructionSemantics

/-- Uniform obstruction bundle. -/
def obstruction : ObstructionBundle obstructionSemantics where
  ind1 := ()
  ind2 := ()
  ind3 := ()
  unitMultiple := ()
  tensorPowerTwist := ()
  verticalShift := ()
  logLinkIterate := ()
  logarithmicConjugate := ()
  approximation := ()

/-- Source realization certificate for output `false` and q-pilot `true`. -/
def sourceCertificate : SourceRealizationCertificate data semantics false true where
  ipl := { fullPolyIso := () }
  apt :=
    { trace := ()
      produces_output := trivial
      uses_input := trivial
      she :=
        { executable_in_domain := trivial
          executable_in_codomain := trivial
          input_qPilot_held_fixed := trivial } }
  obstruction := obstruction

/-- Every named obstruction-control field is discharged in the finite model. -/
theorem obstructionControl : ObstructionControl obstructionSemantics obstruction where
  ind1_procession_automorphism_controlled := trivial
  ind2_tensor_factor_automorphism_controlled := trivial
  ind3_upper_semi_compatibility_controlled := trivial
  unit_multiples_absorbed_by_hull := trivial
  tensor_power_twist_tracked_by_grade := trivial
  vertical_shift_rectified_by_logKummer := trivial
  log_link_iterates_measurement_invariant := trivial
  logarithmic_conjugates_measurement_invariant := trivial
  approximation_is_one_sided := trivial

/-- Complete source-level certified realization. -/
def realization : CertifiedRealization (certification data semantics) false true where
  certificate := sourceCertificate
  obstructionControlled := obstructionControl

/-- Positive unit used in all grade components of the finite model. -/
def one : PositiveNat where
  value := 1
  positive := Nat.zero_lt_succ 0

/-- Constant output grade. -/
def outputGrade : OutputGrade where
  vectorRank := one
  weightedDeterminantPower := one
  directSummandMultiplicity := one
  structureSheafCorrection := 0
  processionAveragingScale := one

/-- Constant determinant grade. -/
def determinantGrade : DeterminantGrade := determinantSigma outputGrade

/-- Constant procession-input grade. -/
def processionGrade : ProcessionInputGrade :=
  determinantToProcessionGrade determinantGrade

/-- Constant q-pilot grade. -/
def qPilotGrade : QPilotGrade := processionSigma processionGrade

/-- Two-stage normalization data with an explicit intermediate line object. -/
def normalizationData : NormalizationData data where
  outputGrade := fun _ => outputGrade
  determinantLineGrade := fun _ => determinantGrade
  processionInputGrade := fun _ => processionGrade
  qPilotGrade := fun _ => qPilotGrade

  determinantCompatible := fun _ _ => True
  processionCompatible := fun _ _ => True

  determinantPreserves := fun _ => rfl
  gradeBridgeCompatible := fun _ => rfl
  processionPreserves := fun _ => rfl

/-- Direct normalization witness for the finite source/target pair. -/
theorem normalizationWitness :
    NormalizationWitness (directNormalization data normalizationData) false true :=
  ⟨(), trivial, trivial⟩

/-- The q-pilot measurement `true` is not contained in the identity hull of the
raw output measurement `false`. -/
theorem not_qPilotHullContainment :
    ¬ QPilotHullContainment data false true := by
  change ¬ (true = false)
  intro h
  cases h

/-- Even the complete typed IPL/SHE/APT realization, all named obstruction
controls, and the full two-stage normalization witness do not imply the Step
(xi-f) containment. -/
theorem all_source_prewitness_fields_do_not_imply_containment :
    TransportedRealizable (certification data semantics) false true ∧
      NormalizationWitness (directNormalization data normalizationData) false true ∧
      ¬ QPilotHullContainment data false true :=
  ⟨⟨realization⟩, normalizationWitness, not_qPilotHullContainment⟩

/-- Consequently there is no global source witness theorem for this finite model.
This is a logical independence result, not a counterexample to IUT. -/
theorem no_sourceWitnessTheorem :
    ¬ SourceWitnessTheorem data semantics normalizationData := by
  intro witnessTheorem
  exact not_qPilotHullContainment
    (witnessTheorem.witness_preserved realization normalizationWitness)

end SourceCountermodel
end IUT312
end KTG
