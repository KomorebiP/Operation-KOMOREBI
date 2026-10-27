import KomorebiLSM.Block10Examples
open Komorebi.LSM.RationalSearch Komorebi.LSM.Block10Examples
example : 0 < lifts zeroBranchCertificate 1 0 0 := by
  unfold lifts zeroBranchCertificate
  norm_num
