import KomorebiRepair.BranchCertificate

-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: a6e6340f65a06dab61f5657558bdc7d4fc11ec88c7553837c88e2854ce49f855
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase000
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : Option (List (Finset (Fin 2))) := none
def original : BranchProblem 3 1 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase000
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 9dbea5a7a5e66975596caac4c0e2b1aa87d5c5f0e88aab41c88d09a4fb679e3c
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase001
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : Option (List (Finset (Fin 2))) := (some [{}, {0}, {1}])
def original : BranchProblem 3 1 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase001
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: c025f255eba841faf17d79585c71149ad4ffac49688fb57777ebaaeb52634713
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase002
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(1, 1), (1, 1), (0, 1)], ![(0, 1), (1, 1), (1, 1)]])
def E : Mat 3 3 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![5, 1, 1]
def admitted : Option (List (Finset (Fin 3))) := none
def original : BranchProblem 3 1 3 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase002
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: ffd184c279b43a10a8222fc1dfa4b79df9ddeff3d3403f32209517d5be978fe4
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase003
def wireD : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireE : WireMatrix 2 1 := (Matrix.of ![![(0, 1)], ![(2, 3)]])
def E : Mat 2 1 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 2)], ![(5, 6)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 1 → ℕ := ![7]
def admitted : Option (List (Finset (Fin 1))) := none
def original : BranchProblem 2 1 1 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase003