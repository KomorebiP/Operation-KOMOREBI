import Input
-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace UserRepair
def wireP : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (3, 4)]])
def P : Mat 1 2 := decodeWireMatrix wireP
def wireK : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def K : Mat 2 1 := decodeWireMatrix wireK
def wireL : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (-1, 2)]])
def L : Mat 1 2 := decodeWireMatrix wireL
def wireF : WireMatrix 1 1 := (Matrix.of ![![(1, 12)]])
def F : Mat 1 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def G : Mat 1 1 := decodeWireMatrix wireG
def wireJ : WireMatrix 1 1 := (Matrix.of ![![(12, 1)]])
def J : Mat 1 1 := decodeWireMatrix wireJ
def wireQ : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def Q : Mat 1 1 := decodeWireMatrix wireQ
def wireE : WireMatrix 2 1 := (Matrix.of ![![(1, 12)], ![(0, 1)]])
def E : Mat 2 1 := decodeWireMatrix wireE
def wireU : WireMatrix 1 1 := (Matrix.of ![![(-5, 8)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 1 1 := (Matrix.of ![![(-1, 1)]])
def W : Mat 1 1 := decodeWireMatrix wireW
def wireH : WireMatrix 1 2 := (Matrix.of ![![(12, 1), (-6, 1)]])
def H : Mat 1 2 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 2 w) (Uprime : Mat 1 1) (Wprime : Mat w 1),
    D * Uprime + Eprime * Wprime = -R → 1 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end UserRepair
