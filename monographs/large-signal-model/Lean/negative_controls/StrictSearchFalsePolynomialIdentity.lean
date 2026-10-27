import KomorebiLSM.BernsteinGridSearch

open Komorebi.LSM.TensorBernsteinCertificate Komorebi.LSM.BernsteinGridSearch

-- Nonnegative submitted arrays still fail when their literal polynomial identity is false.
example : leafValid (1 : Polynomial₂) square ⟨0,0,fun _ _ => 0⟩ := by
  norm_num [leafValid, Rectangle.localPolynomial, tensorPolynomial, Fin.sum_univ_one]
