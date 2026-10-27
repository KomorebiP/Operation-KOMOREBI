import KomorebiPhysics.QuantumInformationExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : (∑ i : Fin 1, (1:ℝ) * ∑ _j : Fin 1, (1:ℝ)) =
    (1/2:ℝ) * ∑ _i : Fin 1, ∑ _j : Fin 1, (1:ℝ) * (1-1) := by
  norm_num
