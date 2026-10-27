import KomorebiLSM.ContinuousReferenceChange

open Komorebi.LSM.ContinuousInstrument
variable {E A Y : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace Y]

/- A changed reference requires reciprocal rescaling of the operator density;
the numerical density itself is not invariant under that change. -/
example {C : Komorebi.LSM.BaseNorm.ProbabilityCone E} {μ : MeasureTheory.Measure Y}
    (D : DensityInstrument (A := A) C μ) (R : ReferenceDensity μ)
    (a : A) (y : Y) (z : DensityInstrument.State C) (hr : R.weight y=2) (hd : D.density a y z.1=1) :
    (D.reweighted R).density a y z.1=D.density a y z.1 := by
  rw [D.reweighted_density R a y z.1,hr,hd]
  norm_num
