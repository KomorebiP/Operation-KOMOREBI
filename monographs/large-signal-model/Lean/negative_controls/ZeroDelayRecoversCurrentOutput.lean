import KomorebiLSM.Block9Examples

example : Komorebi.LSM.Delay.observation (LinearMap.id : ℚ →ₗ[ℚ] ℚ) LinearMap.id 1 1 ⟨0,by decide⟩ = 0 := by
  norm_num [Komorebi.LSM.Delay.observation]
