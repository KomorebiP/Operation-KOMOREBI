import Mathlib

/-!
# Web-checkable core of the infinite Fermat Hodge-packet construction

This file formalizes the finite arithmetic, matrix, conductor, and
implication-chain parts of the construction.

There is no `sorry` and no `axiom` in this file.
The deep algebraic-geometric facts enter only as explicit hypotheses in the
final abstract theorem.
-/

namespace HodgeInfiniteClass

/-! ## 1. The degree-33 seed and its complete unit-orbit balance -/

def seed33 : List Nat := [7, 19, 28, 10, 13, 22]

def units33 : List Nat :=
  (List.range 33).filter (fun u => Nat.gcd u 33 == 1)

def residueSum33 (u : Nat) : Nat :=
  (seed33.map (fun a => (u * a) % 33)).sum

/-- The complete list of units modulo 33. -/
theorem units33_exact :
    units33 = [1, 2, 4, 5, 7, 8, 10, 13, 14, 16,
               17, 19, 20, 23, 25, 26, 28, 29, 31, 32] := by
  native_decide

/-- Every unit translate of the seed has residue sum 99 = 3·33. -/
theorem seed33_complete_hodge_balance :
    units33.map residueSum33 = List.replicate 20 99 := by
  native_decide

/-- The seed itself has the expected middle-Hodge sum. -/
theorem seed33_sum : seed33.sum = 99 := by
  native_decide

/-! ## 2. Coordinate-power scaling and Tate-pair promotion -/

def scalePacket (k : Nat) (a : List Nat) : List Nat :=
  a.map (fun x => k * x)

def towerDegree (k : Nat) : Nat := 33 * k

def promotedPacket (k : Nat) : List Nat :=
  scalePacket k seed33 ++ [1, towerDegree k - 1]

/-- Residue exponents transform by `k(b-1)+(k-1)=kb-1`. -/
theorem residue_exponent_scaling
    (k b : Nat) (hk : 0 < k) (hb : 0 < b) :
    k * (b - 1) + (k - 1) = k * b - 1 := by
  cases k with
  | zero => simp at hk
  | succ k =>
      cases b with
      | zero => simp at hb
      | succ b =>
          simp [Nat.mul_succ, Nat.succ_mul]

/-- The six scaled seed entries sum to 99k. -/
theorem scaled_seed_sum (k : Nat) :
    7*k + 19*k + 28*k + 10*k + 13*k + 22*k = 99*k := by
  ring

/-- The appended complementary pair contributes exactly 33k. -/
theorem tate_pair_sum (k : Nat) (hk : 0 < k) :
    1 + (33*k - 1) = 33*k := by
  omega

/-- The promoted eight-packet has middle-Hodge sum 4·(33k). -/
theorem promoted_packet_sum (k : Nat) (hk : 0 < k) :
    7*k + 19*k + 28*k + 10*k + 13*k + 22*k
      + 1 + (33*k - 1) = 4 * (33*k) := by
  omega

/-- The same statement in the actual list representation. -/
theorem promotedPacket_sum (k : Nat) (hk : 0 < k) :
    (promotedPacket k).sum = 4 * towerDegree k := by
  simp [promotedPacket, scalePacket, seed33, towerDegree]
  omega

/-- The raw conductor gcd is one because the packet contains a coordinate 1. -/
def promotedConductorGcd (k : Nat) : Nat :=
  Nat.gcd (33*k)
    (Nat.gcd (7*k)
      (Nat.gcd (19*k)
        (Nat.gcd (28*k)
          (Nat.gcd (10*k)
            (Nat.gcd (13*k)
              (Nat.gcd (22*k)
                (Nat.gcd 1 (33*k - 1))))))))

theorem promoted_full_conductor (k : Nat) :
    promotedConductorGcd k = 1 := by
  simp [promotedConductorGcd]

/-- A coordinate equal to 1 forces a residue-class stabilizer to be trivial. -/
theorem coordinate_one_trivializes_stabilizer
    {m u : Nat} (hu : u < m) (h : u % m = 1) : u = 1 := by
  simpa [Nat.mod_eq_of_lt hu] using h

/-- Coordinate-power map degrees compose multiplicatively. -/
theorem power_map_degree_composition (r s : Nat) :
    (r * s)^5 = r^5 * s^5 := by
  ring

/-- The numerical Klein projective-torus degree. -/
theorem klein_torus_degree : 33^4 = 1185921 := by
  norm_num

/-! ## 3. Exact finite Klein matrix certificates -/

abbrev IMatrix := List (List Int)
abbrev IVector := List Int

def dot (x y : IVector) : Int :=
  (List.zipWith (fun a b => a * b) x y).sum

/--
Transpose the first `n` columns of a list matrix.  Entries outside a short row
are defined to be zero, but all concrete matrices below are rectangular 6×6.
`List.getD` is used because current Lean/Mathlib no longer exposes `List.get!`.
-/
def transposeN (n : Nat) (M : IMatrix) : IMatrix :=
  (List.range n).map (fun j => M.map (fun row => row.getD j 0))

def matMulN (n : Nat) (A B : IMatrix) : IMatrix :=
  A.map (fun row => (transposeN n B).map (fun col => dot row col))

def matVecN (M : IMatrix) (v : IVector) : IVector :=
  M.map (fun row => dot row v)

def vecAdd (x y : IVector) : IVector :=
  List.zipWith (fun a b => a + b) x y

def vecScale (a : Int) (x : IVector) : IVector :=
  x.map (fun t => a * t)

def kleinA : IMatrix :=
  [[2,0,0,0,1,0],
   [1,2,0,0,0,0],
   [0,1,2,0,0,0],
   [0,0,1,2,0,0],
   [0,0,0,1,2,0],
   [0,0,0,0,0,3]]

def kleinC : IMatrix :=
  [[16,1,-2,4,-8,0],
   [-8,16,1,-2,4,0],
   [4,-8,16,1,-2,0],
   [-2,4,-8,16,1,0],
   [1,-2,4,-8,16,0],
   [0,0,0,0,0,11]]

def diag33 : IMatrix :=
  [[33,0,0,0,0,0],
   [0,33,0,0,0,0],
   [0,0,33,0,0,0],
   [0,0,0,33,0,0],
   [0,0,0,0,33,0],
   [0,0,0,0,0,33]]

/-- Exact exponent-matrix certificate `A*C = 33 I`. -/
theorem klein_matrix_identity :
    matMulN 6 kleinA kleinC = diag33 := by
  native_decide

/-- Every row of C sums to 11. -/
theorem kleinC_row_sums :
    kleinC.map List.sum = List.replicate 6 11 := by
  native_decide

/-- Every column of C sums to 11. -/
theorem kleinC_column_sums :
    (transposeN 6 kleinC).map List.sum = List.replicate 6 11 := by
  native_decide


def cubicMonomialExponent : IVector := [0,1,1,0,0,1]
def ones6 : IVector := [1,1,1,1,1,1]
def fermatTargetExponent : IVector := [6,18,27,9,12,21]

/-- Exact residue-pullback exponent certificate. -/
theorem residue_pullback_exponent_identity :
    vecAdd
      (matVecN (transposeN 6 kleinC) cubicMonomialExponent)
      (vecScale 10 ones6)
      = fermatTargetExponent := by
  native_decide

/-! ## 4. What Lean can prove conditionally about algebraicity -/

/-
`AlgPacket m a` is intentionally abstract here.  In the geometric project it
means that the rational Galois packet indexed by `a` on the degree-`m` Fermat
variety is represented by rational algebraic cycles.
-/
section AbstractAlgebraicity

variable {AlgPacket : Nat → List Nat → Prop}

/--
This is the formally checked implication chain behind the infinite
full-conductor promoted class.  The two deep geometric closure properties are
explicit theorem arguments rather than hidden assumptions.
-/
theorem infinite_promoted_class
    (pullbackAlg :
      ∀ {d k : Nat} {a : List Nat},
        AlgPacket d a → AlgPacket (d*k) (scalePacket k a))
    (tateJoinAlg :
      ∀ {m : Nat} {a : List Nat},
        AlgPacket m a → AlgPacket m (a ++ [1, m-1]))
    (hSeed : AlgPacket 33 seed33) (k : Nat) :
    AlgPacket (33*k) (promotedPacket k) := by
  have hScaled : AlgPacket (33*k) (scalePacket k seed33) :=
    pullbackAlg (d := 33) (k := k) (a := seed33) hSeed
  simpa [promotedPacket, towerDegree] using
    tateJoinAlg (m := 33*k) (a := scalePacket k seed33) hScaled

end AbstractAlgebraicity

/-! ## 5. Visible evaluations in Lean Web -/

#eval units33
#eval units33.map residueSum33
#eval promotedPacket 5
#eval promotedConductorGcd 5
#eval matMulN 6 kleinA kleinC
#eval vecAdd
  (matVecN (transposeN 6 kleinC) cubicMonomialExponent)
  (vecScale 10 ones6)

end HodgeInfiniteClass
