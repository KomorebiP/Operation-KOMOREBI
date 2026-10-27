import KomorebiPhysics.QuantumInformationExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : (binaryAtlas.tensor binaryAtlas).probability bell (0,0) =
    binaryAtlas.probability (PartialTrace.left bell) 0 *
      binaryAtlas.probability (PartialTrace.right bell) 0 := by
  rw [bell_joint_probability, bell_left, bell_right, halfIdentity_probability]
  norm_num
