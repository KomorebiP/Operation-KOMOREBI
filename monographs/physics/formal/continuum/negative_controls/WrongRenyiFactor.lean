import KomorebiPhysics.QuantumInformationExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : deriv (fun t => renyi (packetCurve 1 t) 2) 0 = (4/5:ℝ) := by
  rw [(packet_renyi_two_rate 1).deriv]
  norm_num
