import KomorebiLSM.Block10Examples
open Komorebi.LSM.RationalSearch Komorebi.LSM.Block10Examples
example : 0 < lifts zeroBranchCertificate 1 ⟨0, by decide⟩ ⟨0, by decide⟩ := by
  unfold lifts zeroBranchCertificate
  norm_num
