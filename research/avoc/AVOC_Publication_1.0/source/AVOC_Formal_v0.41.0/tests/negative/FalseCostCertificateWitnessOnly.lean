import AVOC.CostCertificateExamples
open Komorebi.AVOC.CostCertificate
open Komorebi.AVOC.CostCertificateExamples
-- Sound witnesses alone do not establish a constructor lower bound.
example : LowerValid unitAlgebra (fun _ => 2) := by
  constructor <;> intros <;> decide
