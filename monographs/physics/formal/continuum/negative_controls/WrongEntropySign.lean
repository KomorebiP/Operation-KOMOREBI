import KomorebiPhysics.QuantumInformationExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : deriv (fun t => entropy (packetCurve 1 t)) 0 = -Real.log 3 := by
  rw [(packet_entropy_rate 1).deriv]
  have h : 0 < Real.log (3:ℝ) := Real.log_pos (by norm_num)
  simp_all
