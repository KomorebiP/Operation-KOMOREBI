import Mathlib.Tactic.NormNum

/-!
# Komorebi quantum arithmetic bridge

Exact finite formalization of the q = 12 example used in
"Mathematics Between Minds".

The file has two layers.

1. A rational projector layer proving exact filter, idempotence, symmetry,
   energy, and normalization claims.
2. An exact cyclotomic arithmetic layer for the 12th root of unity.  The
   cyclotomic values are represented in the basis 1, sqrt(3), i, i*sqrt(3)
   over Q, so no floating point approximation enters the Fourier claims.

This file is designed for a recent Mathlib environment.
-/

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000

namespace Komorebi.QuantumArithmetic

/-! ## 1. Exact rational signal and projector -/

abbrev QVector := List ℚ
abbrev QMatrix := List (List ℚ)

def dot (x y : QVector) : ℚ :=
  (List.zipWith (fun a b => a * b) x y).sum

def transposeN (n : Nat) (M : QMatrix) : QMatrix :=
  (List.range n).map (fun j => M.map (fun row => row.getD j 0))

def matMulN (n : Nat) (A B : QMatrix) : QMatrix :=
  A.map (fun row => (transposeN n B).map (fun col => dot row col))

def matVec (M : QMatrix) (v : QVector) : QVector :=
  M.map (fun row => dot row v)

def vecAdd (x y : QVector) : QVector :=
  List.zipWith (fun a b => a + b) x y

def vecSub (x y : QVector) : QVector :=
  List.zipWith (fun a b => a - b) x y

def sqEnergy (x : QVector) : ℚ := dot x x

/-- Ramanujan sum c_12(n), n = 0,...,11. -/
def ramanujan12 : QVector :=
  [4, 0, 2, 0, -2, 0, -4, 0, -2, 0, 2, 0]

/-- A deliberately off-band perturbation: 3 cos(pi n/2) + 2. -/
def noise12 : QVector :=
  [5, 2, -1, 2, 5, 2, -1, 2, 5, 2, -1, 2]

/-- Signal used in the essay's filter demonstration. -/
def testSignal12 : QVector :=
  [9, 2, 1, 2, 3, 2, -5, 2, 3, 2, 1, 2]

/-- P_nm = c_12(n-m)/12, written exactly over Q. -/
def projector12 : QMatrix :=
[
  [(1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0],
  [0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ)],
  [(1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0],
  [0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ)],
  [(-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0],
  [0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ)],
  [(-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0],
  [0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ)],
  [(-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ), 0],
  [0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0, (1 / 6 : ℚ)],
  [(1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ), 0],
  [0, (1 / 6 : ℚ), 0, (-1 / 6 : ℚ), 0, (-1 / 3 : ℚ), 0, (-1 / 6 : ℚ), 0, (1 / 6 : ℚ), 0, (1 / 3 : ℚ)]
]

theorem ramanujan12_length : ramanujan12.length = 12 := by decide +kernel

theorem projector12_shape :
    projector12.length = 12 ∧
    projector12.map List.length = List.replicate 12 12 := by
  decide +kernel

/-- The cyclic Ramanujan kernel is symmetric. -/
theorem projector12_symmetric : transposeN 12 projector12 = projector12 := by
  decide +kernel

/-- Exact finite projector identity P^2 = P. -/
theorem projector12_idempotent :
    matMulN 12 projector12 projector12 = projector12 := by
  decide +kernel

/-- The arithmetic signal lies in the selected subspace. -/
theorem projector12_fixes_ramanujan :
    matVec projector12 ramanujan12 = ramanujan12 := by
  decide +kernel

/-- The chosen constant-plus-frequency-3 perturbation lies in the complementary subspace. -/
theorem projector12_kills_noise :
    matVec projector12 noise12 = List.replicate 12 0 := by
  decide +kernel

/-- Therefore the exact filter recovers the arithmetic component. -/
theorem projector12_recovers_test_signal :
    matVec projector12 testSignal12 = ramanujan12 := by
  decide +kernel

/-- The arithmetic amplitude vector has squared norm 48. -/
theorem ramanujan12_energy : sqEnergy ramanujan12 = 48 := by
  decide +kernel

/-- The perturbation has squared norm 102. -/
theorem noise12_energy : sqEnergy noise12 = 102 := by
  decide +kernel

/-- The full signal has squared norm 150. -/
theorem testSignal12_energy : sqEnergy testSignal12 = 150 := by
  decide +kernel

/-- Exact orthogonal energy decomposition 150 = 48 + 102. -/
theorem energy_decomposition :
    sqEnergy testSignal12 = sqEnergy ramanujan12 + sqEnergy noise12 := by
  decide +kernel

/-! ## 2. Exact cyclotomic arithmetic for zeta_12 -/

/--
An exact coordinate model for Q(sqrt(3), i).  The tuple (a,b,c,d) denotes
  a + b*sqrt(3) + i*(c + d*sqrt(3)).
Only the concrete arithmetic needed for the q=12 certificate is used below;
we do not install a global field instance.
-/
structure Cyclo12 where
  a : ℚ
  b : ℚ
  c : ℚ
  d : ℚ
  deriving DecidableEq, Repr

def cZero : Cyclo12 := ⟨0, 0, 0, 0⟩
def cOne  : Cyclo12 := ⟨1, 0, 0, 0⟩
def cRat (r : ℚ) : Cyclo12 := ⟨r, 0, 0, 0⟩

def cAdd (x y : Cyclo12) : Cyclo12 :=
  ⟨x.a + y.a, x.b + y.b, x.c + y.c, x.d + y.d⟩

def cNeg (x : Cyclo12) : Cyclo12 :=
  ⟨-x.a, -x.b, -x.c, -x.d⟩

def cSub (x y : Cyclo12) : Cyclo12 := cAdd x (cNeg y)

/-- Multiplication in Q(sqrt(3), i). -/
def cMul (x y : Cyclo12) : Cyclo12 :=
  ⟨x.a*y.a + 3*x.b*y.b - x.c*y.c - 3*x.d*y.d,
   x.a*y.b + x.b*y.a - x.c*y.d - x.d*y.c,
   x.a*y.c + 3*x.b*y.d + x.c*y.a + 3*x.d*y.b,
   x.a*y.d + x.b*y.c + x.c*y.b + x.d*y.a⟩

def cConj (x : Cyclo12) : Cyclo12 := ⟨x.a, x.b, -x.c, -x.d⟩

def cPow (x : Cyclo12) : Nat → Cyclo12
  | 0 => cOne
  | n + 1 => cMul (cPow x n) x

def cSum : List Cyclo12 → Cyclo12
  | [] => cZero
  | x :: xs => cAdd x (cSum xs)

/-- zeta = exp(2*pi*i/12) = sqrt(3)/2 + i/2. -/
def zeta12 : Cyclo12 := ⟨0, (1/2 : ℚ), (1/2 : ℚ), 0⟩

def zeta12Inv : Cyclo12 := cConj zeta12

theorem zeta12_order_certificate : cPow zeta12 12 = cOne := by
  decide +kernel

theorem zeta12_inverse_certificate : cMul zeta12 zeta12Inv = cOne := by
  decide +kernel

/-- The four coprime residues modulo 12. -/
def unitResidues12 : List Nat := [1, 5, 7, 11]

def ramanujanC12 (n : Nat) : Cyclo12 :=
  cSum (unitResidues12.map (fun a => cPow zeta12 (a*n)))

/-- Exact Ramanujan-sum table obtained from the four primitive phases. -/
theorem ramanujanC12_table :
    (List.range 12).map ramanujanC12 =
      [cRat 4, cRat 0, cRat 2, cRat 0, cRat (-2), cRat 0,
       cRat (-4), cRat 0, cRat (-2), cRat 0, cRat 2, cRat 0] := by
  decide +kernel

/-- Minus-sign DFT over one period, using zeta^(-k*n). -/
def dft12 (x : List Cyclo12) (k : Nat) : Cyclo12 :=
  cSum ((List.range 12).map (fun n =>
    cMul (x.getD n cZero) (cPow zeta12Inv (k*n))))

def ramanujanCVector : List Cyclo12 :=
  (List.range 12).map ramanujanC12

/-- The DFT is supported exactly on 1,5,7,11, with value 12 there. -/
theorem ramanujan_dft_table :
    (List.range 12).map (dft12 ramanujanCVector) =
      [cRat 0, cRat 12, cRat 0, cRat 0, cRat 0, cRat 12,
       cRat 0, cRat 12, cRat 0, cRat 0, cRat 0, cRat 12] := by
  decide +kernel

/-- Absolute-value version of the Ramanujan signal. -/
def absRamanujanCVector : List Cyclo12 :=
  [cRat 4, cRat 0, cRat 2, cRat 0, cRat 2, cRat 0,
   cRat 4, cRat 0, cRat 2, cRat 0, cRat 2, cRat 0]

/-- Removing the signs destroys every coprime Fourier mode. -/
theorem abs_ramanujan_dft_table :
    (List.range 12).map (dft12 absRamanujanCVector) =
      [cRat 16, cRat 0, cRat 4, cRat 0, cRat 4, cRat 0,
       cRat 16, cRat 0, cRat 4, cRat 0, cRat 4, cRat 0] := by
  decide +kernel

/-! ## 3. Quantum probability consequences -/

/-- Squared amplitudes are unchanged by stripping the signs of c_12(n). -/
def absRamanujan12 : QVector :=
  [4, 0, 2, 0, 2, 0, 4, 0, 2, 0, 2, 0]

def sqEntries (x : QVector) : QVector := x.map (fun t => t*t)

theorem same_computational_basis_probabilities :
    sqEntries ramanujan12 = sqEntries absRamanujan12 := by
  decide +kernel

theorem abs_ramanujan12_energy : sqEnergy absRamanujan12 = 48 := by
  decide +kernel

/--
For |psi> = (1/sqrt(48)) sum_n c_12(n)|n>, the unitary inverse DFT contributes
an additional factor 1/sqrt(12).  A recovered Fourier coefficient 12 therefore
has probability 12^2/(48*12) = 1/4.
-/
theorem recovered_mode_probability :
    ((12 : ℚ)^2) / (48 * 12) = 1/4 := by
  norm_num

/-- Four recovered coprime modes exhaust total probability. -/
theorem recovered_total_probability :
    4 * (((12 : ℚ)^2) / (48 * 12)) = 1 := by
  norm_num

/-- The absolute-value state has zero probability on each of the four coprime modes. -/
theorem phase_stripping_coprime_probability :
    4 * (((0 : ℚ)^2) / (48 * 12)) = 0 := by
  norm_num

/-- The publication's central finite bridge, bundled as one exact proposition. -/
theorem arithmetic_signal_quantum_bridge :
    matMulN 12 projector12 projector12 = projector12 ∧
    matVec projector12 testSignal12 = ramanujan12 ∧
    (List.range 12).map (dft12 ramanujanCVector) =
      [cRat 0, cRat 12, cRat 0, cRat 0, cRat 0, cRat 12,
       cRat 0, cRat 12, cRat 0, cRat 0, cRat 0, cRat 12] ∧
    sqEntries ramanujan12 = sqEntries absRamanujan12 := by
  exact ⟨projector12_idempotent, projector12_recovers_test_signal,
    ramanujan_dft_table, same_computational_basis_probabilities⟩

end Komorebi.QuantumArithmetic
