import AVOC.BooleanCostClosure
open Komorebi.AVOC.BoolClosure
-- An empty list is not a globally certified library.
example : checkBank #[] = true := by decide
