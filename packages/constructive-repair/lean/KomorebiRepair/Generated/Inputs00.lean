import KomorebiRepair.Wire
-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 01c80f8d719d3c8e1ca890d6684718c33681caab9879a1df0d7547c1613861f6
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case000
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(2, 1), (4, 1)], ![(1, 1), (2, 1)], ![(1, 1), (2, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case000

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 3c9904a6db6c2f52064569fefcfe301813f77f261c6a178a2950c310c41d8974
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case001
def wireD : WireMatrix 2 1 := (Matrix.of ![![(2, 3)], ![(4, 3)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 2)], ![(5, 6)]])
def R : Mat 2 1 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case001

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 6ecb1309602296f4a4dfedec8dd89d01a579d38944063562ee38aba4fcf73571
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case002
def wireD : WireMatrix 0 2 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 2 := decodeWireMatrix wireD
def wireR : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 3 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case002

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: c0a800bf8159f9b8ade06223648b54e9f580eb3d8d38ac507d13b098f5415b15
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case003
def wireD : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def D : Mat 3 0 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)], ![(0, 1), (0, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case003

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: b86df25b6aa2f31267d1956d574d347ad0071a0994bebc21626410772a4414c2
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case004
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(2, 1)], ![(3, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case004

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 8a913548c95cfcf4f7c16681181a179e2282b09acfb14715e66cd4602df8402d
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case005
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(2, 1)], ![(3, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(0, 1), (0, 1)], ![(0, 1), (0, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case005
