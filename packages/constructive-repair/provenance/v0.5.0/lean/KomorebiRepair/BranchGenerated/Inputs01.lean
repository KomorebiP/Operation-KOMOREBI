import KomorebiRepair.BranchCertificate

-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 069a62c5ded1b5e4c0100c6a587e9c4a744e94f6cfb51d5b50ee0b4e563ec8ac
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase004
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![0, 0]
def admitted : Option (List (Finset (Fin 2))) := none
def original : BranchProblem 3 1 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase004
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 4dd1e7d417b52ec69dfee97967dcd66ad2386ffae63ae903caf84e8c475299b8
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase005
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : Option (List (Finset (Fin 2))) := (some [{0, 1}])
def original : BranchProblem 3 1 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase005
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 606d63809e1e71812b11d3206f362c7b99eae91679464639688572c5fcf3e53a
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase006
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : Option (List (Finset (Fin 2))) := (some [])
def original : BranchProblem 3 1 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase006
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: d36c37f80c419bf19d1272a80279aa63344c0cc17b828f5e28d625b23cb458cc
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase007
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : Option (List (Finset (Fin 2))) := none
def original : BranchProblem 3 1 2 0 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase007