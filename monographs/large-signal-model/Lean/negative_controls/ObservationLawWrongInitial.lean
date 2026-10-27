import KomorebiLSM.ObservationLawKernels
import KomorebiLSM.SequentialLowerCertificate
/- Negative control: the zero-horizon law retains the initial-history TV. -/
set_option backward.isDefEq.respectTransparency false
open MeasureTheory ProbabilityTheory Komorebi.LSM
open ObservationLawKernels SequentialLowerCertificate
noncomputable def unitPolicy : Policy Bool Unit Unit := fun _ => Kernel.const _ (Measure.dirac ())
noncomputable def unitObservation : ObservationKernel Bool Unit Unit := fun _ => Kernel.const _ (Measure.dirac ())
instance : ∀ n, IsMarkovKernel (unitPolicy n) := fun _ => inferInstanceAs (IsMarkovKernel (Kernel.const _ (Measure.dirac ())))
instance : ∀ n, IsMarkovKernel (unitObservation n) := fun _ => inferInstanceAs (IsMarkovKernel (Kernel.const _ (Measure.dirac ())))
instance (b : Bool) : IsProbabilityMeasure (law unitPolicy unitObservation (Measure.dirac b) 0) :=
  law_probability_aux _ _ _ 0
theorem initial_record (b : Bool) : law unitPolicy unitObservation (Measure.dirac b) 0 =
    Measure.dirac ((b,PUnit.unit) : History Bool Unit Unit 0) := by
  change Measure.map (initial (A := Unit) (Y := Unit)) (Measure.dirac b) = _
  rw [Measure.map_dirac' (initial_measurable (A := Unit) (Y := Unit))]
  rfl
example : lawTV (law unitPolicy unitObservation (Measure.dirac false) 0)
    (law unitPolicy unitObservation (Measure.dirac true) 0) ≤ 0 := by
  have h : lawTV (law unitPolicy unitObservation (Measure.dirac false) 0)
      (law unitPolicy unitObservation (Measure.dirac true) 0) = 1 := by
    simpa only [initial_record] using lawTV_dirac_eq_one (Ω := History Bool Unit Unit 0)
      (false,PUnit.unit) (true,PUnit.unit) (by intro h; cases h)
  simp only [h]
  norm_num
