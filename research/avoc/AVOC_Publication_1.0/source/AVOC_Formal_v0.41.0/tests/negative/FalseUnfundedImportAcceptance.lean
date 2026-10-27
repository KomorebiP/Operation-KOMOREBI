import AVOC.SemanticLibrary
open Komorebi.AVOC.SemanticLibrary
-- No credit does not authorize a validation attempt.
example : (paidImport #[] 0).attempted = true := by decide
