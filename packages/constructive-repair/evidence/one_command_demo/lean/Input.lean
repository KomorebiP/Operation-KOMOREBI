import KomorebiRepair.Wire
-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 3c9904a6db6c2f52064569fefcfe301813f77f261c6a178a2950c310c41d8974
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace UserRepair
def wireD : WireMatrix 2 1 := (Matrix.of ![![(2, 3)], ![(4, 3)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireR : WireMatrix 2 1 := (Matrix.of ![![(1, 2)], ![(5, 6)]])
def R : Mat 2 1 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end UserRepair
