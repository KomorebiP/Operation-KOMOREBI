import AVOC.AffineSearchGuard
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic

namespace Komorebi.AVOC.Affine.RankProbe

open Factorization SearchGuard
variable {R : Type} [Field R] {n m : Nat}

/-- A nonzero k-by-k minor is only a lower-rank certificate, not a factorization. -/
theorem nonzero_minor_rank_lower (A : Matrix (Fin m) (Fin n) R) (k : Nat)
    (rows : Fin k → Fin m) (cols : Fin k → Fin n)
    (h : (A.submatrix rows cols).det ≠ 0) : k ≤ A.rank := by
  have he := Matrix.rank_of_det_ne_zero h
  have hl := Matrix.rank_submatrix_le A rows cols
  rw [he, Fintype.card_fin] at hl
  exact hl

structure MinorTwo (m n : Nat) where
  row0 : Fin m
  row1 : Fin m
  col0 : Fin n
  col1 : Fin n
  deriving Repr, DecidableEq

def determinant2 (A : Matrix (Fin m) (Fin n) R) (p : MinorTwo m n) : R :=
  A p.row0 p.col0 * A p.row1 p.col1 - A p.row0 p.col1 * A p.row1 p.col0

def check2 [DecidableEq R] (A : Matrix (Fin m) (Fin n) R) (p : MinorTwo m n) : Bool :=
  decide (determinant2 A p ≠ 0)

theorem check2_iff [DecidableEq R] (A : Matrix (Fin m) (Fin n) R) (p : MinorTwo m n) :
    check2 A p = true ↔ determinant2 A p ≠ 0 := by simp [check2]

theorem check2_rank_lower [DecidableEq R] (A : Matrix (Fin m) (Fin n) R)
    (p : MinorTwo m n) (h : check2 A p = true) : 2 ≤ A.rank := by
  apply nonzero_minor_rank_lower A 2 ![p.row0,p.row1] ![p.col0,p.col1]
  simpa [Matrix.det_fin_two, Matrix.submatrix, determinant2] using (check2_iff A p).1 h

theorem repeated_row_rejected [DecidableEq R] (A : Matrix (Fin m) (Fin n) R)
    (p : MinorTwo m n) (h : p.row0 = p.row1) : check2 A p = false := by
  simp [check2, determinant2, h, mul_comm]

theorem repeated_column_rejected [DecidableEq R] (A : Matrix (Fin m) (Fin n) R)
    (p : MinorTwo m n) (h : p.col0 = p.col1) : check2 A p = false := by
  simp [check2, determinant2, h]

theorem widthFloor_rank [DecidableEq R] (f : Signature R n m) : widthFloor f ≤ f.linear.rank := by
  unfold widthFloor
  split
  · exact Nat.zero_le _
  next h =>
    classical
    have he : ∃ i j, f.linear i j ≠ 0 := by
      by_contra hn
      apply h
      ext i j
      by_contra hij
      exact hn ⟨i,j,hij⟩
    obtain ⟨i,j,hij⟩ := he
    apply nonzero_minor_rank_lower f.linear 1 (fun _ => i) (fun _ => j)
    simpa [Matrix.det_fin_one, Matrix.submatrix] using hij

theorem checked_minor_bounds_every_factor [DecidableEq R] (f : Signature R n m)
    (p : MinorTwo m n) (h : check2 f.linear p = true)
    {k : Nat} (a : Signature R n k) (b : Signature R k m) (he : compose b a = f) : 2 ≤ k := by
  have hlow := check2_rank_lower f.linear p h
  have hup := any_factor_rank_upper a b
  rw [he] at hup
  exact hlow.trans hup

theorem checked_minor_bounds_certificate [DecidableEq R] (f : Signature R n m)
    (p : MinorTwo m n) (h : check2 f.linear p = true) (c : Checked f) : 2 ≤ c.candidate.width := by
  have hl := check2_rank_lower f.linear p h
  rw [valid_rank_exact c.certified] at hl
  exact hl

/-- Only the linear map is probed. Changed affine offsets need no new minor calculation. -/
theorem check2_offset_invariant [DecidableEq R] (f g : Signature R n m)
    (h : f.linear = g.linear) (p : MinorTwo m n) : check2 f.linear p = check2 g.linear p := by rw [h]

end Komorebi.AVOC.Affine.RankProbe
