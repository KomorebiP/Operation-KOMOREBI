import KTG.CertifiedBound

namespace KTG
namespace IUT312

universe u v

/-- The smallest typed vocabulary needed to discuss the Step (xi-e) → (xi-f)
transition without formalizing all of IUT.  The object types are deliberately
separate: an output package is not a q-pilot, and a hull input is not already a
log-volume measurement. -/
structure TypedData where
  MultiradialOutputPackage : Type u
  FixedQPilot : Type u
  HolomorphicHullInput : Type u
  ComparableLineObject : Type u
  PrimeStrip : Type u
  AlgorithmTrace : Type u
  ArithmeticHolomorphicStructure : Type u
  LogVolumeMeasurement : Type v

  domainStructure : ArithmeticHolomorphicStructure
  codomainStructure : ArithmeticHolomorphicStructure

  outputPrimeStrip : MultiradialOutputPackage → PrimeStrip
  qPilotPrimeStrip : FixedQPilot → PrimeStrip
  FullPolyIso : PrimeStrip → PrimeStrip → Type u

  outputHullInput : MultiradialOutputPackage → HolomorphicHullInput
  hullInputMeasurement : HolomorphicHullInput → LogVolumeMeasurement
  qPilotMeasurement : FixedQPilot → LogVolumeMeasurement

  measurementLe : LogVolumeMeasurement → LogVolumeMeasurement → Prop
  measurementLeRefl : ∀ x, measurementLe x x
  measurementLeTrans :
    ∀ {x y z}, measurementLe x y → measurementLe y z → measurementLe x z

  holomorphicHull : LogVolumeMeasurement → LogVolumeMeasurement
  hullExtensive : ∀ x, measurementLe x (holomorphicHull x)
  hullMonotone :
    ∀ {x y}, measurementLe x y →
      measurementLe (holomorphicHull x) (holomorphicHull y)
  hullIdempotent : ∀ x, holomorphicHull (holomorphicHull x) = holomorphicHull x

/-- Context whose objects are multiradial output packages. -/
def sourceContext (D : TypedData.{u, v}) : KContext.{u, v} where
  Obj := D.MultiradialOutputPackage
  MeasureObj := D.LogVolumeMeasurement
  le := D.measurementLe
  le_refl := D.measurementLeRefl
  le_trans := D.measurementLeTrans

/-- Intermediate context of determinant-line / comparable line objects. -/
def comparableContext (D : TypedData.{u, v}) : KContext.{u, v} where
  Obj := D.ComparableLineObject
  MeasureObj := D.LogVolumeMeasurement
  le := D.measurementLe
  le_refl := D.measurementLeRefl
  le_trans := D.measurementLeTrans

/-- Context whose objects are fixed q-pilots. -/
def targetContext (D : TypedData.{u, v}) : KContext.{u, v} where
  Obj := D.FixedQPilot
  MeasureObj := D.LogVolumeMeasurement
  le := D.measurementLe
  le_refl := D.measurementLeRefl
  le_trans := D.measurementLeTrans

/-- The raw output measurement is obtained only after the output package is
converted to a holomorphic-hull input.  It is not itself the hulled result. -/
def rawOutputMeasurement
    (D : TypedData.{u, v})
    (out : D.MultiradialOutputPackage) : D.LogVolumeMeasurement :=
  D.hullInputMeasurement (D.outputHullInput out)

/-- Measurement of the fixed q-pilot in the common log-volume comparison space. -/
def qPilotMeasurementMap
    (D : TypedData.{u, v}) : KMeasurementMap (targetContext D) where
  measure := D.qPilotMeasurement

/-- The source-defined holomorphic hull as a KTG hull operator. -/
def targetHull (D : TypedData.{u, v}) : KHull (targetContext D) where
  hull := D.holomorphicHull
  extensive := D.hullExtensive
  monotone := D.hullMonotone
  idempotent := D.hullIdempotent

/-- The exact source-faithful measurement-level assertion needed at Step (xi-f). -/
def QPilotHullContainment
    (D : TypedData.{u, v})
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) : Prop :=
  D.measurementLe
    (D.qPilotMeasurement q)
    (D.holomorphicHull (rawOutputMeasurement D out))

/-- The source-faithful containment proposition is definitionally the generic
KTG hull witness. -/
theorem qPilotHullContainment_iff_hullWitness
    (D : TypedData.{u, v})
    (out : D.MultiradialOutputPackage)
    (q : D.FixedQPilot) :
    QPilotHullContainment D out q ↔
      HullWitness (targetContext D) (targetHull D)
        ((qPilotMeasurementMap D).measure q)
        (rawOutputMeasurement D out) :=
  Iff.rfl

end IUT312
end KTG
