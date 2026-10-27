import KomorebiPhysics.QuantumInformationExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : 0 ≤ deriv (fun t => entropy (packetCurve (-1) t)) 0 := by
  have h := negative_entropy_rate
  simp_all
