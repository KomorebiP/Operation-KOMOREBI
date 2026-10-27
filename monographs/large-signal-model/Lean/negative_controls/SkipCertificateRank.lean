import KomorebiLSM.Block10Examples
open Komorebi.LSM.RationalSearch Komorebi.LSM.Block10Examples
example : Valid (fun i => if i = 0 then 1 else 0) (fun _ => 1)
    (fun _ => 1) singularCertificate := by
  simpa only [singular_generators_rejected, not_true_eq_false]
