import KomorebiPhysics.Relativistic3DCenteredConvergence
open Filter KomorebiPhysics Relativistic3DCenteredConvergence
open scoped Topology

-- Deliberately invalid: a general ℓ² field is not a supplied maximal-domain vector.
example (m : ℝ) (f : Relativistic3DCenteredConvergence.CoeffL2) :
    ∃ g, Tendsto (fun h => centeredCoeffOperator m h f) (𝓝[≠] 0) (𝓝 g) := by
  exact ⟨_, centered_graph_tendsto m f⟩
