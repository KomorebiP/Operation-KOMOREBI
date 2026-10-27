import KomorebiLSM.MarkovWindows
/- Negative control: rho=1 erases the initial-law error, not the discrepancy
between the two actual transition kernels. -/
open MeasureTheory ProbabilityTheory Komorebi.LSM.MarkovStability
open Komorebi.LSM.SequentialLowerCertificate
open scoped ENNReal
noncomputable def refresh (b : Bool) : Kernel Bool Bool := Kernel.const _ (Measure.dirac b)
instance (b : Bool) : IsMarkovKernel (refresh b) := by unfold refresh; infer_instance
theorem actual_minorization : Minorized (refresh false) 1 (Measure.dirac false) := by
  intro x
  simp only [ENNReal.ofReal_one,one_smul,refresh,Kernel.const_apply]
  exact le_rfl
theorem actual_discrepancy (x : Bool) : lawTV (refresh false x) (refresh true x)=1 :=
  lawTV_dirac_eq_one false true (by decide)
theorem refreshed (b : Bool) : marginal (refresh b) (Measure.dirac false) 1=Measure.dirac b := by
  change (Kernel.const _ (Measure.dirac b)) ∘ₘ Measure.dirac false=Measure.dirac b
  rw [Measure.const_comp,measure_univ,one_smul]
example : lawTV (marginal (refresh false) (Measure.dirac false) 1)
    (marginal (refresh true) (Measure.dirac false) 1)≤0 := by
  have ht : lawTV (marginal (refresh false) (Measure.dirac false) 1)
      (marginal (refresh true) (Measure.dirac false) 1)=1 := by
    simpa only [refreshed] using lawTV_dirac_eq_one false true (by decide)
  rw [ht]
  norm_num
