import PaperICompletion
open Komorebi.PaperICompletion.SpectralCertificates
-- EXPECTED REJECTION: ordinary complex symmetry is not Hermitian symmetry.
example (A : Matrix (Fin 2) (Fin 2) ℂ) (hA : A.IsSymm) :=
  hermitian_matrix_seedNumber_isLeast A hA
