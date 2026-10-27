import KomorebiRepair.Generated.Inputs02
-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case012
def wireP : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (-5, 1)], ![(0, 1), (0, 1), (0, 1)]])
def P : Mat 2 3 := decodeWireMatrix wireP
def wireK : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)], ![(0, 1), (0, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(1, 1), (0, 1), (-10, 1)], ![(0, 1), (1, 1), (-10, 3)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireF : WireMatrix 2 2 := (Matrix.of ![![(-52, 5), (-169, 12)], ![(-4, 3), (-52, 9)]])
def F : Mat 2 2 := decodeWireMatrix wireF
def wireG : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def G : Mat 2 2 := decodeWireMatrix wireG
def wireJ : WireMatrix 2 2 := (Matrix.of ![![(-20, 143), (15, 44)], ![(60, 1859), (-36, 143)]])
def J : Mat 2 2 := decodeWireMatrix wireJ
def wireQ : WireMatrix 2 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def Q : Mat 2 2 := decodeWireMatrix wireQ
def wireE : WireMatrix 3 2 := (Matrix.of ![![(-52, 5), (-169, 12)], ![(-4, 3), (-52, 9)], ![(0, 1), (0, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireU : WireMatrix 2 2 := (Matrix.of ![![(5, 1), (20, 3)], ![(0, 1), (0, 1)]])
def U : Mat 2 2 := decodeWireMatrix wireU
def wireW : WireMatrix 2 2 := (Matrix.of ![![(-1, 1), (0, 1)], ![(0, 1), (-1, 1)]])
def W : Mat 2 2 := decodeWireMatrix wireW
def wireH : WireMatrix 2 3 := (Matrix.of ![![(-20, 143), (15, 44), (75, 286)], ![(60, 1859), (-36, 143), (960, 1859)]])
def H : Mat 2 3 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 3 w) (Uprime : Mat 2 2) (Wprime : Mat w 2),
    D * Uprime + Eprime * Wprime = -R → 2 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case012

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case013
def wireP : WireMatrix 4 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def P : Mat 4 3 := decodeWireMatrix wireP
def wireK : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def K : Mat 3 3 := decodeWireMatrix wireK
def wireL : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 3 3 := decodeWireMatrix wireL
def wireF : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (3, 1), (3, 2)], ![(-1, 3), (-1, 1), (1, 4)], ![(2, 5), (-2, 5), (-1, 2)]])
def F : Mat 3 3 := decodeWireMatrix wireF
def wireG : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def G : Mat 3 3 := decodeWireMatrix wireG
def wireJ : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (3, 2), (15, 4)], ![(-1, 9), (-1, 1), (-5, 6)], ![(8, 9), (2, 1), (5, 3)]])
def J : Mat 3 3 := decodeWireMatrix wireJ
def wireQ : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def Q : Mat 3 3 := decodeWireMatrix wireQ
def wireE : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (3, 1), (3, 2)], ![(-1, 3), (-1, 1), (1, 4)], ![(2, 5), (-2, 5), (-1, 2)]])
def E : Mat 3 3 := decodeWireMatrix wireE
def wireU : WireMatrix 4 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def U : Mat 4 3 := decodeWireMatrix wireU
def wireW : WireMatrix 3 3 := (Matrix.of ![![(-1, 1), (0, 1), (0, 1)], ![(0, 1), (-1, 1), (0, 1)], ![(0, 1), (0, 1), (-1, 1)]])
def W : Mat 3 3 := decodeWireMatrix wireW
def wireH : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (3, 2), (15, 4)], ![(-1, 9), (-1, 1), (-5, 6)], ![(8, 9), (2, 1), (5, 3)]])
def H : Mat 3 3 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 3 w) (Uprime : Mat 4 3) (Wprime : Mat w 3),
    D * Uprime + Eprime * Wprime = -R → 3 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case013

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case014
def wireP : WireMatrix 2 2 := (Matrix.of ![![(-8, 3), (-4, 3)], ![(50, 3), (20, 3)]])
def P : Mat 2 2 := decodeWireMatrix wireP
def wireK : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def K : Mat 2 0 := decodeWireMatrix wireK
def wireL : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def L : Mat 0 2 := decodeWireMatrix wireL
def wireF : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def F : Mat 0 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 0 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 0 := decodeWireMatrix wireJ
def wireQ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def Q : Mat 0 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 2 0 := decodeWireMatrix wireE
def wireU : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 2 0 := decodeWireMatrix wireU
def wireW : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 0 := decodeWireMatrix wireW
def wireH : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 2 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 2 w) (Uprime : Mat 2 0) (Wprime : Mat w 0),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case014

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case015
def wireP : WireMatrix 1 2 := (Matrix.of ![![(0, 1), (5, 6)]])
def P : Mat 1 2 := decodeWireMatrix wireP
def wireK : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def K : Mat 2 1 := decodeWireMatrix wireK
def wireL : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (-15, 8)]])
def L : Mat 1 2 := decodeWireMatrix wireL
def wireF : WireMatrix 1 1 := (Matrix.of ![![(-17, 4)]])
def F : Mat 1 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (-13, 34)]])
def G : Mat 1 2 := decodeWireMatrix wireG
def wireJ : WireMatrix 1 1 := (Matrix.of ![![(-4, 17)]])
def J : Mat 1 1 := decodeWireMatrix wireJ
def wireQ : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def Q : Mat 2 1 := decodeWireMatrix wireQ
def wireE : WireMatrix 2 1 := (Matrix.of ![![(-17, 4)], ![(0, 1)]])
def E : Mat 2 1 := decodeWireMatrix wireE
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-5, 3), (5, 18)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (13, 34)]])
def W : Mat 1 2 := decodeWireMatrix wireW
def wireH : WireMatrix 1 2 := (Matrix.of ![![(-4, 17), (15, 34)]])
def H : Mat 1 2 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 2 w) (Uprime : Mat 1 2) (Wprime : Mat w 2),
    D * Uprime + Eprime * Wprime = -R → 1 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case015

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case016
def wireP : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1)]])
def P : Mat 2 3 := decodeWireMatrix wireP
def wireK : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def K : Mat 3 3 := decodeWireMatrix wireK
def wireL : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 3 3 := decodeWireMatrix wireL
def wireF : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def F : Mat 3 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 0 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 3 := decodeWireMatrix wireJ
def wireQ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def Q : Mat 0 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 3 0 := decodeWireMatrix wireE
def wireU : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 2 0 := decodeWireMatrix wireU
def wireW : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 0 := decodeWireMatrix wireW
def wireH : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 3 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 3 w) (Uprime : Mat 2 0) (Wprime : Mat w 0),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case016

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case017
def wireP : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def P : Mat 3 0 := decodeWireMatrix wireP
def wireK : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def K : Mat 0 0 := decodeWireMatrix wireK
def wireL : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def L : Mat 0 0 := decodeWireMatrix wireL
def wireF : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def F : Mat 0 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 4 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 0 := decodeWireMatrix wireJ
def wireQ : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def Q : Mat 4 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def E : Mat 0 0 := decodeWireMatrix wireE
def wireU : WireMatrix 3 4 := (Matrix.of ![![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)]])
def U : Mat 3 4 := decodeWireMatrix wireU
def wireW : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 4 := decodeWireMatrix wireW
def wireH : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 0 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 0 w) (Uprime : Mat 3 4) (Wprime : Mat w 4),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case017
