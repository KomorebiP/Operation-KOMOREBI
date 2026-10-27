import KomorebiLSM.LorentzBaseNorm

open Komorebi.LSM.LorentzBaseNorm

/- Purely spatial signed vectors have zero mass and strictly positive base
norm. Ignoring the spatial part must not be accepted. -/
example : coneInstance.value (point 0 (1:ℂ)) ≤ |mass (point 0 (1:ℂ))| := by
  rw [value_zero_mass _ (by simp), spatial_point]
  norm_num
