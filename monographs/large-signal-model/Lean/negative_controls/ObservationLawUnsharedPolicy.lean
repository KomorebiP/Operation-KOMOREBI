import KomorebiLSM.ObservationLawKernels
import KomorebiLSM.SequentialLowerCertificate
/- Negative control: equal observation kernels cannot control joint records
when the two action policies differ. -/
set_option backward.isDefEq.respectTransparency false
open MeasureTheory ProbabilityTheory Komorebi.LSM
open ObservationLawKernels SequentialLowerCertificate
noncomputable def fixedPolicy (b : Bool) : Policy Unit Bool Unit :=
  fun _ => Kernel.const _ (Measure.dirac b)
noncomputable def commonObservation : ObservationKernel Unit Bool Unit :=
  fun _ => Kernel.const _ (Measure.dirac ())
instance (b : Bool) : ∀ n, IsMarkovKernel (fixedPolicy b n) :=
  fun _ => inferInstanceAs (IsMarkovKernel (Kernel.const _ (Measure.dirac b)))
instance : ∀ n, IsMarkovKernel (commonObservation n) :=
  fun _ => inferInstanceAs (IsMarkovKernel (Kernel.const _ (Measure.dirac ())))
instance (b : Bool) : IsProbabilityMeasure (law (fixedPolicy b) commonObservation (Measure.dirac ()) 1) :=
  law_probability_aux _ _ _ 1
theorem one_record (b : Bool) :
    law (fixedPolicy b) commonObservation (Measure.dirac ()) 1 =
      Measure.dirac ((),(PUnit.unit,(b,()))) := by
  change Measure.map (append 0)
    (((Measure.map (initial (A := Bool) (Y := Unit)) (Measure.dirac ())) ⊗ₘ
      Kernel.const _ (Measure.dirac b)) ⊗ₘ Kernel.const _ (Measure.dirac ())) = _
  rw [Measure.map_dirac' (initial_measurable (A := Bool) (Y := Unit)),
    Measure.compProd_const, Measure.compProd_const, Measure.dirac_prod_dirac,
    Measure.dirac_prod_dirac,
    Measure.map_dirac' (append_measurable (I := Unit) (A := Bool) (Y := Unit) 0)]
  rfl
example : lawTV (law (fixedPolicy false) commonObservation (Measure.dirac ()) 1)
    (law (fixedPolicy true) commonObservation (Measure.dirac ()) 1) ≤ 0 := by
  have h : lawTV (law (fixedPolicy false) commonObservation (Measure.dirac ()) 1)
      (law (fixedPolicy true) commonObservation (Measure.dirac ()) 1) = 1 := by
    simpa only [one_record] using lawTV_dirac_eq_one
      (Ω := History Unit Bool Unit 1) ((),(PUnit.unit,(false,())))
      ((),(PUnit.unit,(true,()))) (by intro h; cases h)
  simp only [h]
  norm_num
