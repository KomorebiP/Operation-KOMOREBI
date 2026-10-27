import KomorebiLSM.ContinuousRecords

/-! Rejected extension: cone membership alone does not normalize a record law.
The actual zero input has zero empty-record mass, rather than probability one. -/
set_option autoImplicit false
open MeasureTheory
open Komorebi.LSM
open Komorebi.LSM.ContinuousRecords
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y}
example (D : ContinuousInstrument.DensityInstrument (A := A) C μ)
    (π : Policy (A := A) (Y := Y)) : recordLaw D π (0 : E) 0 Set.univ=1 := by
  simp [recordLaw,reference,recordDensity,Policy.weight,run]
