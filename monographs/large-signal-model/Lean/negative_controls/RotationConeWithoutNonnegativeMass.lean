import KomorebiLSM.RotationConeGeometry

/- Without nonnegative mass, the universal cone would satisfy the other
invariance contracts. This negative-mass state prevents that weakening. -/
example : (Komorebi.LSM.LorentzBaseNorm.point (-1) 0) ∈ Komorebi.LSM.RotationModel.cone := by
  change Real.sqrt ((0 : ℝ)^2 + 0^2) ≤ (-1 : ℝ)
  norm_num
