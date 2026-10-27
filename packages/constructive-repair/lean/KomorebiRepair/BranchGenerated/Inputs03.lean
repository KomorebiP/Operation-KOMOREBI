import KomorebiRepair.BranchCertificate

-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 8c896b622b7f6675ef34d81c567e0b0b079071cd512a6b4608d917804ea6a41b
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase012
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 2 := (Matrix.of ![![(2, 1), (3, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![2, 4]
def admitted : Option (List (Finset (Fin 2))) := none
def original : BranchProblem 3 1 2 2 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase012
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: d81a9bae2114e516f1e4f07e8c61af5fc9704542c7e05eb31ab4f510f1d6826c
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase013
def wireD : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def D : Mat 2 2 := decodeWireMatrix wireD
def wireE : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def E : Mat 2 2 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![5, 1]
def admitted : Option (List (Finset (Fin 2))) := (some [{0}, {1}, {0, 1}])
def original : BranchProblem 2 2 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase013
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: dda1850553ce757cd0d04cca3dc80afe0d76fdf383c83011d5e5d5d854e9e1bb
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase014
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(1, 1), (1, 1), (1, 1)], ![(0, 1), (0, 1), (0, 1)]])
def E : Mat 3 3 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![3, 3, 3]
def admitted : Option (List (Finset (Fin 3))) := none
def original : BranchProblem 3 1 3 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase014
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 4268bc4c362e8d1cb173cdd0161750c0a81dbdd1f643b89016d842a2d7ce24de
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase015
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(1, 1), (0, 1), (1, 1)], ![(1, 1), (1, 1), (0, 1)]])
def E : Mat 3 3 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![1, 9, 4]
def admitted : Option (List (Finset (Fin 3))) := none
def original : BranchProblem 3 1 3 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase015