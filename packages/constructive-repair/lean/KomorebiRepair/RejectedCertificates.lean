import KomorebiRepair.Generated.Inputs00
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace RejectBrokenSplit
abbrev D := Case000.D
abbrev R := Case000.R
def wireE : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(1, 1)]])
def E : Mat 3 1 := decodeWireMatrix wireE
def wireF : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(1, 1)]])
def F : Mat 2 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (2, 1)]])
def G : Mat 1 2 := decodeWireMatrix wireG
def wireH : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def H : Mat 1 3 := decodeWireMatrix wireH
def wireJ : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def J : Mat 1 2 := decodeWireMatrix wireJ
def wireK : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireP : WireMatrix 1 3 := (Matrix.of ![![(2, 1), (0, 1), (0, 1)]])
def P : Mat 1 3 := decodeWireMatrix wireP
def wireQ : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def Q : Mat 2 1 := decodeWireMatrix wireQ
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-2, 1), (-4, 1)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (-2, 1)]])
def W : Mat 1 2 := decodeWireMatrix wireW
def result : Bool := checkOptimalConstruction D R P K L F G J Q
theorem rejected : result = false := by decide +kernel
end RejectBrokenSplit
namespace RejectBrokenFactor
abbrev D := Case000.D
abbrev R := Case000.R
def wireE : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(1, 1)]])
def E : Mat 3 1 := decodeWireMatrix wireE
def wireF : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(1, 1)]])
def F : Mat 2 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 2 := (Matrix.of ![![(2, 1), (2, 1)]])
def G : Mat 1 2 := decodeWireMatrix wireG
def wireH : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def H : Mat 1 3 := decodeWireMatrix wireH
def wireJ : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def J : Mat 1 2 := decodeWireMatrix wireJ
def wireK : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireP : WireMatrix 1 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)]])
def P : Mat 1 3 := decodeWireMatrix wireP
def wireQ : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def Q : Mat 2 1 := decodeWireMatrix wireQ
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-2, 1), (-4, 1)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (-2, 1)]])
def W : Mat 1 2 := decodeWireMatrix wireW
def result : Bool := checkOptimalConstruction D R P K L F G J Q
theorem rejected : result = false := by decide +kernel
end RejectBrokenFactor
namespace RejectFalseDimension
abbrev D := Case000.D
abbrev R := Case000.R
def wireE : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(1, 1)]])
def E : Mat 3 1 := decodeWireMatrix wireE
def wireF : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(1, 1)]])
def F : Mat 2 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (2, 1)]])
def G : Mat 1 2 := decodeWireMatrix wireG
def wireH : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def H : Mat 1 3 := decodeWireMatrix wireH
def wireJ : WireMatrix 1 2 := (Matrix.of ![![(2, 1), (0, 1)]])
def J : Mat 1 2 := decodeWireMatrix wireJ
def wireK : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireP : WireMatrix 1 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)]])
def P : Mat 1 3 := decodeWireMatrix wireP
def wireQ : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def Q : Mat 2 1 := decodeWireMatrix wireQ
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-2, 1), (-4, 1)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (-2, 1)]])
def W : Mat 1 2 := decodeWireMatrix wireW
def result : Bool := checkOptimalConstruction D R P K L F G J Q
theorem rejected : result = false := by decide +kernel
end RejectFalseDimension
namespace RejectFalseOutput
abbrev D := Case000.D
abbrev R := Case000.R
def wireE : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(1, 1)], ![(1, 1)]])
def E : Mat 3 1 := decodeWireMatrix wireE
def wireF : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(1, 1)]])
def F : Mat 2 1 := decodeWireMatrix wireF
def wireG : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (2, 1)]])
def G : Mat 1 2 := decodeWireMatrix wireG
def wireH : WireMatrix 1 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)]])
def H : Mat 1 3 := decodeWireMatrix wireH
def wireJ : WireMatrix 1 2 := (Matrix.of ![![(1, 1), (0, 1)]])
def J : Mat 1 2 := decodeWireMatrix wireJ
def wireK : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(1, 1), (0, 1)], ![(0, 1), (1, 1)]])
def K : Mat 3 2 := decodeWireMatrix wireK
def wireL : WireMatrix 2 3 := (Matrix.of ![![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def L : Mat 2 3 := decodeWireMatrix wireL
def wireP : WireMatrix 1 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)]])
def P : Mat 1 3 := decodeWireMatrix wireP
def wireQ : WireMatrix 2 1 := (Matrix.of ![![(1, 1)], ![(0, 1)]])
def Q : Mat 2 1 := decodeWireMatrix wireQ
def wireU : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (-4, 1)]])
def U : Mat 1 2 := decodeWireMatrix wireU
def wireW : WireMatrix 1 2 := (Matrix.of ![![(-1, 1), (-2, 1)]])
def W : Mat 1 2 := decodeWireMatrix wireW
def result : Bool := decide (D * U + E * W = -R)
theorem rejected : result = false := by decide +kernel
end RejectFalseOutput
namespace RejectZeroDenominator
def result : Bool := checkWireMatrix (Matrix.of ![![(0,0)]] : WireMatrix 1 1)
theorem rejected : result = false := by decide +kernel
end RejectZeroDenominator
namespace RejectHiddenObstruction
def result : Bool := checkOptimalConstruction (0 : Mat 1 0) (1 : Mat 1 1) (0 : Mat 0 1) (0 : Mat 1 0) (0 : Mat 0 1) (0 : Mat 0 0) (0 : Mat 0 1) (0 : Mat 0 0) (0 : Mat 1 0)
theorem rejected : result = false := by decide +kernel
end RejectHiddenObstruction
