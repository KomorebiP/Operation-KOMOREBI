import KomorebiPhysics.RefinementExamples
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 2 (fun h : ℝ => h^2) 1 =O[𝓝[≠] 0] (fun h : ℝ => h^3) := by
  simp only [quadratic_not_third_order]
