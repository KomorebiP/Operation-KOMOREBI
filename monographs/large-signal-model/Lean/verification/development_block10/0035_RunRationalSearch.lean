import KomorebiLSM.Block10Examples
open Komorebi.LSM.RationalSearch Komorebi.LSM.Block10Examples
#eval decide (Valid (fun _ => 1) (fun _ => 1) (fun _ => 1) oneCertificate)
#eval decide (Valid (fun _ => 1) (fun _ => 1) (fun t => if t = 0 then 1 else 0) zeroBranchCertificate)
#eval decide (Valid (fun _ => 1) (fun _ => 1) (fun _ => -1) signedCertificate)
#eval (checkCode (fun _ => 1) (fun _ => 1) (fun _ => 1) (Encodable.encode oneCertificate)).isSome
#eval (search (fun _ => 1) (fun _ => 1) (fun _ => 1) 64 : Option (Candidate 1 1)).isSome
