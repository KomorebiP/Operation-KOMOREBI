import KomorebiLSM.RegressionExponential
/- Negative control: a mixing measure of mass two cannot give M0=1. -/
open scoped ENNReal
open MeasureTheory Komorebi.LSM.RegressionConfidence
noncomputable def doublePrior : Measure (Unit → ℝ) :=
  (2:ℝ≥0∞) • Measure.dirac (fun _ => 0)
example : exponentialMixture (Ω := Unit) (I := Unit) 1 (fun _ _ _ => 0)
    (fun _ _ => 0) doublePrior 0 ()=1 := by
  simp only [exponentialMixture,probabilityMixture,exponentialProcess_zero]
  rw [integral_const]
  norm_num [doublePrior,measureReal_def,Measure.smul_apply]
