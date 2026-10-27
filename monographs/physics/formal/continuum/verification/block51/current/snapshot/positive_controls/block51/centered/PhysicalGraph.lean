import KomorebiPhysics.Relativistic3DCenteredConvergence
open Filter KomorebiPhysics
open Relativistic3DCenteredConvergence Relativistic3DWeightedDomain
open scoped Topology

example (f : physicalDiracDomain (-2)) :
    Tendsto (fun h => physicalCenteredOperator (-2) h f.1) (𝓝[≠] 0)
      (𝓝 (physicalDiracPMap (-2) f)) :=
  physical_centered_graph_tendsto (-2) f

example (f : Relativistic3DUnboundedDirac.continuumDiracDomain (-2)) :
    Tendsto (fun h => centeredCoeffOperator (-2) h f.1) (𝓝[≠] 0)
      (𝓝 (Relativistic3DUnboundedDirac.continuumDiracOutput (-2) f)) :=
  centered_graph_tendsto (-2) f
