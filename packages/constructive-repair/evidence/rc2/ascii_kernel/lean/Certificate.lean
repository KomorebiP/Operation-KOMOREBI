import Input
-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace UserRepair
def wireP : WireMatrix 1 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)]])
def P : Mat 1 3 := decodeWireMatrix wireP
def wireK : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireF : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(1, 1)]])
def F : Mat 2 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (2, 1)]])
def G : Mat 1 2 := decodeWireMatrix wireG
def wireJ : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def J : Mat 1 2 := decodeWireMatrix wireJ
def wireQ : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def Q : Mat 2 1 := decodeWireMatrix wireQ
def wireE : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(1, 1)]])
def E : Mat 3 1 := decodeWireMatrix wireE
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-2, 1), (-4, 1)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (-2, 1)]])
def W : Mat 1 2 := decodeWireMatrix wireW
def wireH : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def H : Mat 1 3 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 3 w) (Uprime : Mat 1 2) (Wprime : Mat w 2),
    D * Uprime + Eprime * Wprime = -R → 1 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end UserRepair
