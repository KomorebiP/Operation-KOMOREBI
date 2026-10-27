import KomorebiPhysics.LindbladExamples
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : (Matrix.single (0:Fin 2) (1:Fin 2) (4:ℂ)).conjTranspose *
    Matrix.single (0:Fin 2) (1:Fin 2) (4:ℂ) = Matrix.single 1 1 (4:ℂ) := by
  have h := square_root_is_essential
  simp_all
