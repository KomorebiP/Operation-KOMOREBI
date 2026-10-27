import KomorebiRepair.RationalMenuCover

-- Independently emitted original problem.
-- Canonical input SHA256: cee5fabeaf9c77b000dee364104dc7084aeb961114d50e5f29f27732bee6deb3
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase004
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
end MenuCase004
-- Independently emitted original problem.
-- Canonical input SHA256: 3cb0c0b5d3ca1ecf45135282e74bce1762d9dab2f3013bd5b00770275063e446
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase005
def wireD : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireE : WireMatrix 2 4 := (Matrix.of ![![(2, 1), (3, 1), (4, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (1, 1)]])
def E : Mat 2 4 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(0, 1)], ![(1, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 4 → ℕ := ![0, 0, 0, 3]
def admitted : List (Finset (Fin 4)) := [{}, {0}, {1}, {0, 1}, {2}, {0, 2}, {1, 2}, {0, 1, 2}, {3}, {0, 3}, {1, 3}, {0, 1, 3}, {2, 3}, {0, 2, 3}, {1, 2, 3}, {0, 1, 2, 3}]
def original : Problem 2 1 4 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase005
-- Independently emitted original problem.
-- Canonical input SHA256: 0e95d9f6efe684d593b34531f0e8d3ce115b14b884e9fb06dc404ed577ac321d
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase006
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![0, 0]
def admitted : List (Finset (Fin 2)) := [{}, {0}, {1}, {0, 1}]
def original : Problem 3 1 2 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase006
-- Independently emitted original problem.
-- Canonical input SHA256: 1433c529d8e87725eecef82eeac88dffa106f40fa5733ddb18ba4ca656af386c
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase007
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(1, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![1, 1]
def admitted : List (Finset (Fin 2)) := [{0, 1}]
def original : Problem 3 1 2 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase007