import KomorebiLSM.CellDistance

open MeasureTheory Komorebi.LSM
/- Two actual independent interval-uniform points have mean separation 1/3;
a smaller guessed constant cannot replace the integrated calculation. -/
example : (∫ y,∫ v,dist y v∂AveragedCongruence.uniformInterval 0 1
    ∂AveragedCongruence.uniformInterval 0 1)≤(1/4:ℝ) := by
  rw [CellDistance.uniform_double_distance 0 1 (by norm_num)]
  norm_num
