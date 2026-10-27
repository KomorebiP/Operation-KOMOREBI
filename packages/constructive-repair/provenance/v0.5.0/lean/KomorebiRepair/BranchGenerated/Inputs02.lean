import KomorebiRepair.BranchCertificate

-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: e48a8178c2efb79d1f84483bec5d347eb5083f65bf4c2c3c54f1410b3c98db86
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase008
def wireD : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 2 := decodeWireMatrix wireD
def wireE : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def E : Mat 0 2 := decodeWireMatrix wireE
def wireR : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 3 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 2]
def admitted : Option (List (Finset (Fin 2))) := none
def original : BranchProblem 0 2 2 3 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase008
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: dc9b490e0d889d4137e1ac9f132a49b291d5f042c0dd84234a6548cb3034e012
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase009
def wireD : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 2 0 := decodeWireMatrix wireD
def wireE : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def E : Mat 2 2 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : Option (List (Finset (Fin 2))) := none
def original : BranchProblem 2 0 2 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase009
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 5d2028216403fc4cb43b3a1e0405bf29fbb513a3aaacacaa4df61496ae5a5dc4
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase010
def wireD : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def D : Mat 2 2 := decodeWireMatrix wireD
def wireE : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 2 0 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 0 → ℕ := (fun j => Fin.elim0 j)
def admitted : Option (List (Finset (Fin 0))) := none
def original : BranchProblem 2 2 0 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase010
-- Original input, emitted independently of witnesses.
-- Canonical JSON SHA256: 0cc205195fcd105dd2f2108e3cddbeda158ee918c388c6dc882da40b91047203
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace BranchCase011
def wireD : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 2 0 := decodeWireMatrix wireD
def wireE : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 2 0 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 0 → ℕ := (fun j => Fin.elim0 j)
def admitted : Option (List (Finset (Fin 0))) := none
def original : BranchProblem 2 0 0 1 := ⟨D, E, R, weights, admitted⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end BranchCase011