import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Data.Fintype.BigOperators
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Tactic

/-! Author: Komorebi P. Enumerated finite path law and the actual potential-weighted matrix. -/
namespace KomorebiPaperVI.FeynmanKac
open scoped BigOperators
variable {I : Type*} [Fintype I] [DecidableEq I]

noncomputable def pathProbability (K : Matrix I I ℝ) : (n : ℕ) → I → (Fin n → I) → ℝ
  | 0, _, _ => 1
  | n+1, i, x => K (x 0) i*pathProbability K n (x 0) (Fin.tail x)

noncomputable def pathPotential (V : I → ℝ) : (n : ℕ) → I → (Fin n → I) → ℝ
  | 0, _, _ => 0
  | n+1, i, x => V i+pathPotential V n (x 0) (Fin.tail x)

def terminal : (n : ℕ) → I → (Fin n → I) → I
  | 0, i, _ => i
  | n+1, _, x => terminal n (x 0) (Fin.tail x)

noncomputable def pathExpectation (K : Matrix I I ℝ) (V f : I → ℝ) (n : ℕ) (i : I) : ℝ :=
  ∑ x : Fin n → I, pathProbability K n i x*Real.exp (-pathPotential V n i x)*f (terminal n i x)

noncomputable def transfer (K : Matrix I I ℝ) (V : I → ℝ) : Matrix I I ℝ :=
  Matrix.diagonal (fun i => Real.exp (-V i))*K.transpose

omit [DecidableEq I] in
theorem sum_paths_succ (n : ℕ) (F : (Fin (n+1) → I) → ℝ) :
    (∑ x, F x)=∑ i, ∑ y : Fin n → I, F (Fin.cons i y) := by
  have h := (Fin.consEquiv (fun _ : Fin (n+1) => I)).sum_comp F
  change (∑ x : I × (Fin n → I), F (Fin.cons x.1 x.2))=∑ x : Fin (n+1) → I, F x at h
  rw [Fintype.sum_prod_type] at h
  exact h.symm

theorem transfer_entry (K : Matrix I I ℝ) (V : I → ℝ) (i j : I) :
    transfer K V i j=Real.exp (-V i)*K j i := by simp [transfer]

omit [Fintype I] [DecidableEq I] in
theorem path_probability_nonnegative (K : Matrix I I ℝ) (hK : ∀ i j, 0 ≤ K i j)
    (n : ℕ) (i : I) (x : Fin n → I) : 0 ≤ pathProbability K n i x := by
  induction n generalizing i with
  | zero => exact zero_le_one
  | succ n ih => exact mul_nonneg (hK _ _) (ih _ _)

omit [DecidableEq I] in
theorem path_probability_mass (K : Matrix I I ℝ) (hK : ∀ j, ∑ i, K i j=1)
    (n : ℕ) (i : I) : (∑ x : Fin n → I, pathProbability K n i x)=1 := by
  induction n generalizing i with
  | zero => simp [pathProbability]
  | succ n ih =>
    rw [sum_paths_succ]
    simp only [pathProbability,Fin.cons_zero,Fin.tail_cons,← Finset.mul_sum,ih,mul_one,hK]

omit [DecidableEq I] in
theorem path_expectation_zero (K : Matrix I I ℝ) (V f : I → ℝ) (i : I) :
    pathExpectation K V f 0 i=f i := by simp [pathExpectation,pathProbability,pathPotential,terminal]

omit [DecidableEq I] in
theorem path_expectation_step (K : Matrix I I ℝ) (V f : I → ℝ) (n : ℕ) (i : I) :
    pathExpectation K V f (n+1) i=
      Real.exp (-V i)*∑ j, K j i*pathExpectation K V f n j := by
  unfold pathExpectation
  rw [sum_paths_succ]
  simp only [pathProbability,pathPotential,terminal,Fin.cons_zero,Fin.tail_cons,neg_add,
    Real.exp_add,Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro x _
  ring

theorem feynman_kac_path_formula (K : Matrix I I ℝ) (V f : I → ℝ) (n : ℕ) :
    (transfer K V ^ n).mulVec f=pathExpectation K V f n := by
  induction n with
  | zero => funext i; simp [path_expectation_zero]
  | succ n ih =>
    rw [pow_succ',← Matrix.mulVec_mulVec,ih]
    funext i
    rw [path_expectation_step]
    simp only [Matrix.mulVec,dotProduct,transfer_entry,Finset.mul_sum,mul_assoc]

omit [Fintype I] [DecidableEq I] in
theorem path_probability_product (K : Matrix I I ℝ) (n : ℕ) (i : I) (x : Fin n → I) :
    pathProbability K n i x = ∏ r : Fin n,
      K ((Fin.cons i x : Fin (n+1) → I) r.succ) ((Fin.cons i x : Fin (n+1) → I) r.castSucc) := by
  induction n generalizing i with
  | zero => simp [pathProbability]
  | succ n ih =>
    rw [pathProbability,ih,Fin.prod_univ_succ]
    simp [Fin.castSucc_succ,Fin.cons_self_tail,Fin.tail]

omit [Fintype I] [DecidableEq I] in
theorem path_potential_sum (V : I → ℝ) (n : ℕ) (i : I) (x : Fin n → I) :
    pathPotential V n i x = ∑ r : Fin n, V ((Fin.cons i x : Fin (n+1) → I) r.castSucc) := by
  induction n generalizing i with
  | zero => simp [pathPotential]
  | succ n ih =>
    rw [pathPotential,ih,Fin.sum_univ_succ]
    simp [Fin.castSucc_succ,Fin.cons_self_tail]

omit [Fintype I] [DecidableEq I] in
theorem terminal_last (n : ℕ) (i : I) (x : Fin n → I) :
    terminal n i x = (Fin.cons i x : Fin (n+1) → I) (Fin.last n) := by
  induction n generalizing i with
  | zero => simp [terminal]
  | succ n ih =>
    rw [terminal,ih,← Fin.succ_last]
    simp

end KomorebiPaperVI.FeynmanKac
