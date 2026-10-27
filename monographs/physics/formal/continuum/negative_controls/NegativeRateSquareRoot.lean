import KomorebiPhysics.LindbladExamples
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : (Real.sqrt (-4:ℝ) : ℂ) * (Real.sqrt (-4:ℝ) : ℂ) = (-4:ℂ) := by
  have h := rate_nonnegativity_is_essential
  simp_all
