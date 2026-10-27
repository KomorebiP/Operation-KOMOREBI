import KomorebiLSM.RotationRank

/- Full prediction for the rational rotation law does not admit two-dimensional
linear realizations. This incorrect smaller-rank claim must be rejected. -/
example : Module.finrank ℝ (Komorebi.LSM.Behavior.space
    Komorebi.LSM.RotationModel.process) ≤ 2 := by
  rw [Komorebi.LSM.RotationModel.behavior_dimension_three]
  norm_num
