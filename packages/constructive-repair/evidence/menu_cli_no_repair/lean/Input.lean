import KomorebiRepair.RationalMenuCover
-- Independently emitted original problem.
-- Canonical input SHA256: cee5fabeaf9c77b000dee364104dc7084aeb961114d50e5f29f27732bee6deb3
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace UserMenu
def wireD : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireE : WireMatrix 2 4 := (Matrix.of ![![(2, 1), (3, 1), (4, 1), (5, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)]])
def E : Mat 2 4 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(0, 1)], ![(1, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 4 → ℕ := ![1, 1, 1, 1]
def admitted : List (Finset (Fin 4)) := [{}, {0}, {1}, {0, 1}, {2}, {0, 2}, {1, 2}, {0, 1, 2}, {3}, {0, 3}, {1, 3}, {0, 1, 3}, {2, 3}, {0, 2, 3}, {1, 2, 3}, {0, 1, 2, 3}]
def original : Problem 2 1 4 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end UserMenu
