import KomorebiLSM.MarkovWindows
/- Negative control: complete refresh contracts the output marginal to zero
but a joint record still retains its distinct entry state. -/
set_option backward.isDefEq.respectTransparency false
open MeasureTheory ProbabilityTheory Komorebi.LSM.MarkovStability
open Komorebi.LSM.SequentialLowerCertificate
open scoped ENNReal
noncomputable def reset : Kernel Bool Bool := Kernel.const _ (Measure.dirac false)
instance : IsMarkovKernel reset := by unfold reset; infer_instance
theorem actual_minorization : Minorized reset 1 (Measure.dirac false) := by
  intro x
  simp only [ENNReal.ofReal_one,one_smul,reset,Kernel.const_apply]
  exact le_rfl
theorem retained_record (b : Bool) : recordLaw reset (Measure.dirac b) 1=
    Measure.dirac ((b,false) : Record Bool 1) := by
  change Measure.dirac b ⊗ₘ reset.comap (recordLast 0) (recordLast_measurable 0)=_
  have hk : reset.comap (recordLast 0) (recordLast_measurable 0)=
      Kernel.const (Record Bool 0) (Measure.dirac false) := rfl
  rw [hk,Measure.compProd_const,Measure.dirac_prod_dirac]
instance (b : Bool) : IsProbabilityMeasure (recordLaw reset (Measure.dirac b) 1) :=
  recordLaw_probability_aux reset (Measure.dirac b) 1
example : lawTV (recordLaw reset (Measure.dirac false) 1)
    (recordLaw reset (Measure.dirac true) 1)≤0 := by
  have ht : lawTV (recordLaw reset (Measure.dirac false) 1)
      (recordLaw reset (Measure.dirac true) 1)=1 := by
    simpa only [retained_record] using lawTV_dirac_eq_one (Ω := Record Bool 1)
      (false,false) (true,false) (by intro h; cases h)
  rw [ht]
  norm_num
