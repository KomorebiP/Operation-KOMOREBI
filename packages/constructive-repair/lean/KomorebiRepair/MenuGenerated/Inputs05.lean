import KomorebiRepair.RationalMenuCover

-- Independently emitted original problem.
-- Canonical input SHA256: b0f07f4d16f7c9b0b52864d91b0c3fec1597d7f74a3ffdb6efe0fd9eb63beba2
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase020
def wireD : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 0 := decodeWireMatrix wireD
def wireE : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def E : Mat 0 0 := decodeWireMatrix wireE
def wireR : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 2 := decodeWireMatrix wireR
def weights : Fin 0 → ℕ := (fun j => Fin.elim0 j)
def admitted : List (Finset (Fin 0)) := [{}]
def original : Problem 0 0 0 2 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase020
-- Independently emitted original problem.
-- Canonical input SHA256: 8ba750209258932800b36e6bf4d7dc6e3ecf5de1e518e431f8b0836cec55194d
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase021
def wireD : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 2 := decodeWireMatrix wireD
def wireE : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def E : Mat 0 3 := decodeWireMatrix wireE
def wireR : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 3 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![4, 0, 2]
def admitted : List (Finset (Fin 3)) := [{}, {0}, {1}, {0, 1}, {1, 2}]
def original : Problem 0 2 3 3 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase021
-- Independently emitted original problem.
-- Canonical input SHA256: 2819232cbab5fcfc7e04cee15228a0c996c6f0616ac5707bfd26bf7adb20c403
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase022
def wireD : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 4 0 := decodeWireMatrix wireD
def wireE : WireMatrix 4 3 := (Matrix.of ![![(2, 1), (2, 1), (1, 2)], ![(-2, 3), (2, 3), (1, 2)], ![(0, 1), (0, 1), (0, 1)], ![(0, 1), (-1, 2), (3, 4)]])
def E : Mat 4 3 := decodeWireMatrix wireE
def wireR : WireMatrix 4 1 := (Matrix.of ![![(-1, 4)], ![(-1, 1)], ![(0, 1)], ![(3, 2)]])
def R : Mat 4 1 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![2, 2, 0]
def admitted : List (Finset (Fin 3)) := [{}, {0}, {1}, {0, 1}, {2}, {1, 2}, {0, 1, 2}]
def original : Problem 4 0 3 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase022
-- Independently emitted original problem.
-- Canonical input SHA256: dcdc1bea356e608335ed8e95d54d84a979710546d2c600eda453d7a60b7b27d0
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase023
def wireD : WireMatrix 3 1 := (Matrix.of ![![(-3, 1)], ![(-3, 4)], ![(3, 2)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 3 := (Matrix.of ![![(-1, 1), (-1, 4), (2, 3)], ![(1, 2), (-1, 2), (3, 1)], ![(0, 1), (2, 1), (1, 4)]])
def E : Mat 3 3 := decodeWireMatrix wireE
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
def weights : Fin 3 → ℕ := ![1, 3, 0]
def admitted : List (Finset (Fin 3)) := [{0}, {1}, {0, 1}, {0, 2}, {1, 2}, {0, 1, 2}]
def original : Problem 3 1 3 0 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase023