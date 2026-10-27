import KomorebiPhysics.LindbladExamples
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : 0 ≤ deriv (fun t => relativeEntropy (population (localCurve t)) reference) 0 := by
  have h := local_relativeEntropy_strictly_decreases
  simp_all
