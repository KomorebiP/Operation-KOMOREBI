import AVOC.ObservationPolicy
open Komorebi.AVOC.ObservationPolicy
-- The first two reports have one success; a later success cannot change them.
example : availableCount 2 [true, false, true] = some ⟨2, by decide⟩ := by decide
