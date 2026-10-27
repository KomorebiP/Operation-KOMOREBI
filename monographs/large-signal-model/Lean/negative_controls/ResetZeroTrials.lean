import KomorebiLSM.ResetCertificate
/- Zero trials do not produce a probability estimate equal to the target. -/
example : Komorebi.LSM.ResetCertificate.sampleMean
    (N:=0) (fun i : Fin 0 => Fin.elim0 i : Fin 0 → Unit → ℝ) () = 1 := by
  norm_num [Komorebi.LSM.ResetCertificate.sampleMean]
