import KomorebiPhysics.LindbladExamples
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : deriv (fun t => relativeEntropy (population (biasedCurve t)) (fun _ => (1/2:ℝ))) 0 ≤ 0 := by
  have h := wrong_reference_strictly_increases
  simp_all
