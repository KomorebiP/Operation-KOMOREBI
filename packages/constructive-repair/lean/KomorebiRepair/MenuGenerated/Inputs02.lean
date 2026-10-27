import KomorebiRepair.RationalMenuCover

-- Independently emitted original problem.
-- Canonical input SHA256: 1ef1bdebda90d60ecf7ac84941c3774e9b2fefdcf83508eff0bc9e88b619389d
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase008
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : List (Finset (Fin 2)) := []
def original : Problem 3 1 2 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase008
-- Independently emitted original problem.
-- Canonical input SHA256: 910f6816663d8e0fa489c4735e5ea8ccddaeb04715ca7ebcec3b45611b1b675a
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase009
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : List (Finset (Fin 2)) := [{}, {0}, {1}, {0, 1}]
def original : Problem 3 1 2 0 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase009
-- Independently emitted original problem.
-- Canonical input SHA256: fe67f28221a91b44e87ff96e45369f1aa92be9a3b093601a7a891c46e3a7f37d
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase010
def wireD : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 2 := decodeWireMatrix wireD
def wireE : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def E : Mat 0 2 := decodeWireMatrix wireE
def wireR : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 3 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 2]
def admitted : List (Finset (Fin 2)) := [{}, {0}, {1}, {0, 1}]
def original : Problem 0 2 2 3 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase010
-- Independently emitted original problem.
-- Canonical input SHA256: 65a167de51995921fffaae56a3177ee7617c47540054dc9675e8877209c7bfba
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase011
def wireD : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 2 0 := decodeWireMatrix wireD
def wireE : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def E : Mat 2 2 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : List (Finset (Fin 2)) := [{}, {0}, {1}, {0, 1}]
def original : Problem 2 0 2 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase011