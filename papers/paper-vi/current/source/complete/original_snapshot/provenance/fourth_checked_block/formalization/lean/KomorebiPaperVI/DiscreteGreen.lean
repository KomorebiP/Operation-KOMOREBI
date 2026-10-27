import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Matrix.Basic
import Mathlib.Tactic

/-! Author: Komorebi P. The literal Dirichlet tridiagonal inverse at every grid size. -/
namespace KomorebiPaperVI.DiscreteGreen
open scoped BigOperators
set_option backward.isDefEq.respectTransparency false

noncomputable def green (N : ℝ) (i j : ℕ) : ℝ :=
  min (i:ℝ) (j:ℝ)-(i:ℝ)*(j:ℝ)/N

theorem green_zero (N : ℝ) (j : ℕ) : green N 0 j=0 := by simp [green]

theorem green_end (n j : ℕ) (hj : j  ≤  n+1) : green (n+1) (n+1) j=0 := by
  have h : (j:ℝ)  ≤  n+1 := by exact_mod_cast hj
  have hn : (n:ℝ)+1≠0 := by positivity
  simp only [green,Nat.cast_add,Nat.cast_one,min_eq_right h]
  field_simp
  ring

theorem green_second_difference (N : ℝ) (i j : ℕ) :
    2*green N (i+1) j-green N i j-green N (i+2) j=if i+1=j then 1 else 0 := by
  unfold green
  by_cases ha : j  ≤  i
  · have h0 : (j:ℝ) ≤ i := by exact_mod_cast ha
    have h1 : (j:ℝ) ≤ (i+1:ℕ) := by exact_mod_cast (show j ≤ i+1 by omega)
    have h2 : (j:ℝ) ≤ (i+2:ℕ) := by exact_mod_cast (show j ≤ i+2 by omega)
    rw [min_eq_right h1,min_eq_right h0,min_eq_right h2,ite_eq_right (by omega)]
    push_cast
    ring
  · by_cases hb : j=i+1
    · subst j
      have h0 : (i:ℝ) ≤ (i+1:ℕ) := by exact_mod_cast (show i ≤ i+1 by omega)
      have h2 : ((i+1:ℕ):ℝ) ≤ (i+2:ℕ) := by exact_mod_cast (show i+1 ≤ i+2 by omega)
      rw [min_self,min_eq_left h0,min_eq_right h2,ite_eq_left rfl]
      push_cast
      ring
    · have h0 : (i:ℝ) ≤ j := by exact_mod_cast (show i ≤ j by omega)
      have h1 : ((i+1:ℕ):ℝ) ≤ j := by exact_mod_cast (show i+1 ≤ j by omega)
      have h2 : ((i+2:ℕ):ℝ) ≤ j := by exact_mod_cast (show i+2 ≤ j by omega)
      rw [min_eq_left h1,min_eq_left h0,min_eq_left h2,ite_eq_right (by omega)]
      push_cast
      ring

noncomputable def tridiagonal (n : ℕ) : Matrix (Fin n) (Fin n) ℝ := fun i j =>
  (if i=j then 2 else 0)-(if j.val=i.val+1 then 1 else 0)-(if j.val+1=i.val then 1 else 0)

noncomputable def inverseKernel (n : ℕ) : Matrix (Fin n) (Fin n) ℝ :=
  fun i j => green (n+1) (i.val+1) (j.val+1)

theorem sparse_sum (n q : ℕ) (v : Fin n → ℝ) :
    (∑ k : Fin n, if k.val=q then v k else 0)=if h:q < n then v ⟨q,h⟩ else 0 := by
  classical
  split_ifs with h
  · rw [Finset.sum_eq_single (⟨q,h⟩ : Fin n)]
    · simp
    · intro k _ hk
      exact ite_eq_right (by intro he; apply hk; exact Fin.ext he)
    · simp
  · apply Finset.sum_eq_zero
    intro k _
    exact ite_eq_right (by omega)

theorem tridiagonal_mul (n : ℕ) (M : Matrix (Fin n) (Fin n) ℝ) (i j : Fin n) :
    (tridiagonal n*M) i j=2*M i j-
      (if h:i.val+1 < n then M ⟨i.val+1,h⟩ j else 0)-
      (if h:0 < i.val then M ⟨i.val-1,by omega⟩ j else 0) := by
  classical
  simp only [Matrix.mul_apply,tridiagonal,sub_mul,Finset.sum_sub_distrib,ite_mul,one_mul,zero_mul]
  rw [Finset.sum_ite_eq,sparse_sum]
  simp only [Finset.mem_univ,ite_true]
  congr 1
  by_cases h:0 < i.val
  · rw [dite_eq_left h,Finset.sum_eq_single (⟨i.val-1,by omega⟩ : Fin n)]
    · simp [show i.val-1+1=i.val by omega]
    · intro k _ hk
      exact ite_eq_right (by intro he; apply hk; apply Fin.ext; change k.val=i.val-1; omega)
    · simp
  · rw [dite_eq_right h]
    apply Finset.sum_eq_zero
    intro k _
    exact ite_eq_right (by omega)

theorem tridiagonal_inverse_kernel (n : ℕ) : tridiagonal n*inverseKernel n=1 := by
  ext i j
  rw [tridiagonal_mul]
  have h := green_second_difference (n+1) i.val (j.val+1)
  have hu : (if h:i.val+1 < n then inverseKernel n ⟨i.val+1,h⟩ j else 0)=
      green (n+1) (i.val+2) (j.val+1) := by
    split_ifs with hi
    · rfl
    · have he : i.val+2=n+1 := by omega
      rw [he,green_end n (j.val+1) (by omega)]
  have hd : (if h:0 < i.val then inverseKernel n ⟨i.val-1,by omega⟩ j else 0)=
      green (n+1) i.val (j.val+1) := by
    split_ifs with hi
    · simp only [inverseKernel]
      congr 1
      omega
    · have he : i.val=0 := by omega
      rw [he,green_zero]
  rw [hu,hd]
  simp only [inverseKernel,Matrix.one_apply]
  have he : (i.val+1=j.val+1) ↔ i=j := by constructor  <;> intro hh; exact Fin.ext (by omega); subst j; rfl
  simp only [he] at h
  linarith

theorem inverse_eq_kernel (n : ℕ) : (tridiagonal n)⁻¹=inverseKernel n := by
  exact Matrix.inv_eq_right_inv (tridiagonal_inverse_kernel n)

noncomputable def laplacian (n : ℕ) : Matrix (Fin n) (Fin n) ℝ :=
  ((n:ℝ)+1)^2 • tridiagonal n

theorem laplacian_inverse (n : ℕ) :
    (laplacian n)⁻¹=(((n:ℝ)+1)^2)⁻¹ • inverseKernel n := by
  apply Matrix.inv_eq_right_inv
  rw [laplacian,smul_mul_smul_comm,tridiagonal_inverse_kernel]
  have hn : ((n:ℝ)+1)^2≠0 := by positivity
  simp [hn]

theorem grid_reconstruction (n : ℕ) (i j : Fin n) :
    ((n:ℝ)+1)*(laplacian n)⁻¹ i j=
      min (((i.val:ℝ)+1)/((n:ℝ)+1)) (((j.val:ℝ)+1)/((n:ℝ)+1))-
        (((i.val:ℝ)+1)/((n:ℝ)+1))*(((j.val:ℝ)+1)/((n:ℝ)+1)) := by
  rw [laplacian_inverse]
  simp only [Matrix.smul_apply,smul_eq_mul,inverseKernel,green,Nat.cast_add,Nat.cast_one]
  rw [min_div_div_right (by positivity)]
  field_simp

end KomorebiPaperVI.DiscreteGreen
