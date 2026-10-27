import KomorebiLSM.ContinuousInstrument

open Komorebi.LSM.ContinuousInstrument
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace Y]

/- An observation density can exceed one. The kernel construction integrates
it and does not impose the branch-probability upper bound on its point values. -/
example {C : Komorebi.LSM.BaseNorm.ProbabilityCone E} {μ : MeasureTheory.Measure Y}
    (D : DensityInstrument (A := A) C μ) (a : A) (y : Y) (z : DensityInstrument.State C)
    (hd : D.density a y z.1=2) : D.density a y z.1≤1 := by
  rw [hd]
  norm_num
