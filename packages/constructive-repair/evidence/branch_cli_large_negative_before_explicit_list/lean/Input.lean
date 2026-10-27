import KomorebiRepair.BranchCertificate
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 4ee0021d79033187ca82f60ec6a84b74c6554309f79662724ce3769629b5d1d0
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace UserBranch
def wireD : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireE : WireMatrix 2 24 := (Matrix.of ![![(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1), (19, 1), (20, 1), (21, 1), (22, 1), (23, 1), (24, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)]])
def E : Mat 2 24 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(0, 1)], ![(1, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 24 → ℕ := ![1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
def admitted : Option (List (Finset (Fin 24))) := none
def original : BranchProblem 2 1 24 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end UserBranch
