import AVOC.CostCertificateExamples
open Komorebi.AVOC.Synthesis
open Komorebi.AVOC.CostCertificate
open Komorebi.AVOC.CostCertificateExamples
-- A vacuous zero lower table cannot be attained by the claimed one-node witness.
example : Realizes unitAlgebra (fun _ => 0) (fun _ => Program.literal false) := by
  intro s
  constructor
  · cases s; rfl
  · decide
