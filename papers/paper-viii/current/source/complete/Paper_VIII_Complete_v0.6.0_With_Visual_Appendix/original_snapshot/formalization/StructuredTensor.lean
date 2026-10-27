module
public import Mathlib.LinearAlgebra.Matrix.Vec
public import Mathlib.Data.Fintype.Card
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 4.5 and 4.6. Actual column-major vectorization and recursively
implemented tensor contractions. Counts use the declared two-operation
multiply-accumulate model, not a hardware instruction model.
-/
@[expose] public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators Kronecker
open Matrix

/-- Column-major convention, with ordinary transpose rather than adjoint. -/
theorem kronecker_modewise {M N : Type*} [Fintype M] [Fintype N]
    (A : Matrix M M ℂ) (B : Matrix N N ℂ) (X : Matrix N M ℂ) :
    (A ⊗ₖ B) *ᵥ Matrix.vec X = Matrix.vec (B * X * Aᵀ) := by
  exact Matrix.kronecker_mulVec_vec B X A

abbrev TwoModeOperations (m n : ℕ) :=
  ((Fin n × Fin n) × Fin m × Bool) ⊕ ((Fin n × Fin m) × Fin m × Bool)

theorem kronecker_modewise_work (m n : ℕ) :
    Fintype.card (TwoModeOperations m n) = 2*n^2*m + 2*n*m^2 := by
  simp [TwoModeOperations, Fintype.card_prod]
  ring

theorem kronecker_factor_storage (m n : ℕ) :
    Fintype.card ((Fin n × Fin n) ⊕ (Fin m × Fin m)) = n^2+m^2 ∧
    Fintype.card ((Fin m × Fin n) × (Fin m × Fin n)) = n^2*m^2 := by
  simp [Fintype.card_prod, pow_two, mul_comm, mul_left_comm]

/-- A nested product records tensor coordinates without an implicit reindexing. -/
def TensorIndex (d : ℕ) : ℕ → Type
  | 0 => Unit
  | k+1 => Fin d × TensorIndex d k

instance tensorFintype (d k : ℕ) : Fintype (TensorIndex d k) := by
  induction k with
  | zero => exact inferInstanceAs (Fintype Unit)
  | succ k ih => exact @instFintypeProd _ _ inferInstance ih

instance tensorDecidableEq (d : ℕ) : (k : ℕ) → DecidableEq (TensorIndex d k)
  | 0 => inferInstanceAs (DecidableEq Unit)
  | k+1 => @instDecidableEqProd (Fin d) (TensorIndex d k) inferInstance (tensorDecidableEq d k)

theorem tensor_dimension (d k : ℕ) : Fintype.card (TensorIndex d k) = d^k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    change Fintype.card (Fin d × TensorIndex d k) = _
    simp [ih, pow_succ, mul_comm]

/-- The represented operator is an iterated actual Kronecker product. -/
def tensorMatrix (d : ℕ) : (k : ℕ) →
    (Fin k → Matrix (Fin d) (Fin d) ℂ) →
    Matrix (TensorIndex d k) (TensorIndex d k) ℂ
  | 0, _ => fun _ _ => 1
  | k+1, A => A 0 ⊗ₖ tensorMatrix d k (fun j => A j.succ)

/-- Contract the trailing modes on each first-index slice, then the first mode. -/
def tensorApply (d : ℕ) : (k : ℕ) →
    (Fin k → Matrix (Fin d) (Fin d) ℂ) →
    (TensorIndex d k → ℂ) → (TensorIndex d k → ℂ)
  | 0, _, x => x
  | k+1, A, x => fun p =>
      ∑ j, A 0 p.1 j * tensorApply d k (fun i => A i.succ) (fun u => x (j,u)) p.2

theorem tensor_apply_correct (d k : ℕ) (A : Fin k → Matrix (Fin d) (Fin d) ℂ)
    (x : TensorIndex d k → ℂ) :
    tensorApply d k A x = tensorMatrix d k A *ᵥ x := by
  induction k with
  | zero =>
    funext i
    cases i
    change x PUnit.unit = ∑ i : Unit, (1 : ℂ) * x i
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
    change (∑ j, A 0 p.1 j * tensorApply d k (fun i => A i.succ) (fun u => x (j,u)) p.2) = _
    simp_rw [ih]
    change (∑ j, A 0 p.1 j * (∑ u, tensorMatrix d k (fun i => A i.succ) p.2 u * x (j,u))) =
      ∑ i : Fin d × TensorIndex d k,
        (A 0 p.1 i.1 * tensorMatrix d k (fun j => A j.succ) p.2 i.2) * x i
    simp only [Fintype.sum_prod_type, Finset.mul_sum, mul_assoc]

/-- Actual declared arithmetic events for the recursive contraction algorithm. -/
def TensorOperation (d : ℕ) : ℕ → Type
  | 0 => Empty
  | k+1 => (Fin d × TensorOperation d k) ⊕
      (TensorIndex d k × Fin d × Fin d × Bool)

instance tensorOperationFintype (d k : ℕ) : Fintype (TensorOperation d k) := by
  induction k with
  | zero => exact inferInstanceAs (Fintype Empty)
  | succ k ih =>
    change Fintype ((Fin d × TensorOperation d k) ⊕ (TensorIndex d k × Fin d × Fin d × Bool))
    letI := ih
    exact inferInstance

theorem tensor_modewise_work (d k : ℕ) :
    Fintype.card (TensorOperation d k) = 2*k*d^(k+1) := by
  induction k with
  | zero =>
    change Fintype.card Empty = _
    simp
  | succ k ih =>
    change Fintype.card ((Fin d × TensorOperation d k) ⊕
      (TensorIndex d k × Fin d × Fin d × Bool)) = _
    simp only [Fintype.card_sum, Fintype.card_prod, Fintype.card_fin,
      Fintype.card_bool, tensor_dimension, ih]
    simp only [pow_succ]
    ring

theorem tensor_factor_storage (d k : ℕ) :
    Fintype.card (Fin k × Fin d × Fin d) = k*d^2 := by
  simp [pow_two]

end KomorebiPaperVIII

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.kronecker_modewise
#print axioms KomorebiPaperVIII.kronecker_modewise_work
#print axioms KomorebiPaperVIII.kronecker_factor_storage
#print axioms KomorebiPaperVIII.tensor_dimension
#print axioms KomorebiPaperVIII.tensor_apply_correct
#print axioms KomorebiPaperVIII.tensor_modewise_work
#print axioms KomorebiPaperVIII.tensor_factor_storage

#print axioms KomorebiPaperVIII.tensorMatrix

#print axioms KomorebiPaperVIII.tensorApply

#print axioms KomorebiPaperVIII.TensorOperation
