import KomorebiPhysics.Relativistic3DCliffordHilbertRefinement

open KomorebiPhysics.Relativistic3DCliffordTransportU1
open KomorebiPhysics.Relativistic3DCliffordHilbertRefinement

variable {Site : Type*} [Fintype Site]

/-- Deliberately false: raw counting measure doubles under two-child replication. -/
theorem rawReplicationIsometry
    (ψ φ : State (Site := Site)) :
    stateIP (Site := FineSite Site) (replicateState ψ) (replicateState φ) =
      stateIP ψ φ := by
  rw [replicateState_stateIP]
