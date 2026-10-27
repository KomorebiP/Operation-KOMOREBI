import KomorebiPhysics.QuantumInformationExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : PartialTrace.left ((1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ
    (1 : Matrix (Fin 2) (Fin 2) ℂ)) = (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  rw [partial_trace_identity_factor]
  ext i j
  norm_num
