module
public import StructuredTensor
public import Mathlib.LinearAlgebra.Matrix.Block
public import Mathlib.Data.Nat.Log
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 4.7: recursively constructed Walsh matrices, actual butterfly
application, and an exact count of scalar additions/subtractions.
-/
@[expose] public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open Matrix
open scoped BigOperators Kronecker

/-- The first tensor coordinate distinguishes the upper and lower half. -/
def walshTwo : Matrix (Fin 2) (Fin 2) ℂ := !![1,1;1,-1]

theorem walsh_two_orthogonal : walshTwo * walshTwoᵀ = (2:ℂ) • 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [walshTwo, Matrix.mul_apply, Fin.sum_univ_two]

def walshMatrix : (k : ℕ) → Matrix (TensorIndex 2 k) (TensorIndex 2 k) ℂ
  | 0 => fun _ _ => 1
  | k+1 => walshTwo ⊗ₖ walshMatrix k

theorem walsh_recursion (k : ℕ) :
    walshMatrix (k+1) = walshTwo ⊗ₖ walshMatrix k := rfl

/-- This is the ordinary transpose identity over the complex scalar field. -/
theorem walsh_orthogonal (k : ℕ) :
    walshMatrix k * (walshMatrix k)ᵀ = ((2:ℂ)^k) • 1 := by
  induction k with
  | zero =>
    have hb : walshMatrix 0 = 1 := by
      ext i j
      cases i
      cases j
      change (1:ℂ) = if (PUnit.unit : Unit) = PUnit.unit then 1 else 0
      simp
    rw [hb]
    simp
  | succ k ih =>
    change (walshTwo ⊗ₖ walshMatrix k) * (walshTwo ⊗ₖ walshMatrix k)ᵀ = _
    rw [← Matrix.kroneckerMap_transpose, ← Matrix.mul_kronecker_mul, walsh_two_orthogonal, ih,
      Matrix.smul_kronecker, Matrix.kronecker_smul, Matrix.one_kronecker_one, smul_smul]
    change ((2:ℂ) * 2^k) • (1 : Matrix (Fin 2 × TensorIndex 2 k) (Fin 2 × TensorIndex 2 k) ℂ) =
      (2:ℂ)^(k+1) • (1 : Matrix (Fin 2 × TensorIndex 2 k) (Fin 2 × TensorIndex 2 k) ℂ)
    rw [pow_succ, mul_comm]

/-- Two recursive transforms of the elementwise sum and difference of the halves. -/
def walshApply : (k : ℕ) → (TensorIndex 2 k → ℂ) → (TensorIndex 2 k → ℂ)
  | 0, x => x
  | k+1, x => fun p =>
      if p.1 = 0 then walshApply k (fun u => x (0,u)+x (1,u)) p.2
      else walshApply k (fun u => x (0,u)-x (1,u)) p.2

theorem walsh_apply_correct (k : ℕ) (x : TensorIndex 2 k → ℂ) :
    walshApply k x = walshMatrix k *ᵥ x := by
  induction k with
  | zero =>
    funext i
    cases i
    change x PUnit.unit = ∑ i : Unit, (1:ℂ)*x i
    simp only [one_mul]
    symm
    apply Finset.sum_eq_single PUnit.unit
    · intro b _ h
      cases b
      exact (h rfl).elim
    · intro h
      exact (h (Finset.mem_univ _)).elim
  | succ k ih =>
    funext p
    rcases p with ⟨i,u⟩
    change (if i = 0 then walshApply k (fun v => x (0,v)+x (1,v)) u
      else walshApply k (fun v => x (0,v)-x (1,v)) u) =
        ∑ v : Fin 2 × TensorIndex 2 k, (walshTwo i v.1 * walshMatrix k u v.2) * x v
    simp_rw [ih]
    fin_cases i <;>
      simp [walshTwo, Matrix.mulVec, dotProduct, Fintype.sum_prod_type,
        Fin.sum_univ_two, mul_add, Finset.sum_add_distrib, sub_eq_add_neg]

/-- Addition/subtraction event addresses of the actual recursive algorithm. -/
def WalshOperation : ℕ → Type
  | 0 => Empty
  | k+1 => (Fin 2 × WalshOperation k) ⊕ (TensorIndex 2 k × Bool)

instance walshOperationFintype (k : ℕ) : Fintype (WalshOperation k) := by
  induction k with
  | zero => exact inferInstanceAs (Fintype Empty)
  | succ k ih =>
    change Fintype ((Fin 2 × WalshOperation k) ⊕ (TensorIndex 2 k × Bool))
    letI := ih
    exact inferInstance

theorem walsh_operation_count (k : ℕ) : Fintype.card (WalshOperation k) = k*2^k := by
  induction k with
  | zero =>
    change Fintype.card Empty = _
    simp
  | succ k ih =>
    change Fintype.card ((Fin 2 × WalshOperation k) ⊕ (TensorIndex 2 k × Bool)) = _
    simp only [Fintype.card_sum, Fintype.card_prod, Fintype.card_fin, Fintype.card_bool,
      tensor_dimension, ih, pow_succ]
    ring

theorem walsh_inverse_action (k : ℕ) (x : TensorIndex 2 k → ℂ) :
    walshMatrix k *ᵥ ((walshMatrix k)ᵀ *ᵥ x) = ((2:ℂ)^k) • x := by
  rw [Matrix.mulVec_mulVec, walsh_orthogonal, Matrix.smul_mulVec, Matrix.one_mulVec]

/-- The manuscript's N log2(N) formula, with N = 2^k. -/
theorem walsh_log_operation_count (k : ℕ) :
    Fintype.card (WalshOperation k) = 2^k * Nat.log2 (2^k) := by
  rw [walsh_operation_count, Nat.log2_eq_log_two, Nat.log_pow Nat.one_lt_two, mul_comm]

end KomorebiPaperVIII

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.walsh_two_orthogonal
#print axioms KomorebiPaperVIII.walsh_recursion
#print axioms KomorebiPaperVIII.walsh_orthogonal
#print axioms KomorebiPaperVIII.walsh_apply_correct
#print axioms KomorebiPaperVIII.walsh_operation_count
#print axioms KomorebiPaperVIII.walsh_inverse_action

#print axioms KomorebiPaperVIII.walsh_log_operation_count

#print axioms KomorebiPaperVIII.walshMatrix

#print axioms KomorebiPaperVIII.walshApply
