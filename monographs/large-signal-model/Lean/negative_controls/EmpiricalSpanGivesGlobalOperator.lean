import KomorebiLSM.Block9Examples

example : Komorebi.LSM.Block9Examples.firstFit (0,1) = Komorebi.LSM.Block9Examples.secondFit (0,1) := by
  norm_num [Komorebi.LSM.Block9Examples.firstFit, Komorebi.LSM.Block9Examples.secondFit]
