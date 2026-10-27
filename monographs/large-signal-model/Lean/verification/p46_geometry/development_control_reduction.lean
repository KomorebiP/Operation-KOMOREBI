import KomorebiLSM.RotationConeGeometry

/- Dropping the nonnegative-mass contract would admit the universal invariant
cone. The concrete state below shows why it cannot be the probability cone. -/
example : (Komorebi.LSM.LorentzBaseNorm.point (-1) 0) ∈ Komorebi.LSM.RotationModel.cone := by
  norm_num [Komorebi.LSM.RotationModel.cone, Komorebi.LSM.LorentzBaseNorm.point]
