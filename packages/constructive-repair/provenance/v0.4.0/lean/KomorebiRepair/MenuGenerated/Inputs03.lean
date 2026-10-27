import KomorebiRepair.RationalMenuCover

-- Independently emitted original problem.
-- Canonical input SHA256: 49c6f584187c07858b83541909a34a9eab1d7266b462c4c96419acc564a86541
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase012
def wireD : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def D : Mat 2 2 := decodeWireMatrix wireD
def wireE : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 2 0 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 0 → ℕ := (fun j => Fin.elim0 j)
def admitted : List (Finset (Fin 0)) := [{}]
def original : Problem 2 2 0 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase012
-- Independently emitted original problem.
-- Canonical input SHA256: 5a321607a1f119edb51890b3e5d66e84bae9d592b4dc7ee3d317a598a7136765
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase013
def wireD : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 2 0 := decodeWireMatrix wireD
def wireE : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 2 0 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 0 → ℕ := (fun j => Fin.elim0 j)
def admitted : List (Finset (Fin 0)) := [{}]
def original : Problem 2 0 0 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase013
-- Independently emitted original problem.
-- Canonical input SHA256: 417c7bbab019dcf8989f76c752edda28f19b386004fe96fcf653f3fb1dc28122
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase014
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireE : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireR : WireMatrix 3 2 := (Matrix.of ![![(2, 1), (3, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![2, 4]
def admitted : List (Finset (Fin 2)) := [{}, {0}, {1}, {0, 1}]
def original : Problem 3 1 2 2 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase014
-- Independently emitted original problem.
-- Canonical input SHA256: 92fff92cd0e18f67bc5e4577b111e92145c2be093fb313b3930f6d6779c43510
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace MenuCase015
def wireD : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def D : Mat 2 2 := decodeWireMatrix wireD
def wireE : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def E : Mat 2 2 := decodeWireMatrix wireE
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(2, 1)]])
def R : Mat 2 1 := decodeWireMatrix wireR
def weights : Fin 2 → ℕ := ![5, 1]
def admitted : List (Finset (Fin 2)) := [{0}, {1}, {0, 1}]
def original : Problem 2 2 2 1 :=
  ⟨D, E, R, tableAllowed admitted, additiveCost weights⟩
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireE ∧ WireMatrixValid wireR := by decide +kernel
end MenuCase015