import AVOC.OperationalExamples

open Komorebi.AVOC.MultiLevel
open Komorebi.AVOC.Affine.MultiLevelRank
open Komorebi.AVOC.Affine.MultiLevelOperational
open Komorebi.AVOC.Affine.CertifiedOperational
open Komorebi.AVOC.Affine.OperationalExamples

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

example : acknowledgeProbe (rankCatalogue catalogue) initial () () .fault =
    some (step (model catalogue) initial (.probe ()) false) := by
  rw [operational_fault_rejected]
