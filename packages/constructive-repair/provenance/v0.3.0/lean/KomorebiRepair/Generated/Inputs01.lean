import KomorebiRepair.Wire
-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 230880a71c0b0621e249d4195ceb680a5190813267f01369130c0c9eb10494d1
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case006
def wireD : WireMatrix 3 3 := (Matrix.of ![![(1, 1), (0, 1), (0, 1)], ![(0, 1), (1, 1), (0, 1)], ![(0, 1), (0, 1), (1, 1)]])
def D : Mat 3 3 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (3, 1)], ![(2, 1), (1, 1)], ![(3, 1), (7, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case006

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 8d081c98ea0368b34c31482551ac70d961f98dbfb25990f3b1fda233e69aa0d3
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case007
def wireD : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(0, 1), (0, 1)], ![(0, 1), (0, 1)]])
def D : Mat 3 2 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)], ![(1, 1), (1, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case007

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 14af328aec1d86d54ca41b37d0c297126fe89f1bb2cbbb5810e2216422e2bd1f
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case008
def wireD : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 0 := decodeWireMatrix wireD
def wireR : WireMatrix 0 0 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 0 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case008

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 17eef2e0e0264bd243ba45ddc5f47ec8c0853d840e5ccda990ae38d12982fe40
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case009
def wireD : WireMatrix 4 2 := (Matrix.of ![![(1, 1), (2, 1)], ![(2, 1), (4, 1)], ![(0, 1), (0, 1)], ![(0, 1), (0, 1)]])
def D : Mat 4 2 := decodeWireMatrix wireD
def wireR : WireMatrix 4 2 := (Matrix.of ![![(1, 1), (0, 1)], ![(0, 1), (1, 1)], ![(1, 1), (2, 1)], ![(0, 1), (1, 1)]])
def R : Mat 4 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case009

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: e8878bd6c73c6212f3f5868b74cd33309188b40d9af5fe2b209187bd187c12d2
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case010
def wireD : WireMatrix 3 1 := (Matrix.of ![![(0, 1)], ![(0, 1)], ![(0, 1)]])
def D : Mat 3 1 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(1, 4), (-1, 1)], ![(1, 2), (2, 1)], ![(-1, 1), (0, 1)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case010

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: c1eac19e7192610d0019a3b6b86c98bbb9ecff0b9143c19cfab78d94dc0cc53b
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case011
def wireD : WireMatrix 3 3 := (Matrix.of ![![(-119, 30), (4, 5), (-1, 40)], ![(239, 60), (13, 5), (241, 80)], ![(-1, 6), (-11, 8), (-29, 16)]])
def D : Mat 3 3 := decodeWireMatrix wireD
def wireR : WireMatrix 3 1 := (Matrix.of ![![(1, 1)], ![(-1, 1)], ![(0, 1)]])
def R : Mat 3 1 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case011
