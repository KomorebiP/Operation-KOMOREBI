import KomorebiPhysics.Relativistic3DFullWalkRefinement

open KomorebiPhysics
open Relativistic3DCubicalRefinement
open Relativistic3DFullWalkRefinement

/-- Deliberately false: one half-grid step reaches the midpoint, not the next
coarse endpoint. -/
example :
    halfShiftX (Equiv.refl Unit)
      ((), ⟨false, false, false⟩) =
    coarseLift (Equiv.refl Unit)
      ((), ⟨false, false, false⟩) := by
  simp [halfShiftX, coarseLift]
