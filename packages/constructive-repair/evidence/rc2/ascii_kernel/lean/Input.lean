import KomorebiRepair.Wire
-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 01c80f8d719d3c8e1ca890d6684718c33681caab9879a1df0d7547c1613861f6
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace UserRepair
def wireD : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(2, 1), (4, 1)], ![(1, 1), (2, 1)], ![(1, 1), (2, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end UserRepair
