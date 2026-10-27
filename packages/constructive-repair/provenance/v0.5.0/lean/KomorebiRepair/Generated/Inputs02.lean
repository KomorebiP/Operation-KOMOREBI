import KomorebiRepair.Wire
-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 29cb4b4f324fbd1fd78fe3ca186e5a20ddecbc35052afb9be5859d7ca0874b6f
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case012
def wireD : WireMatrix 3 2 := (Matrix.of ![![(-2, 1), (-4, 1)], ![(-2, 3), (-4, 3)], ![(-1, 5), (-2, 5)]])
def D : Mat 3 2 := decodeWireMatrix wireD
def wireR : WireMatrix 3 2 := (Matrix.of ![![(-2, 5), (-3, 4)], ![(2, 1), (-4, 3)], ![(1, 1), (4, 3)]])
def R : Mat 3 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case012

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 7364020c1f709575ae1572491c4489258e79a59db349689e1221731d96b74364
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case013
def wireD : WireMatrix 3 4 := (Matrix.of ![![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)], ![(0, 1), (0, 1), (0, 1), (0, 1)]])
def D : Mat 3 4 := decodeWireMatrix wireD
def wireR : WireMatrix 3 3 := (Matrix.of ![![(0, 1), (3, 1), (3, 2)], ![(-1, 3), (-1, 1), (1, 4)], ![(2, 5), (-2, 5), (-1, 2)]])
def R : Mat 3 3 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case013

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: e044c72d704a3f3569d27a9756b183588df7401574755a63d5306868f598c77f
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case014
def wireD : WireMatrix 2 2 := (Matrix.of ![![(3, 2), (3, 10)], ![(-15, 4), (-3, 5)]])
def D : Mat 2 2 := decodeWireMatrix wireD
def wireR : WireMatrix 2 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 2 0 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case014

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: f191953f33634560a19a3a2333cbf852fe9803362de5fd106b3da191caf454d5
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case015
def wireD : WireMatrix 2 1 := (Matrix.of ![![(9, 4)], ![(6, 5)]])
def D : Mat 2 1 := decodeWireMatrix wireD
def wireR : WireMatrix 2 2 := (Matrix.of ![![(-1, 2), (1, 1)], ![(2, 1), (-1, 3)]])
def R : Mat 2 2 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case015

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: e92112d84db6b36d8c8544a29ea2ca40f789588ae6271bdc6ed47b88c9e8c4f3
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case016
def wireD : WireMatrix 3 2 := (Matrix.of ![![(0, 1), (0, 1)], ![(0, 1), (0, 1)], ![(0, 1), (0, 1)]])
def D : Mat 3 2 := decodeWireMatrix wireD
def wireR : WireMatrix 3 0 := (Matrix.of fun _ j => Fin.elim0 j)
def R : Mat 3 0 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case016

-- Fixed original problem, emitted independently of certificate contents.
-- Canonical problem SHA256: 846d86d2581ca6c1bdd441592ffe8f622eb33ed8b99d4578317c10585cb554be
set_option autoImplicit false
set_option maxRecDepth 100000
open KomorebiRepair.RationalCertificates
namespace Case017
def wireD : WireMatrix 0 3 := (Matrix.of fun i => Fin.elim0 i)
def D : Mat 0 3 := decodeWireMatrix wireD
def wireR : WireMatrix 0 4 := (Matrix.of fun i => Fin.elim0 i)
def R : Mat 0 4 := decodeWireMatrix wireR
theorem input_encoding_valid : WireMatrixValid wireD ∧ WireMatrixValid wireR := by decide +kernel
end Case017
