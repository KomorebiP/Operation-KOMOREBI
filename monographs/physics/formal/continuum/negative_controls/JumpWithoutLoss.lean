import KomorebiPhysics.LindbladExamples
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : Matrix.trace (jump rates 0 1 * density * (jump rates 0 1).conjTranspose) = 0 := by
  rw [loss_terms_are_essential]
  norm_num
