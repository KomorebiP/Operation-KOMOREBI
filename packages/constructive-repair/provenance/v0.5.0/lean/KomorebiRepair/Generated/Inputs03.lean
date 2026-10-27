import KomorebiRepair.Wire
-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 226d7e900145d1b2fec3217d5917a09aedf8cd6766a26089271b7b00b2968f84
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case018
def wireD : WireMatrix 2 3 := (Matrix.of ![![(-1, 6), (4, 1), (-2, 1)], ![(2, 3), (-4, 1), (2, 1)]])
def D : Mat 2 3 := decodeWireMatrix wireD
def wireR : WireMatrix 2 4 := (Matrix.of ![![(-2, 1), (-2, 1), (-1, 4), (4, 5)], ![(0, 1), (3, 1), (-2, 1), (-3, 1)]])
def R : Mat 2 4 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case018

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: bd3d11604b98ca5f80fdaecca7f97c6f69f8f8629293cb0c0b331be84a5c115e
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case019
def wireD : WireMatrix 1 4 := (Matrix.of ![![(0, 1), (0, 1), (0, 1), (0, 1)]])
def D : Mat 1 4 := decodeWireMatrix wireD
def wireR : WireMatrix 1 1 := (Matrix.of ![![(0, 1)]])
def R : Mat 1 1 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case019

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: e3848f055ceceb80686b401d49c2cf52931ad7acc68839ad68b475c82e28bbb9
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case020
def wireD : WireMatrix 3 1 := (Matrix.of ![![(-8, 25)], ![(-4, 5)], ![(-4, 15)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireR : WireMatrix 3 3 := (Matrix.of ![![(1, 2), (1, 1), (1, 1)], ![(2, 1), (1, 1), (4, 1)], ![(0, 1), (1, 1), (-1, 5)]])
def R : Mat 3 3 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case020

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: bcbd152ce3c0dc28d3156a0390069c98c0c2b66aa32623580845561c449d73b6
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case021
def wireD : WireMatrix 4 4 := (Matrix.of ![![(-19, 15), (19, 15), (3, 5), (32, 15)], ![(1, 4), (-43, 10), (0, 1), (-13, 2)], ![(-77, 72), (52, 15), (13, 4), (95, 36)], ![(-59, 48), (11, 9), (-2, 3), (23, 12)]])
def D : Mat 4 4 := decodeWireMatrix wireD
def wireR : WireMatrix 4 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 4 0 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case021

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 9ee65dfcd7ba82ad2049e8cb694d32c3e5dd1f0b5b541b45f762191a160e6846
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case022
def wireD : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 1 := decodeWireMatrix wireD
def wireR : WireMatrix 0 1 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 1 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case022

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: d2973e9749511f1858e595fa99ac170cb13ec33138b309bb99fe8b5c6491648b
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case023
def wireD : WireMatrix 1 4 := (Matrix.of ![![(0, 1), (0, 1), (0, 1), (0, 1)]])
def D : Mat 1 4 := decodeWireMatrix wireD
def wireR : WireMatrix 1 4 := (Matrix.of ![![(1, 5), (0, 1), (2, 3), (-1, 3)]])
def R : Mat 1 4 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case023
