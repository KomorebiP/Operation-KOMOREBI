import PaperX.IdempotentNewton
import PaperX.MatrixWitnessLimits
import Mathlib.LinearAlgebra.Matrix.Ideal

/-! Idempotents in a complete matrix algebra lift by polynomial correction.
The construction preserves every matrix commuting with the original approximation.
No exact idempotent or compatible family is supplied as a premise. -/
set_option autoImplicit false

namespace PaperX.AdicIdempotent
open PaperX.RepresentationLimits PaperX.MatrixWitnessLimits
open PaperX.IdempotentNewton

variable {R : Type*} [CommRing R]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem matrix_map_pow {S : Type*} [CommRing S] (f : R →+* S)
    (A : Matrix ι ι R) (n : ℕ) : (A^n).map f = (A.map f)^n :=
  map_pow f.mapMatrix A n

theorem matrix_map_sub {S : Type*} [CommRing S] (f : R →+* S)
    (A B : Matrix ι ι R) : (A-B).map f = A.map f - B.map f :=
  map_sub f.mapMatrix A B

/-- Entrywise reduction detects membership in the matrix ideal. -/
theorem map_eq_zero_iff (I : Ideal R) (A : Matrix ι ι R) :
    A.map (Ideal.Quotient.mk I) = 0 ↔ A ∈ I.matrix ι := by
  constructor
  · intro h i j
    apply Ideal.Quotient.eq_zero_iff_mem.mp
    exact congrArg (fun M => M i j) h
  · intro h
    ext i j
    exact Ideal.Quotient.eq_zero_iff_mem.mpr (h i j)

/-- Entrywise ideal products contain matrix products. -/
theorem matrix_mul_mem (I J : Ideal R) {A B : Matrix ι ι R}
    (hA : A ∈ I.matrix ι) (hB : B ∈ J.matrix ι) :
    A * B ∈ (I * J).matrix ι := by
  intro i j
  rw [Matrix.mul_apply]
  exact Ideal.sum_mem _ fun l _ => Ideal.mul_mem_mul (hA i l) (hB l j)

/-- Multiplication on either side preserves entrywise ideal membership. -/
theorem matrix_mul_right_mem (I : Ideal R) {A : Matrix ι ι R}
    (hA : A ∈ I.matrix ι) (B : Matrix ι ι R) : A * B ∈ I.matrix ι := by
  intro i j
  rw [Matrix.mul_apply]
  exact Ideal.sum_mem _ fun l _ => I.mul_mem_right _ (hA i l)

/-- The polynomial iteration, started at an approximate idempotent. -/
def iterate (A : Matrix ι ι R) : ℕ → Matrix ι ι R
  | 0 => A
  | n+1 => correct (iterate A n)

@[simp] theorem iterate_zero (A : Matrix ι ι R) : iterate A 0 = A := rfl
@[simp] theorem iterate_succ (A : Matrix ι ι R) (n : ℕ) :
    iterate A (n+1) = correct (iterate A n) := rfl

/-- One correction at least adds one ideal digit when the starting depth is positive. -/
theorem iterate_error_mem (I : Ideal R) (k : ℕ) (hk : 0 < k)
    (A : Matrix ι ι R) (hA : A^2 - A ∈ (I^k).matrix ι) (n : ℕ) :
    (iterate A n)^2 - iterate A n ∈ (I^(n+k)).matrix ι := by
  induction n with
  | zero => simpa using hA
  | succ n ih =>
    rw [iterate_succ, correct_error]
    have hsq : ((iterate A n)^2 - iterate A n)^2 ∈
        (I^((n+k)+(n+k))).matrix ι := by
      rw [pow_two, pow_add]
      exact matrix_mul_mem _ _ ih ih
    exact Ideal.matrix_monotone ι
      (Ideal.pow_le_pow_right (by omega : n+1+k ≤ (n+k)+(n+k)))
      (matrix_mul_right_mem _ hsq _)

/-- Each correction has the same precision as the preceding defect. -/
theorem iterate_step_mem (I : Ideal R) (k : ℕ) (hk : 0 < k)
    (A : Matrix ι ι R) (hA : A^2 - A ∈ (I^k).matrix ι) (n : ℕ) :
    iterate A (n+1) - iterate A n ∈ (I^(n+k)).matrix ι := by
  rw [iterate_succ, correct_sub]
  exact (I^(n+k)).matrix ι |>.mul_mem_left _ (iterate_error_mem I k hk A hA n)

/-- Every iterate retains the initial prescribed reduction. -/
theorem iterate_reduces (I : Ideal R) (k : ℕ) (hk : 0 < k)
    (A : Matrix ι ι R) (hA : A^2 - A ∈ (I^k).matrix ι) (n : ℕ) :
    (iterate A n).map (Ideal.Quotient.mk (I^k)) = A.map (Ideal.Quotient.mk (I^k)) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    have hmem := Ideal.matrix_monotone ι
      (Ideal.pow_le_pow_right (Nat.le_add_left k n)) (iterate_step_mem I k hk A hA n)
    have H := (map_eq_zero_iff (I^k) _).mpr hmem
    rw [matrix_map_sub] at H
    exact (sub_eq_zero.mp H).trans ih

/-- Polynomial iterates commute with any matrix commuting with the input. -/
theorem iterate_commutes (A C : Matrix ι ι R) (h : C*A=A*C) (n : ℕ) :
    C * iterate A n = iterate A n * C := by
  induction n with
  | zero => exact h
  | succ n ih => exact (correct_intertwines (iterate A n) (iterate A n) C ih.symm).symm

/-- The corrected finite matrices form a coherent family without supplied choices. -/
def family (I : Ideal R) (k : ℕ) (hk : 0 < k)
    (A : Matrix ι ι R) (hA : A^2 - A ∈ (I^k).matrix ι) : MatrixFamily R I ι :=
  matrix_family_of_succ I (fun n => (iterate A n).map (Ideal.Quotient.mk (I^n))) (by
    intro n
    have hmem := Ideal.matrix_monotone ι
      (Ideal.pow_le_pow_right (Nat.le_add_right n k)) (iterate_step_mem I k hk A hA n)
    have H := (map_eq_zero_iff (I^n) _).mpr hmem
    rw [matrix_map_sub] at H
    have heq := sub_eq_zero.mp H
    ext i j
    simpa using congrArg (fun M => M i j) heq)

/-- Actual idempotent correction in the complete matrix algebra, retaining any
positive starting precision and every existing commutation relation. -/
theorem correct_commuting (I : Ideal R) [IsAdicComplete I R]
    (k : ℕ) (hk : 0 < k) (A : Matrix ι ι R)
    (hA : (A.map (Ideal.Quotient.mk (I^k)))^2 = A.map (Ideal.Quotient.mk (I^k))) :
    ∃ E : Matrix ι ι R, E^2 = E ∧
      E.map (Ideal.Quotient.mk (I^k)) = A.map (Ideal.Quotient.mk (I^k)) ∧
      ∀ C : Matrix ι ι R, C*A=A*C → C*E=E*C := by
  have hmem : A^2 - A ∈ (I^k).matrix ι := by
    apply (map_eq_zero_iff (I^k) _).mp
    simp only [matrix_map_sub, matrix_map_pow, hA, sub_self]
  let F := family I k hk A hmem
  let E := reconstructMatrix I F
  have hE (n : ℕ) : E.map (Ideal.Quotient.mk (I^n)) =
      (iterate A n).map (Ideal.Quotient.mk (I^n)) := reconstructMatrix_reduces I F n
  refine ⟨E, ?_, ?_, ?_⟩
  · apply matrix_ext I
    intro n
    have hd := Ideal.matrix_monotone ι
      (Ideal.pow_le_pow_right (Nat.le_add_right n k)) (iterate_error_mem I k hk A hmem n)
    have H := (map_eq_zero_iff (I^n) _).mpr hd
    rw [matrix_map_sub] at H
    have hpow : (E^2).map (Ideal.Quotient.mk (I^n)) =
        (E.map (Ideal.Quotient.mk (I^n)))^2 := by
      exact map_pow (Ideal.Quotient.mk (I^n)).mapMatrix E 2
    rw [hpow, hE]
    simpa only [matrix_map_pow] using sub_eq_zero.mp H
  · exact (hE k).trans (iterate_reduces I k hk A hmem k)
  · intro C hC
    apply matrix_ext I
    intro n
    simp only [Matrix.map_mul, hE]
    simpa only [Matrix.map_mul] using congrArg (fun M => M.map (Ideal.Quotient.mk (I^n)))
      (iterate_commutes A C hC n)

end PaperX.AdicIdempotent
