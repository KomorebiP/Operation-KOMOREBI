import AVOC.OperationalExamples

open Komorebi.AVOC.MultiLevel
open Komorebi.AVOC.Affine.MultiLevelOperational
open Komorebi.AVOC.Affine.CertifiedOperational
open Komorebi.AVOC.Affine.OperationalExamples

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

example : acknowledgeTerminal (model catalogue) initial .reuse
    (.success coldDeployment) = some (terminal initial) := by
  rw [wrong_terminal_kind_rejected]
