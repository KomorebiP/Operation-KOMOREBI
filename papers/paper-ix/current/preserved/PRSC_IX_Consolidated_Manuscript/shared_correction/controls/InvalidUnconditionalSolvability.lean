import SharedCorrectionControls

open Komorebi.SharedCorrectionControls

-- EXPECTED FAILURE: one correction cannot realize two arbitrary identity targets.
example (a b : Two) : ∃ w : Two, identity w = a ∧ identity w = b := by
  exact ⟨a, rfl, rfl⟩
