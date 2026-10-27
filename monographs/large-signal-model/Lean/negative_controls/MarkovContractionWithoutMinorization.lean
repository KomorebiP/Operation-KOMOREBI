import KomorebiLSM.MarkovWindows
/- Negative control: a common Markov kernel is contractive but has no strict
universal coefficient without the asserted minorization. -/
open MeasureTheory ProbabilityTheory Komorebi.LSM.MarkovStability
open Komorebi.LSM.SequentialLowerCertificate
example : lawTV (marginal Kernel.id (Measure.dirac false) 1)
    (marginal Kernel.id (Measure.dirac true) 1)≤(1/2:ℝ) := by
  have he (b : Bool) : marginal Kernel.id (Measure.dirac b) 1=Measure.dirac b := by
    change Kernel.id ∘ₘ Measure.dirac b=Measure.dirac b
    exact Measure.id_comp
  have ht : lawTV (marginal Kernel.id (Measure.dirac false) 1)
      (marginal Kernel.id (Measure.dirac true) 1)=1 := by
    simpa only [he] using lawTV_dirac_eq_one false true (by decide)
  rw [ht]
  norm_num
