import KomorebiLSM.VilleInequality
open MeasureTheory Komorebi.LSM.VilleInequality

/- The constant process two is a genuine nonnegative supermartingale. Its
crossing probability at two is one, so the initial expectation budget matters. -/
example (F : Filtration ℕ (inferInstance : MeasurableSpace Unit)) :
    (Measure.dirac ()) (crossing (fun (_ : ℕ) (_ : Unit) => (2 : ℝ)) 2)≤ENNReal.ofReal (1/2) := by
  have hM : Supermartingale (fun (_ : ℕ) (_ : Unit) => (2 : ℝ)) F (Measure.dirac ()) :=
    (martingale_const F (Measure.dirac ()) (2 : ℝ)).supermartingale
  norm_num [crossing]
