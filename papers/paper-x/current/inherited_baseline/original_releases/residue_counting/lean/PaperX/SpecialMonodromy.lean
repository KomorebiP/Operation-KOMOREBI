import PaperX.MonodromyKernels
import Mathlib.Tactic.Ring

/-! Exact version of Komorebi's special monodromy chain.
Coordinates are 0,...,n-1; N e_j=e_(j-1), and F e_j=a q^(-j)e_j.
The length-zero case is included as a zero-dimensional space. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SpecialMonodromy
open scoped BigOperators Matrix
open Polynomial
open PaperX.MonodromyData

variable {K : Type*} [Field K]

def shift (n : ℕ) : Module.End K (Fin n → K) where
  toFun x i := if h : i.val + 1 < n then x ⟨i.val + 1, h⟩ else 0
  map_add' := by intro x y; funext i; dsimp; split <;> simp
  map_smul' := by intro a x; funext i; dsimp; split <;> simp

@[simp] theorem shift_apply (n : ℕ) (x : Fin n → K) (i : Fin n) :
    shift n x i = if h : i.val + 1 < n then x ⟨i.val + 1, h⟩ else 0 := rfl

theorem shift_pow_apply (n k : ℕ) (x : Fin n → K) (i : Fin n) :
    (shift n ^ k) x i = if h : i.val + k < n then x ⟨i.val + k, h⟩ else 0 := by
  induction k generalizing x i with
  | zero => simp [i.isLt]
  | succ k ih =>
      rw [pow_succ', Module.End.mul_apply, shift_apply]
      by_cases h : i.val + 1 < n
      · rw [dite_eq_left h, ih]
        by_cases h' : i.val + (k + 1) < n
        · have hh : (i.val + 1) + k < n := by omega
          rw [dite_eq_left hh, dite_eq_left h']
          congr 1
          apply Fin.ext
          dsimp
          omega
        · have hh : ¬ (i.val + 1) + k < n := by omega
          rw [dite_eq_right hh, dite_eq_right h']
      · have h' : ¬ i.val + (k + 1) < n := by omega
        rw [dite_eq_right h, dite_eq_right h']

theorem shift_nilpotent (n : ℕ) : shift (K := K) n ^ n = 0 := by
  apply LinearMap.ext
  intro x
  funext i
  rw [shift_pow_apply, dite_eq_right (by omega)]
  rfl

theorem shift_previous_power_nonzero (n : ℕ) (hn : 0 < n) :
    shift (K := K) n ^ (n - 1) ≠ 0 := by
  intro h
  have hh := congrFun (LinearMap.congr_fun h (fun _ => (1 : K))) (⟨0, hn⟩ : Fin n)
  simp [shift_pow_apply, Nat.ne_of_gt hn] at hh

/-- Diagonal linear automorphism; inverses are actual coordinatewise inverses. -/
def diagonalF (q a : Kˣ) (n : ℕ) : (Fin n → K) ≃ₗ[K] (Fin n → K) where
  toFun x i := ((a * q⁻¹ ^ i.val : Kˣ) : K) * x i
  invFun x i := (((a * q⁻¹ ^ i.val)⁻¹ : Kˣ) : K) * x i
  left_inv x := by funext i; simp [← mul_assoc]
  right_inv x := by funext i; simp [← mul_assoc]
  map_add' x y := by funext i; exact mul_add _ _ _
  map_smul' c x := by funext i; simp [mul_left_comm]

@[simp] theorem diagonalF_apply (q a : Kˣ) (n : ℕ) (x : Fin n → K) (i : Fin n) :
    diagonalF q a n x i = ((a * q⁻¹ ^ i.val : Kˣ) : K) * x i := rfl

theorem chain_relation (q a : Kˣ) (n : ℕ) (x : Fin n → K) :
    diagonalF q a n (shift n x) = (q : K) • shift n (diagonalF q a n x) := by
  funext i
  simp only [diagonalF_apply, shift_apply, Pi.smul_apply, smul_eq_mul]
  split_ifs with h
  · simp only [Units.val_mul, Units.val_pow_eq_pow_val, Units.val_inv_eq_inv_val, pow_succ]
    field_simp
  · simp

def specialDatum (q a : Kˣ) (n : ℕ) : Datum q (Fin n → K) where
  F := diagonalF q a n
  N := shift n
  nilpotent := ⟨n, shift_nilpotent n⟩
  relation := chain_relation q a n

/-- The kernel is precisely the first-coordinate line when n is positive. -/
theorem shift_kernel_iff (n : ℕ) (x : Fin n → K) :
    shift n x = 0 ↔ ∀ j : Fin n, j.val ≠ 0 → x j = 0 := by
  constructor
  · intro hx j hj
    have hi : j.val - 1 < n := by omega
    have hn : j.val - 1 + 1 < n := by omega
    have hidx : (⟨j.val - 1 + 1, hn⟩ : Fin n) = j := by apply Fin.ext; dsimp; omega
    have hh := congrFun hx (⟨j.val - 1, hi⟩ : Fin n)
    simpa [shift_apply, hn, hidx] using hh
  · intro hx
    funext i
    by_cases h : i.val + 1 < n
    · simpa [shift_apply, h] using hx (⟨i.val + 1, h⟩ : Fin n) (by dsimp; omega)
    · simp [shift_apply, h]

def kernelLine (n : ℕ) (hn : 0 < n) : LinearMap.ker (shift (K := K) n) ≃ₗ[K] K where
  toFun x := x.val ⟨0, hn⟩
  invFun c := ⟨fun j => if j.val = 0 then c else 0, by
    apply (shift_kernel_iff n _).2
    intro j hj
    simp [hj]⟩
  left_inv x := by
    apply Subtype.ext
    funext j
    by_cases hj : j.val = 0
    · have hidx : j = (⟨0, hn⟩ : Fin n) := by apply Fin.ext; exact hj
      simp [hidx]
    · simp [hj, (shift_kernel_iff n x.val).1 x.property j hj]
  right_inv c := by simp
  map_add' x y := rfl
  map_smul' a x := rfl

theorem kernelLine_conjugate (q a : Kˣ) (n : ℕ) (hn : 0 < n) :
    (kernelLine n hn).conj (kernelF (specialDatum q a n)).toLinearMap =
      (a : K) • (LinearMap.id : K →ₗ[K] K) := by
  apply LinearMap.ext
  intro c
  change ((a * q⁻¹ ^ 0 : Kˣ) : K) * c = (a : K) * c
  simp

theorem scalar_charpoly (a : K) :
    (a • (LinearMap.id : K →ₗ[K] K)).charpoly = X - C a := by
  rw [← LinearMap.charpoly_toMatrix _ (Module.Basis.singleton Unit K)]
  have h : LinearMap.toMatrix (Module.Basis.singleton Unit K) (Module.Basis.singleton Unit K)
      (a • (LinearMap.id : K →ₗ[K] K)) = Matrix.diagonal (fun _ : Unit => a) := by
    ext i j
    cases i; cases j
    simp [LinearMap.toMatrix_apply]
  rw [h, Matrix.charpoly_diagonal]
  simp

theorem special_kernel_charpoly (q a : Kˣ) (n : ℕ) (hn : 0 < n) :
    kernelCharpoly (specialDatum q a n) = X - C (a : K) := by
  let e : LinearMap.ker (specialDatum q a n).N ≃ₗ[K] K := kernelLine n hn
  unfold kernelCharpoly
  calc
    _ = (e.conj (kernelF (specialDatum q a n)).toLinearMap).charpoly :=
      (e.charpoly_conj _).symm
    _ = ((a : K) • (LinearMap.id : K →ₗ[K] K)).charpoly := by
      congr 1
      exact kernelLine_conjugate q a n hn
    _ = X - C (a : K) := scalar_charpoly _

theorem special_kernel_dimension (q a : Kˣ) (n : ℕ) (hn : 0 < n) :
    Module.finrank K (LinearMap.ker (specialDatum q a n).N) = 1 := by
  change Module.finrank K (LinearMap.ker (shift (K := K) n)) = 1
  rw [(kernelLine (K := K) n hn).finrank_eq]
  simp

theorem whole_charpoly (q a : Kˣ) (n : ℕ) :
    (specialDatum q a n).F.toLinearMap.charpoly =
      ∏ j : Fin n, (X - C ((a * q⁻¹ ^ j.val : Kˣ) : K)) := by
  have h : (specialDatum q a n).F.toLinearMap =
      (Matrix.diagonal (fun j : Fin n => ((a * q⁻¹ ^ j.val : Kˣ) : K))).toLin' := by
    apply LinearMap.ext
    intro x
    funext i
    simp [specialDatum, diagonalF, Matrix.toLin'_apply, Matrix.mulVec, dotProduct, Matrix.diagonal_apply]
  rw [h, Matrix.charpoly_toLin', Matrix.charpoly_diagonal]

end PaperX.SpecialMonodromy
