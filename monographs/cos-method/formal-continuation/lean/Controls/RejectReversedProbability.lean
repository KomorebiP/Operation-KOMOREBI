import KomorebiQCOS.TailProbability
open KomorebiQCOS MeasureTheory
example : tailProbability (Measure.dirac ()) (fun _ => (1 : ℝ)) 1 ≤
    tailProbability (Measure.dirac ()) (fun _ => (0 : ℝ)) 1 := by
  norm_num [tailProbability, tailEvent]
