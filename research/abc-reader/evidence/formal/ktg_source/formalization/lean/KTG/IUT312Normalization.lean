import KTG.IUT312Certificates

namespace KTG
namespace IUT312

universe u v

/-- A positive natural number used for tensor powers, multiplicities, and
procession-normalization scales. -/
structure PositiveNat where
  value : Nat
  positive : 0 < value
  deriving DecidableEq

/-- Grade carried by the rank > 1 localized arithmetic-vector-bundle output
before determinant formation. -/
structure OutputGrade where
  vectorRank : PositiveNat
  weightedDeterminantPower : PositiveNat
  directSummandMultiplicity : PositiveNat
  structureSheafCorrection : Nat
  processionAveragingScale : PositiveNat
  deriving DecidableEq

/-- Grade after forming the suitably weighted positive tensor power of the
determinant. -/
structure DeterminantGrade where
  lineTensorPower : PositiveNat
  directSummandMultiplicity : PositiveNat
  structureSheafCorrection : Nat
  processionAveragingScale : PositiveNat
  deriving DecidableEq

/-- A definitionally distinct grade space for the input side of procession
normalization.  Its separation prevents a silent identification of conventions. -/
structure ProcessionInputGrade where
  lineTensorPower : PositiveNat
  directSummandMultiplicity : PositiveNat
  structureSheafCorrection : Nat
  processionAveragingScale : PositiveNat
  deriving DecidableEq

/-- Grade of the fixed q-pilot line object after the determinant/tensor-power and
procession-normalization stages. -/
structure QPilotGrade where
  qPilotTensorPower : PositiveNat
  directSummandMultiplicity : PositiveNat
  structureSheafCorrection : Nat
  processionAveragingScale : PositiveNat
  deriving DecidableEq

/-- Ob3: determinant formation removes the vector rank while retaining every
load-bearing normalization factor. -/
def determinantSigma (g : OutputGrade) : DeterminantGrade where
  lineTensorPower := g.weightedDeterminantPower
  directSummandMultiplicity := g.directSummandMultiplicity
  structureSheafCorrection := g.structureSheafCorrection
  processionAveragingScale := g.processionAveragingScale

/-- Explicit grade-space bridge between determinant conventions and procession
input conventions. -/
def determinantToProcessionGrade (g : DeterminantGrade) : ProcessionInputGrade where
  lineTensorPower := g.lineTensorPower
  directSummandMultiplicity := g.directSummandMultiplicity
  structureSheafCorrection := g.structureSheafCorrection
  processionAveragingScale := g.processionAveragingScale

/-- Procession normalization transfers all tracked factors to the q-pilot grade. -/
def processionSigma (g : ProcessionInputGrade) : QPilotGrade where
  qPilotTensorPower := g.lineTensorPower
  directSummandMultiplicity := g.directSummandMultiplicity
  structureSheafCorrection := g.structureSheafCorrection
  processionAveragingScale := g.processionAveragingScale

/-- Source-specific grade assignments and compatibility predicates.  Existence
of compatible determinant-line objects is not built in. -/
structure NormalizationData (D : TypedData.{u, v}) where
  outputGrade : D.MultiradialOutputPackage → OutputGrade
  determinantLineGrade : D.ComparableLineObject → DeterminantGrade
  processionInputGrade : D.ComparableLineObject → ProcessionInputGrade
  qPilotGrade : D.FixedQPilot → QPilotGrade

  determinantCompatible :
    D.MultiradialOutputPackage → D.ComparableLineObject → Prop
  processionCompatible : D.ComparableLineObject → D.FixedQPilot → Prop

  determinantPreserves :
    ∀ {out line}, determinantCompatible out line →
      determinantLineGrade line = determinantSigma (outputGrade out)
  gradeBridgeCompatible :
    ∀ line,
      processionInputGrade line =
        determinantToProcessionGrade (determinantLineGrade line)
  processionPreserves :
    ∀ {line q}, processionCompatible line q →
      qPilotGrade q = processionSigma (processionInputGrade line)

/-- First normalization stage: output package to determinant-line object. -/
def determinantNormalization
    (D : TypedData.{u, v})
    (N : NormalizationData D) :
    KNormalization (sourceContext D) (comparableContext D) where
  GradeA := OutputGrade
  GradeB := DeterminantGrade
  gradeA := N.outputGrade
  gradeB := N.determinantLineGrade
  sigma := determinantSigma
  compatible := N.determinantCompatible
  preserves := N.determinantPreserves

/-- Second normalization stage: determinant-line object to fixed q-pilot. -/
def processionNormalization
    (D : TypedData.{u, v})
    (N : NormalizationData D) :
    KNormalization (comparableContext D) (targetContext D) where
  GradeA := ProcessionInputGrade
  GradeB := QPilotGrade
  gradeA := N.processionInputGrade
  gradeB := N.qPilotGrade
  sigma := processionSigma
  compatible := N.processionCompatible
  preserves := N.processionPreserves

/-- The explicit KTG grade bridge demanded by the mismatch between determinant
and procession grade spaces. -/
def normalizationGradeBridge
    (D : TypedData.{u, v})
    (N : NormalizationData D) :
    KGradeBridge (determinantNormalization D N) (processionNormalization D N) where
  bridge := determinantToProcessionGrade
  grade_compatible := N.gradeBridgeCompatible

/-- Direct output-to-q-pilot normalization.  A witness contains an actual
intermediate determinant-line object and certificates for both normalization
stages. -/
def directNormalization
    (D : TypedData.{u, v})
    (N : NormalizationData D) :
    KNormalization (sourceContext D) (targetContext D) where
  GradeA := OutputGrade
  GradeB := QPilotGrade
  gradeA := N.outputGrade
  gradeB := N.qPilotGrade
  sigma := fun grade =>
    processionSigma (determinantToProcessionGrade (determinantSigma grade))
  compatible := fun out q =>
    ∃ line : D.ComparableLineObject,
      N.determinantCompatible out line ∧ N.processionCompatible line q
  preserves := by
    intro out q witness
    rcases witness with ⟨line, hDet, hProc⟩
    exact normalization_composes_through_bridge
      (determinantNormalization D N)
      (processionNormalization D N)
      (normalizationGradeBridge D N)
      hDet hProc

/-- The direct normalization witness transparently records its intermediate
comparable line object. -/
theorem directNormalizationWitness_iff
    (D : TypedData.{u, v})
    (N : NormalizationData D)
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) :
    NormalizationWitness (directNormalization D N) out q ↔
      ∃ line : D.ComparableLineObject,
        N.determinantCompatible out line ∧ N.processionCompatible line q :=
  Iff.rfl

/-- Full tracked grade equation for the source-faithful normalization chain. -/
theorem directNormalization_grade_eq
    (D : TypedData.{u, v})
    (N : NormalizationData D)
    {out : D.MultiradialOutputPackage}
    {q : D.FixedQPilot}
    (h : NormalizationWitness (directNormalization D N) out q) :
    N.qPilotGrade q =
      processionSigma
        (determinantToProcessionGrade
          (determinantSigma (N.outputGrade out))) :=
  normalization_grade_eq (directNormalization D N) h

/-- Downstream IUT IV grade that attaches the explicit j² exponent used in the
weighted log-volume estimate.  This is deliberately not a field of the IUT III
Step (xi) normalization. -/
structure IUTIVSquareWeightedGrade where
  base : QPilotGrade
  indexJ : Nat
  qExponent : Nat
  qExponent_is_square : qExponent = indexJ * indexJ
  deriving DecidableEq

/-- Attach the later IUT IV square weight to an already normalized q-pilot grade. -/
def attachIUTIVSquareWeight
    (grade : QPilotGrade) (j : Nat) : IUTIVSquareWeightedGrade where
  base := grade
  indexJ := j
  qExponent := j * j
  qExponent_is_square := rfl

/-- Machine-checked location of the later j² factor. -/
theorem attachIUTIVSquareWeight_exponent
    (grade : QPilotGrade) (j : Nat) :
    (attachIUTIVSquareWeight grade j).qExponent = j * j :=
  rfl

end IUT312
end KTG
