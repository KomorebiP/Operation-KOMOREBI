import Mathlib

/-!
# Endpoint Krylov bases for path graphs

For the path with vertices `0, ..., n`, let `A` be its adjacency operator and
let `e₀` be the endpoint vector.  This file proves that the walk matrix whose
`k`th column is `A ^ k e₀` is upper triangular with diagonal equal to one.
Consequently its determinant is one over every commutative ring, the first
`n + 1` Krylov vectors span, and `e₀` is a cyclic vector for `A`.

Writing the number of vertices as `n + 1` makes the endpoint available without
an extra nonemptiness hypothesis; thus the result covers every nonempty finite
path, including the one-vertex path.
-/

set_option autoImplicit false

namespace Komorebi.PathGraphKrylov

universe u

variable (R : Type u) [CommSemiring R]
variable (n : ℕ)

/-- The contribution from the neighbor immediately to the left, when it exists. -/
def leftTerm (x : Fin (n + 1) → R) (i : Fin (n + 1)) : R :=
  if _h : i = 0 then
    0
  else
    x ⟨i.val - 1, lt_of_le_of_lt (Nat.sub_le i.val 1) i.isLt⟩

/-- The contribution from the neighbor immediately to the right, when it exists. -/
def rightTerm (x : Fin (n + 1) → R) (i : Fin (n + 1)) : R :=
  if h : i.val < n then x ⟨i.val + 1, Nat.succ_lt_succ h⟩ else 0

/-- The shift which reads the neighbor immediately to the left. -/
def leftStep : Module.End R (Fin (n + 1) → R) :=
  LinearMap.pi fun i ↦
    if _h : i = 0 then
      0
    else
      LinearMap.proj ⟨i.val - 1, lt_of_le_of_lt (Nat.sub_le i.val 1) i.isLt⟩

/-- The shift which reads the neighbor immediately to the right. -/
def rightStep : Module.End R (Fin (n + 1) → R) :=
  LinearMap.pi fun i ↦
    if h : i.val < n then LinearMap.proj ⟨i.val + 1, Nat.succ_lt_succ h⟩ else 0

/-- The adjacency operator of the path `0 - 1 - ... - n`. -/
def pathStep : Module.End R (Fin (n + 1) → R) :=
  leftStep R n + rightStep R n

@[simp]
theorem pathStep_apply (x : Fin (n + 1) → R) (i : Fin (n + 1)) :
    pathStep R n x i = leftTerm R n x i + rightTerm R n x i :=
  by
    by_cases hLeft : i = 0
    · subst i
      by_cases hn : 0 < n <;>
        simp [pathStep, leftStep, rightStep, leftTerm, rightTerm, hn]
    · by_cases hRight : i.val < n <;>
        simp [pathStep, leftStep, rightStep, leftTerm, rightTerm, hLeft, hRight]

/-- The standard basis vector at the left endpoint. -/
def endpoint : Fin (n + 1) → R :=
  fun i ↦ if i.val = 0 then 1 else 0

/-- The recursively presented Krylov sequence `e₀, A e₀, A² e₀, ...`. -/
def krylov : ℕ → Fin (n + 1) → R
  | 0 => endpoint R n
  | k + 1 => pathStep R n (krylov k)

@[simp]
theorem krylov_zero : krylov R n 0 = endpoint R n :=
  rfl

@[simp]
theorem krylov_succ (k : ℕ) :
    krylov R n (k + 1) = pathStep R n (krylov R n k) :=
  rfl

/-- The recursive Krylov sequence really is given by powers of the adjacency operator. -/
theorem krylov_eq_pow (k : ℕ) :
    krylov R n k = ((pathStep R n) ^ k) (endpoint R n) := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [krylov_succ, pow_succ', Module.End.mul_apply, ih]

/-- A walk of length `k` from `0` cannot reach a vertex strictly beyond `k`. -/
theorem krylov_apply_eq_zero_of_lt (k : ℕ) (i : Fin (n + 1))
    (hki : k < i.val) : krylov R n k i = 0 := by
  induction k generalizing i with
  | zero =>
      simp only [krylov_zero, endpoint]
      simp [Nat.ne_of_gt hki]
  | succ k ih =>
      rw [krylov_succ, pathStep_apply]
      have hi : 0 < i.val := by omega
      have hi0 : i ≠ 0 := Fin.ne_of_val_ne (by simpa using Nat.ne_of_gt hi)
      let iLeft : Fin (n + 1) :=
        ⟨i.val - 1, lt_of_le_of_lt (Nat.sub_le i.val 1) i.isLt⟩
      have hLeft : k < iLeft.val := by
        dsimp [iLeft]
        omega
      have hzLeft : krylov R n k iLeft = 0 := ih iLeft hLeft
      by_cases hRight : i.val < n
      · let iRight : Fin (n + 1) := ⟨i.val + 1, Nat.succ_lt_succ hRight⟩
        have hRight' : k < iRight.val := by
          dsimp [iRight]
          omega
        have hzRight : krylov R n k iRight = 0 := ih iRight hRight'
        simp only [leftTerm, rightTerm, hi0, hRight, dite_true, dite_false,
          iLeft, iRight, hzLeft, hzRight, add_zero]
      · simp only [leftTerm, rightTerm, hi0, hRight, dite_false,
          iLeft, hzLeft, add_zero]

/-- There is exactly one length-`k` walk from `0` to vertex `k`. -/
theorem krylov_diagonal (k : ℕ) (hk : k < n + 1) :
    krylov R n k ⟨k, hk⟩ = 1 := by
  induction k with
  | zero => simp [krylov_zero, endpoint]
  | succ k ih =>
      rw [krylov_succ, pathStep_apply]
      have hk' : k < n + 1 := by omega
      have hne : (⟨k + 1, hk⟩ : Fin (n + 1)) ≠ 0 :=
        Fin.ne_of_val_ne (by simp)
      by_cases hRight : k + 1 < n
      · let iRight : Fin (n + 1) :=
          ⟨(k + 1) + 1, Nat.succ_lt_succ hRight⟩
        have hlt : k < iRight.val := by
          dsimp [iRight]
          omega
        have hzRight : krylov R n k iRight = 0 :=
          krylov_apply_eq_zero_of_lt R n k iRight hlt
        simp only [leftTerm, rightTerm, hne, hRight, dite_true, dite_false,
          Nat.add_sub_cancel, ih hk', iRight, hzRight, add_zero]
      · simp only [leftTerm, rightTerm, hne, hRight, dite_false,
          Nat.add_sub_cancel, ih hk', add_zero]

/-- The matrix of the path adjacency operator in the standard coordinate basis. -/
noncomputable def pathAdjacency : Matrix (Fin (n + 1)) (Fin (n + 1)) R :=
  LinearMap.toMatrix (Pi.basisFun R (Fin (n + 1)))
    (Pi.basisFun R (Fin (n + 1))) (pathStep R n)

/-- Matrix multiplication by `pathAdjacency` is exactly `pathStep`. -/
theorem pathAdjacency_mulVec (x : Fin (n + 1) → R) :
    (pathAdjacency R n).mulVec x = pathStep R n x := by
  have h := LinearMap.congr_fun
    (Matrix.toLin_toMatrix (Pi.basisFun R (Fin (n + 1)))
      (Pi.basisFun R (Fin (n + 1))) (pathStep R n)) x
  simpa only [pathAdjacency, Matrix.toLin_eq_toLin', Matrix.toLin'_apply] using h

/-- Matrix powers of the adjacency matrix give the same Krylov vectors. -/
theorem pathAdjacency_pow_mulVec_endpoint (k : ℕ) :
    ((pathAdjacency R n) ^ k).mulVec (endpoint R n) = krylov R n k := by
  induction k with
  | zero => simp [krylov_zero]
  | succ k ih =>
      rw [pow_succ', ← Matrix.mulVec_mulVec, ih, pathAdjacency_mulVec,
        ← krylov_succ]

/-- The walk matrix: column `k` is `A ^ k e₀`. -/
noncomputable def walkMatrix : Matrix (Fin (n + 1)) (Fin (n + 1)) R :=
  fun i k ↦ ((pathAdjacency R n) ^ k.val).mulVec (endpoint R n) i

theorem walkMatrix_apply (i k : Fin (n + 1)) :
    walkMatrix R n i k = krylov R n k.val i := by
  rw [walkMatrix, pathAdjacency_pow_mulVec_endpoint]

/-- Entries below the diagonal of the walk matrix vanish. -/
theorem walkMatrix_apply_eq_zero_of_lt (i k : Fin (n + 1)) (hki : k < i) :
    walkMatrix R n i k = 0 := by
  rw [walkMatrix_apply]
  exact krylov_apply_eq_zero_of_lt R n k.val i hki

/-- Every diagonal entry of the walk matrix is one. -/
@[simp]
theorem walkMatrix_diagonal (i : Fin (n + 1)) :
    walkMatrix R n i i = 1 := by
  rw [walkMatrix_apply]
  exact krylov_diagonal R n i.val i.isLt

/-- The endpoint walk matrix is upper triangular. -/
theorem walkMatrix_isUpperTriangular :
    (walkMatrix R n).IsUpperTriangular := by
  intro i k hki
  exact walkMatrix_apply_eq_zero_of_lt R n i k hki

section CommRing

variable {R : Type u} [CommRing R]

/-- The endpoint walk matrix is unitriangular, hence has determinant one. -/
@[simp]
theorem walkMatrix_det : (walkMatrix R n).det = 1 := by
  rw [Matrix.det_of_isUpperTriangular (walkMatrix_isUpperTriangular R n)]
  simp

/-- The finite endpoint Krylov family spans the whole coordinate module. -/
theorem krylov_span_eq_top :
    Submodule.span R (Set.range fun k : Fin (n + 1) ↦ krylov R n k.val) = ⊤ := by
  have hdet : IsUnit (walkMatrix R n).det := by
    rw [walkMatrix_det]
    exact isUnit_one
  have hrange : LinearMap.range (Matrix.toLin' (walkMatrix R n)) = ⊤ := by
    rw [← Matrix.toLin_eq_toLin']
    exact Matrix.range_toLin_eq_top (Pi.basisFun R (Fin (n + 1)))
      (walkMatrix R n) hdet
  rw [Matrix.range_toLin'] at hrange
  have hcol : (walkMatrix R n).col =
      (fun k : Fin (n + 1) ↦ krylov R n k.val) := by
    funext k i
    exact walkMatrix_apply R n i k
  rwa [hcol] at hrange

/-- A vector is cyclic for an operator when the span of all of its iterates is the top module. -/
def IsCyclic (T : Module.End R (Fin (n + 1) → R))
    (x : Fin (n + 1) → R) : Prop :=
  Submodule.span R (Set.range fun k : ℕ ↦ (T ^ k) x) = ⊤

/-- The left endpoint is cyclic for the path adjacency operator. -/
theorem endpoint_isCyclic :
    IsCyclic (R := R) n (pathStep R n) (endpoint R n) := by
  rw [IsCyclic]
  apply le_antisymm le_top
  rw [← krylov_span_eq_top (R := R) n]
  apply Submodule.span_mono
  rintro _ ⟨k, rfl⟩
  refine ⟨k.val, ?_⟩
  exact (krylov_eq_pow R n k.val).symm

end CommRing

end Komorebi.PathGraphKrylov

#print axioms Komorebi.PathGraphKrylov.endpoint_isCyclic
