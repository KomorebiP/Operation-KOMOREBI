import KomorebiRepair.BranchCertificate

-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: f9b5786d526a7e933e7158a05b8b91ae350f9a9c5b75220d66754b5fe965e44d
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase020
def wireD : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 1 0 := decodeWireMatrix wireD
def wireE : WireMatrix 1 24 := (Matrix.of ![![(1, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]])
def E : Mat 1 24 := decodeWireMatrix wireE
def wireR : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def R : Mat 1 1 := decodeWireMatrix wireR
def weights : Fin 24 → ℕ := ![0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
def admitted : Option (List (Finset (Fin 24))) := none
def original : BranchProblem 1 0 24 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase020
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: ebc74c89e8b1ec4b5199d16267341ab0082df083d4d19bbe64d881571cea7b84
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase021
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 24 := (Matrix.of ![![(0, 1), (0, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)], ![(1, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]])
def E : Mat 3 24 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(1, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 24 → ℕ := ![2, 3, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
def admitted : Option (List (Finset (Fin 24))) := (some [{0, 1}])
def original : BranchProblem 3 1 24 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase021
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 45ec62cd7cb373df309dcbde41f648de74edaa517387d87e8bd7754aeb7f5845
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase022
def wireD : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 1 0 := decodeWireMatrix wireD
def wireE : WireMatrix 1 24 := (Matrix.of ![![(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]])
def E : Mat 1 24 := decodeWireMatrix wireE
def wireR : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def R : Mat 1 1 := decodeWireMatrix wireR
def weights : Fin 24 → ℕ := ![0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
def admitted : Option (List (Finset (Fin 24))) := (some [])
def original : BranchProblem 1 0 24 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase022
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: de3e96c27a9d428ea72da82cd80edd4d3c612d0a6b9b0a34a23073465df062dc
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase023
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![0, 2]
def admitted : Option (List (Finset (Fin 2))) := (some [{0}, {1}, {0, 1}])
def original : BranchProblem 3 1 2 0 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase023