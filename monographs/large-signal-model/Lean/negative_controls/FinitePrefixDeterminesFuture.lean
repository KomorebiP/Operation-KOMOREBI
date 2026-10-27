import KomorebiLSM.Block9Examples

example : Komorebi.LSM.Delay.output 3 ((Komorebi.LSM.Delay.shift 5 ^ 4) (Komorebi.LSM.Delay.delayedInitial 3)) = 0 := by
  rw [Komorebi.LSM.Delay.delayed_output]
  norm_num
