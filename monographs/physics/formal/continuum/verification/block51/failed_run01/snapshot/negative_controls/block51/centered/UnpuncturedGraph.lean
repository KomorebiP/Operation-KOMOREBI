import KomorebiPhysics.Relativistic3DCenteredConvergence
open Filter KomorebiPhysics Relativistic3DCenteredConvergence Relativistic3DUnboundedDirac
open scoped Topology

-- Deliberately invalid: the auxiliary zero-spacing value is not the continuum output.
example (m : ℝ) (f : continuumDiracDomain m) :
    Tendsto (fun h => centeredCoeffOperator m h f.1) (𝓝 0) (𝓝 (continuumDiracOutput m f)) := by
  exact centered_graph_tendsto m f
