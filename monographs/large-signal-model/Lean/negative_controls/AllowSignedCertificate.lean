import KomorebiLSM.Block10Examples
open Komorebi.LSM.RationalSearch Komorebi.LSM.Block10Examples
example : Valid (fun _ => 1) (fun _ => 1) (fun _ => -1) signedCertificate := by
  simpa only [signed_lift_rejected, not_true_eq_false]
