import KTG.IUT312Types

namespace KTG
namespace IUT312

universe u v

/-- Types and control predicates for the three named indeterminacies of Theorem
3.11 together with the live comparison indeterminacies used in Remark 3.9.5 and
Step (xi).  The predicates are interfaces for source theorems; naming a channel
does not prove it controlled. -/
structure ObstructionSemantics where
  Ind1State : Type u
  Ind2State : Type u
  Ind3State : Type u
  UnitMultipleState : Type u
  TensorPowerTwistState : Type u
  VerticalShiftState : Type u
  LogLinkIterateState : Type u
  LogarithmicConjugateState : Type u
  ApproximationState : Type u

  ind1Controlled : Ind1State → Prop
  ind2Controlled : Ind2State → Prop
  ind3Controlled : Ind3State → Prop
  unitMultipleControlled : UnitMultipleState → Prop
  tensorPowerTwistControlled : TensorPowerTwistState → Prop
  verticalShiftControlled : VerticalShiftState → Prop
  logLinkIterateControlled : LogLinkIterateState → Prop
  logarithmicConjugateControlled : LogarithmicConjugateState → Prop
  approximationControlled : ApproximationState → Prop

/-- One explicit value for every obstruction channel. -/
structure ObstructionBundle (O : ObstructionSemantics.{u}) where
  ind1 : O.Ind1State
  ind2 : O.Ind2State
  ind3 : O.Ind3State
  unitMultiple : O.UnitMultipleState
  tensorPowerTwist : O.TensorPowerTwistState
  verticalShift : O.VerticalShiftState
  logLinkIterate : O.LogLinkIterateState
  logarithmicConjugate : O.LogarithmicConjugateState
  approximation : O.ApproximationState

/-- A channel-by-channel control certificate.  The field names record the
source-level mechanism expected to discharge each obligation. -/
structure ObstructionControl
    (O : ObstructionSemantics.{u})
    (b : ObstructionBundle O) : Prop where
  ind1_procession_automorphism_controlled : O.ind1Controlled b.ind1
  ind2_tensor_factor_automorphism_controlled : O.ind2Controlled b.ind2
  ind3_upper_semi_compatibility_controlled : O.ind3Controlled b.ind3
  unit_multiples_absorbed_by_hull : O.unitMultipleControlled b.unitMultiple
  tensor_power_twist_tracked_by_grade :
    O.tensorPowerTwistControlled b.tensorPowerTwist
  vertical_shift_rectified_by_logKummer :
    O.verticalShiftControlled b.verticalShift
  log_link_iterates_measurement_invariant :
    O.logLinkIterateControlled b.logLinkIterate
  logarithmic_conjugates_measurement_invariant :
    O.logarithmicConjugateControlled b.logarithmicConjugate
  approximation_is_one_sided : O.approximationControlled b.approximation

/-- Semantic predicates used by the source-faithful IPL/SHE/APT certificate.
They describe an algorithm trace; none mentions hull containment or the desired
scalar inequality. -/
structure CertificateSemantics (D : TypedData.{u, v}) where
  ProducesOutput : D.AlgorithmTrace → D.MultiradialOutputPackage → Prop
  UsesInput : D.AlgorithmTrace → D.FixedQPilot → Prop
  ExecutableIn :
    D.AlgorithmTrace → D.ArithmeticHolomorphicStructure → Prop
  InputHeldFixed : D.AlgorithmTrace → D.FixedQPilot → Prop
  obstructions : ObstructionSemantics.{u}

/-- IPL: a full poly-isomorphism between the output prime-strip and the fixed
input q-pilot prime-strip.  This is structural linkage, not measurement-level
membership. -/
structure InputPrimeStripLink
    (D : TypedData.{u, v})
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) where
  fullPolyIso : D.FullPolyIso (D.outputPrimeStrip out) (D.qPilotPrimeStrip q)

/-- SHE for a single algorithm trace: the same trace is executable in both
arithmetic-holomorphic structures while the q-pilot input remains fixed. -/
structure SimultaneousHolomorphicExpressibility
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (trace : D.AlgorithmTrace)
    (q : D.FixedQPilot) : Prop where
  executable_in_domain : S.ExecutableIn trace D.domainStructure
  executable_in_codomain : S.ExecutableIn trace D.codomainStructure
  input_qPilot_held_fixed : S.InputHeldFixed trace q

/-- APT: an algorithm trace produces the output from the fixed input and has
SHE.  It is deliberately not represented as a set-theoretic function carrying a
region into another region. -/
structure AlgorithmicParallelTransport
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) where
  trace : D.AlgorithmTrace
  produces_output : S.ProducesOutput trace out
  uses_input : S.UsesInput trace q
  she : SimultaneousHolomorphicExpressibility D S trace q

/-- Exact Block 03 realization certificate: IPL plus an APT trace carrying SHE,
and an explicit obstruction bundle.  No hull witness is a field. -/
structure SourceRealizationCertificate
    (D : TypedData.{u, v})
    (S : CertificateSemantics D)
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) where
  ipl : InputPrimeStripLink D out q
  apt : AlgorithmicParallelTransport D S out q
  obstruction : ObstructionBundle S.obstructions

/-- Structural transport induced by prime-strip linkage. -/
def transport
    (D : TypedData.{u, v})
    (S : CertificateSemantics D) :
    KTransport (sourceContext D) (targetContext D) where
  Carrier := D.PrimeStrip
  leftRep := D.outputPrimeStrip
  rightRep := D.qPilotPrimeStrip
  related := fun left right => Nonempty (D.FullPolyIso left right)
  Obstruction := ObstructionBundle S.obstructions

/-- KTG certification interface induced by the source-level IPL/SHE/APT
certificate and channel-by-channel obstruction control. -/
def certification
    (D : TypedData.{u, v})
    (S : CertificateSemantics D) :
    KTransportCertification (transport D S) where
  Certificate := SourceRealizationCertificate D S
  obstruction := fun certificate => certificate.obstruction
  controlled := ObstructionControl S.obstructions
  related_of_controlled := by
    intro out q certificate _
    exact ⟨certificate.ipl.fullPolyIso⟩

/-- The typed source certificate exposes IPL. -/
theorem SourceRealizationCertificate.has_IPL
    {D : TypedData.{u, v}}
    {S : CertificateSemantics D}
    {out : D.MultiradialOutputPackage}
    {q : D.FixedQPilot}
    (certificate : SourceRealizationCertificate D S out q) :
    Nonempty
      (D.FullPolyIso (D.outputPrimeStrip out) (D.qPilotPrimeStrip q)) :=
  ⟨certificate.ipl.fullPolyIso⟩

/-- The typed source certificate exposes SHE through its APT trace. -/
theorem SourceRealizationCertificate.has_SHE
    {D : TypedData.{u, v}}
    {S : CertificateSemantics D}
    {out : D.MultiradialOutputPackage}
    {q : D.FixedQPilot}
    (certificate : SourceRealizationCertificate D S out q) :
    SimultaneousHolomorphicExpressibility D S certificate.apt.trace q :=
  certificate.apt.she

end IUT312
end KTG
