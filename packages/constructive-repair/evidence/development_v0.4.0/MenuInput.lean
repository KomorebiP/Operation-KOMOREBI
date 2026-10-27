import KomorebiRepair.RationalMenuCover
-- Independently emitted original problem.
-- Canonical input SHA256: 59a5d2fab313c6943062f69ccbc13badb6fb21b1900af2f8fb1990fd74e4998c
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace DemoMenu
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : List (Finset (Fin 2)) := [{}, {0}, {1}, {0, 1}]
def original : Problem 3 1 2 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end DemoMenu
