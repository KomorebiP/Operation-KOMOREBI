import KomorebiRepair.RationalMenuCover

-- Independently emitted original problem.
-- Canonical input SHA256: 6ac4816568e3b0d9a97bac30277cbed2ed0514c0bb5d3e1d78d67e12b255b429
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase016
def wireD : WireMatrix 3 3 := (Matrix.of ![![(-3, 2), (1, 1), (0, 1)], ![(-3, 4), (-1, 1), (1, 4)], ![(-1, 3), (-2, 3), (1, 2)]])
def D : Mat 3 3 := decodeWireMatrix wireD
def wireE : WireMatrix 3 4 := (Matrix.of ![![(-2, 1), (-2, 3), (1, 2), (-1, 3)], ![(0, 1), (-2, 3), (-3, 4), (1, 1)], ![(0, 1), (1, 1), (-1, 1), (-3, 2)]])
def E : Mat 3 4 := decodeWireMatrix wireE
def wireR : WireMatrix 3 1 := (Matrix.of ![![(1, 2)], ![(2, 3)], ![(1, 3)]])
def R : Mat 3 1 := decodeWireMatrix wireR
def weights : Fin 4 → ℕ := ![4, 3, 4, 0]
def admitted : List (Finset (Fin 4)) := [{0}, {0, 1}, {1, 2}, {0, 1, 2}, {0, 3}, {1, 3}, {0, 1, 3}, {2, 3}, {0, 2, 3}, {0, 1, 2, 3}]
def original : Problem 3 3 4 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase016
-- Independently emitted original problem.
-- Canonical input SHA256: 3a4203e986adfae3da4245d348f04c7819f196f848e7c27a366445476dd1c524
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase017
def wireD : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (1, 4)], ![(0, 1), (-2, 3)], ![(1, 3), (0, 1)]])
def D : Mat 3 2 := decodeWireMatrix wireD
def wireE : WireMatrix 3 1 := (Matrix.of ![![(-1, 1)], ![(-1, 4)], ![(1, 3)]])
def E : Mat 3 1 := decodeWireMatrix wireE
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
def weights : Fin 1 → ℕ := ![0]
def admitted : List (Finset (Fin 1)) := [{}]
def original : Problem 3 2 1 0 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase017
-- Independently emitted original problem.
-- Canonical input SHA256: 1d3ea94c607d36f6aebfaa4c492d0e703548cf9cabca81c603dd0b7858bae851
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase018
def wireD : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 1 0 := decodeWireMatrix wireD
def wireE : WireMatrix 1 3 := (Matrix.of ![![(-1, 1), (-3, 1), (1, 4)]])
def E : Mat 1 3 := decodeWireMatrix wireE
def wireR : WireMatrix 1 2 := (Matrix.of ![![(3, 2), (1, 2)]])
def R : Mat 1 2 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![3, 1, 1]
def admitted : List (Finset (Fin 3)) := [{}, {0}, {1}, {0, 1}, {2}, {0, 2}, {1, 2}, {0, 1, 2}]
def original : Problem 1 0 3 2 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase018
-- Independently emitted original problem.
-- Canonical input SHA256: af3ed923f3a99bfd35534d2db60708a7d6176af4f5bda415cb03e97d144aba37
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase019
def wireD : WireMatrix 1 2 := (Matrix.of ![![(1, 3), (-3, 4)]])
def D : Mat 1 2 := decodeWireMatrix wireD
def wireE : WireMatrix 1 1 := (Matrix.of ![![(1, 3)]])
def E : Mat 1 1 := decodeWireMatrix wireE
def wireR : WireMatrix 1 1 := (Matrix.of ![![(-2, 1)]])
def R : Mat 1 1 := decodeWireMatrix wireR
def weights : Fin 1 → ℕ := ![4]
def admitted : List (Finset (Fin 1)) := [{}]
def original : Problem 1 2 1 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase019