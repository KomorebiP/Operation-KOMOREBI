import KomorebiRepair.RationalMenuCover
-- Independently emitted original problem.
-- Canonical input SHA256: 219f811fd959e2b7753930229a70ec3744c100b63e4821e8a9c0840ba2ef4e13
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace UserMenu
def wireD : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireE : WireMatrix 2 1 := (Matrix.of ![![(0, 1)], ![(2, 3)]])
def E : Mat 2 1 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 2)], ![(5, 6)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 1 → ℕ := ![7]
def admitted : List (Finset (Fin 1)) := [{}, {0}]
def original : Problem 2 1 1 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end UserMenu
