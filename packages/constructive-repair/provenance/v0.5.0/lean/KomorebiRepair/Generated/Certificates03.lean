import KomorebiRepair.Generated.Inputs03
-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case018
def wireP : WireMatrix 3 2 := (Matrix.of ![![(2, 1), (2, 1)], ![(1, 3), (1, 12)], ![(0, 1), (0, 1)]])
def P : Mat 3 2 := decodeWireMatrix wireP
def wireK : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def K : Mat 2 0 := decodeWireMatrix wireK
def wireL : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def L : Mat 0 2 := decodeWireMatrix wireL
def wireF : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def F : Mat 0 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 4 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 0 := decodeWireMatrix wireJ
def wireQ : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def Q : Mat 4 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 2 0 := decodeWireMatrix wireE
def wireU : WireMatrix 3 4 := (Matrix.of ![![(4, 1), (-2, 1), (9, 2), (22, 5)], ![(2, 3), (5, 12), (1, 4), (-1, 60)], ![(0, 1), (0, 1), (0, 1), (0, 1)]])
def U : Mat 3 4 := decodeWireMatrix wireU
def wireW : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 4 := decodeWireMatrix wireW
def wireH : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 2 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 2 w) (Uprime : Mat 3 4) (Wprime : Mat w 4),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case018

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case019
def wireP : WireMatrix 4 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def P : Mat 4 1 := decodeWireMatrix wireP
def wireK : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def K : Mat 1 1 := decodeWireMatrix wireK
def wireL : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def L : Mat 1 1 := decodeWireMatrix wireL
def wireF : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def F : Mat 1 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 1 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 1 := decodeWireMatrix wireJ
def wireQ : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def Q : Mat 1 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 1 0 := decodeWireMatrix wireE
def wireU : WireMatrix 4 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def U : Mat 4 1 := decodeWireMatrix wireU
def wireW : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 1 := decodeWireMatrix wireW
def wireH : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 1 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 1 w) (Uprime : Mat 4 1) (Wprime : Mat w 1),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case019

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case020
def wireP : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (0, 1), (-15, 4)]])
def P : Mat 1 3 := decodeWireMatrix wireP
def wireK : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)], ![(0, 1), (0, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(1, 1), (0, 1), (-6, 5)], ![(0, 1), (1, 1), (-3, 1)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireF : WireMatrix 2 2 := (Matrix.of ![![(1, 2), (-1, 5)], ![(2, 1), (-2, 1)]])
def F : Mat 2 2 := decodeWireMatrix wireF
def wireG : WireMatrix 2 3 := (Matrix.of ![![(1, 1), (0, 1), (13, 5)], ![(0, 1), (1, 1), (3, 10)]])
def G : Mat 2 3 := decodeWireMatrix wireG
def wireJ : WireMatrix 2 2 := (Matrix.of ![![(10, 3), (-1, 3)], ![(10, 3), (-5, 6)]])
def J : Mat 2 2 := decodeWireMatrix wireJ
def wireQ : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)], ![(0, 1), (0, 1)]])
def Q : Mat 3 2 := decodeWireMatrix wireQ
def wireE : WireMatrix 3 2 := (Matrix.of ![![(1, 2), (-1, 5)], ![(2, 1), (-2, 1)], ![(0, 1), (0, 1)]])
def E : Mat 3 2 := decodeWireMatrix wireE
def wireU : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (15, 4), (-3, 4)]])
def U : Mat 1 3 := decodeWireMatrix wireU
def wireW : WireMatrix 2 3 := (Matrix.of ![![(-1, 1), (0, 1), (-13, 5)], ![(0, 1), (-1, 1), (-3, 10)]])
def W : Mat 2 3 := decodeWireMatrix wireW
def wireH : WireMatrix 2 3 := (Matrix.of ![![(10, 3), (-1, 3), (-3, 1)], ![(10, 3), (-5, 6), (-3, 2)]])
def H : Mat 2 3 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 3 w) (Uprime : Mat 1 3) (Wprime : Mat w 3),
    D * Uprime + Eprime * Wprime = -R → 2 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case020

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case021
def wireP : WireMatrix 4 4 := (Matrix.of ![![(-28043, 85337), (-345854, 1280055), (-2484, 60955), (-42192, 85337)], ![(-494265, 341348), (6841, 170674), (5949, 12191), (91800, 85337)], ![(228315, 341348), (11891, 512022), (453, 12191), (-61176, 85337)], ![(322661, 341348), (-488351, 2560110), (-19773, 60955), (-62352, 85337)]])
def P : Mat 4 4 := decodeWireMatrix wireP
def wireK : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def K : Mat 4 0 := decodeWireMatrix wireK
def wireL : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def L : Mat 0 4 := decodeWireMatrix wireL
def wireF : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def F : Mat 0 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 0 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 0 := decodeWireMatrix wireJ
def wireQ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def Q : Mat 0 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def E : Mat 4 0 := decodeWireMatrix wireE
def wireU : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def U : Mat 4 0 := decodeWireMatrix wireU
def wireW : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 0 := decodeWireMatrix wireW
def wireH : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 4 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 4 w) (Uprime : Mat 4 0) (Wprime : Mat w 0),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case021

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case022
def wireP : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def P : Mat 1 0 := decodeWireMatrix wireP
def wireK : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def K : Mat 0 0 := decodeWireMatrix wireK
def wireL : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def L : Mat 0 0 := decodeWireMatrix wireL
def wireF : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def F : Mat 0 0 := decodeWireMatrix wireF
def wireG : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def G : Mat 0 1 := decodeWireMatrix wireG
def wireJ : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def J : Mat 0 0 := decodeWireMatrix wireJ
def wireQ : WireMatrix 1 0 := (Matrix.of fun _ j => Fin.elim0 j)
def Q : Mat 1 0 := decodeWireMatrix wireQ
def wireE : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def E : Mat 0 0 := decodeWireMatrix wireE
def wireU : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def U : Mat 1 1 := decodeWireMatrix wireU
def wireW : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def W : Mat 0 1 := decodeWireMatrix wireW
def wireH : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def H : Mat 0 0 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 0 w) (Uprime : Mat 1 1) (Wprime : Mat w 1),
    D * Uprime + Eprime * Wprime = -R → 0 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case022

-- Untrusted certificate data; original D and R are fixed imports.
set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 3000000
open KomorebiRepair.RationalCertificates
namespace Case023
def wireP : WireMatrix 4 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def P : Mat 4 1 := decodeWireMatrix wireP
def wireK : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def K : Mat 1 1 := decodeWireMatrix wireK
def wireL : WireMatrix 1 1 := (Matrix.of ![![(1, 1)]])
def L : Mat 1 1 := decodeWireMatrix wireL
def wireF : WireMatrix 1 1 := (Matrix.of ![![(1, 5)]])
def F : Mat 1 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 4 := (Matrix.of ![![(1, 1), (0, 1), (10, 3), (-5, 3)]])
def G : Mat 1 4 := decodeWireMatrix wireG
def wireJ : WireMatrix 1 1 := (Matrix.of ![![(5, 1)]])
def J : Mat 1 1 := decodeWireMatrix wireJ
def wireQ : WireMatrix 4 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)], ![(0, 1)]])
def Q : Mat 4 1 := decodeWireMatrix wireQ
def wireE : WireMatrix 1 1 := (Matrix.of ![![(1, 5)]])
def E : Mat 1 1 := decodeWireMatrix wireE
def wireU : WireMatrix 4 4 := (Matrix.of ![![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)]])
def U : Mat 4 4 := decodeWireMatrix wireU
def wireW : WireMatrix 1 4 := (Matrix.of ![![(-1, 1), (0, 1), (-10, 3), (5, 3)]])
def W : Mat 1 4 := decodeWireMatrix wireW
def wireH : WireMatrix 1 1 := (Matrix.of ![![(5, 1)]])
def H : Mat 1 1 := decodeWireMatrix wireH
theorem certificate_encoding_valid : WireMatrixValid wireP ∧ WireMatrixValid wireK ∧ WireMatrixValid wireL ∧ WireMatrixValid wireF ∧ WireMatrixValid wireG ∧ WireMatrixValid wireJ ∧ WireMatrixValid wireQ ∧ WireMatrixValid wireE ∧ WireMatrixValid wireU ∧ WireMatrixValid wireW ∧ WireMatrixValid wireH := by decide +kernel
theorem certificate_checked : checkOptimalConstruction D R P K L F G J Q = true := by decide +kernel
theorem original_equations_checked : D * U + E * W = -R := by decide +kernel
theorem output_matches_construction : E = K * F ∧ U = -(P * R) ∧ W = -G ∧ H = J * L := by decide +kernel
theorem optimal : D * U + E * W = -R ∧
    ∀ (w : ℕ) (Eprime : Mat 1 w) (Uprime : Mat 4 4) (Wprime : Mat w 4),
    D * Uprime + Eprime * Wprime = -R → 1 ≤ w := by
  exact ⟨original_equations_checked,
    (checkOptimalConstruction_sound D R P K L F G J Q certificate_checked).2⟩
end Case023
