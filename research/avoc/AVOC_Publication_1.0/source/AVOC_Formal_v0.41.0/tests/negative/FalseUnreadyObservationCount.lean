import AVOC.ObservationPolicy
open Komorebi.AVOC.ObservationPolicy
-- One report cannot populate a predeclared two-report checkpoint.
example : availableCount 2 [true] = some ⟨1, by decide⟩ := by decide
