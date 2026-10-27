module

public import KomorebiPhysics.MixedTransfer
public import Mathlib.LinearAlgebra.Matrix.Kronecker

/-!
Chapter 4.4, equations (4.23)--(4.28): actual tensor-product matrix atlases
and marginal traces for arbitrary joint states. No product-state hypothesis
is inserted into the marginal identities. Finite-dimensional throughout.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace TensorAtlas
open scoped BigOperators Matrix Kronecker ComplexOrder

variable {m n I J : Type*}

/-- Kronecker multiplication distributes over a finite sum on the left. -/
theorem sum_kronecker_left [Fintype I]
    (A : I → Matrix m m ℂ) (B : Matrix n n ℂ) :
    (∑ i, A i) ⊗ₖ B = ∑ i, A i ⊗ₖ B := by
  ext x y
  simp only [Matrix.kroneckerMap_apply, Matrix.sum_apply, Finset.sum_mul]

/-- Kronecker multiplication distributes over a finite sum on the right. -/
theorem sum_kronecker_right [Fintype J]
    (A : Matrix m m ℂ) (B : J → Matrix n n ℂ) :
    A ⊗ₖ (∑ j, B j) = ∑ j, A ⊗ₖ B j := by
  ext x y
  simp only [Matrix.kroneckerMap_apply, Matrix.sum_apply, Finset.mul_sum]

end TensorAtlas

namespace MixedTransfer.MatrixAtlas
open scoped BigOperators Matrix Kronecker ComplexOrder
open TensorAtlas
variable {m n I J : Type*} [Fintype m] [DecidableEq m]
  [Fintype n] [DecidableEq n] [Fintype I] [DecidableEq I]
  [Fintype J] [DecidableEq J]
variable (P : MatrixAtlas m I) (Q : MatrixAtlas n J)

/-- Equation (4.23): the joint atlas is constructed by the actual Kronecker
product. Its orthogonality, completeness and adjoint laws are proved. -/
def tensor : MatrixAtlas (m × n) (I × J) where
  proj a := P.proj a.1 ⊗ₖ Q.proj a.2
  mul_proj := by
    intro a b
    rw [← Matrix.mul_kronecker_mul, P.mul_proj, Q.mul_proj]
    by_cases h₁ : a.1 = b.1 <;> by_cases h₂ : a.2 = b.2 <;>
      simp [h₁, h₂, Prod.ext_iff]
  sum_proj := by
    rw [Fintype.sum_prod_type]
    simp only [← sum_kronecker_right, Q.sum_proj, ← sum_kronecker_left,
      P.sum_proj, Matrix.one_kronecker_one]
  hermitian := by
    intro a
    rw [Matrix.conjTranspose_kronecker, P.hermitian, Q.hermitian]

/-- The constructed projector is the literal tensor product. -/
theorem tensor_proj (i : I) (j : J) :
    (P.tensor Q).proj (i,j) = P.proj i ⊗ₖ Q.proj j := rfl

/-- Equation (4.24), with both address equalities made explicit. -/
theorem tensor_mul_proj (i k : I) (j l : J) :
    (P.tensor Q).proj (i,j) * (P.tensor Q).proj (k,l) =
      if i = k ∧ j = l then (P.tensor Q).proj (i,j) else 0 := by
  simpa only [Prod.mk.injEq] using (P.tensor Q).mul_proj (i,j) (k,l)

/-- Equation (4.25): the joint projectors sum to the joint identity. -/
theorem tensor_sum_proj : (∑ i, ∑ j, (P.tensor Q).proj (i,j)) = 1 := by
  simpa only [Fintype.sum_prod_type] using (P.tensor Q).sum_proj

/-- Resolving only the second address leaves the first projector tensored
with the identity, with no assumption on a state. -/
theorem tensor_sum_right_proj (i : I) :
    (∑ j, (P.tensor Q).proj (i,j)) = P.proj i ⊗ₖ (1 : Matrix n n ℂ) := by
  simp only [tensor_proj, ← sum_kronecker_right, Q.sum_proj]

/-- Resolving only the first address leaves the second projector. -/
theorem tensor_sum_left_proj (j : J) :
    (∑ i, (P.tensor Q).proj (i,j)) = (1 : Matrix m m ℂ) ⊗ₖ Q.proj j := by
  simp only [tensor_proj, ← sum_kronecker_left, P.sum_proj]

/-- The first subsystem is a genuine address-map coarsening of the joint atlas. -/
theorem tensor_coarsen_fst_proj (i : I) :
    ((P.tensor Q).coarsen Prod.fst).proj i =
      P.proj i ⊗ₖ (1 : Matrix n n ℂ) := by
  rw [coarsen_proj]
  simp only [Atlas.fiber, Finset.sum_filter, Fintype.sum_prod_type]
  rw [Finset.sum_comm]
  simp only [Finset.sum_ite_eq', Finset.mem_univ, ite_true]
  exact P.tensor_sum_right_proj Q i

/-- The second subsystem is also an actual address-map coarsening. -/
theorem tensor_coarsen_snd_proj (j : J) :
    ((P.tensor Q).coarsen Prod.snd).proj j =
      (1 : Matrix m m ℂ) ⊗ₖ Q.proj j := by
  rw [coarsen_proj]
  simp only [Atlas.fiber, Finset.sum_filter, Fintype.sum_prod_type]
  simp only [Finset.sum_ite_eq', Finset.mem_univ, ite_true]
  exact P.tensor_sum_left_proj Q j

/-- Equation (4.27), in the stronger complex form: no Hermiticity or
factorization is needed for the marginal trace identity itself. -/
theorem tensor_marginal_left_trace (ρ : Matrix (m × n) (m × n) ℂ) (i : I) :
    (∑ j, Matrix.trace ((P.tensor Q).proj (i,j) * ρ)) =
      Matrix.trace ((P.proj i ⊗ₖ (1 : Matrix n n ℂ)) * ρ) := by
  rw [← Matrix.trace_sum, ← Finset.sum_mul, P.tensor_sum_right_proj Q]

/-- Equation (4.28), likewise valid for every joint complex matrix. -/
theorem tensor_marginal_right_trace (ρ : Matrix (m × n) (m × n) ℂ) (j : J) :
    (∑ i, Matrix.trace ((P.tensor Q).proj (i,j) * ρ)) =
      Matrix.trace (((1 : Matrix m m ℂ) ⊗ₖ Q.proj j) * ρ) := by
  rw [← Matrix.trace_sum, ← Finset.sum_mul, P.tensor_sum_left_proj Q]

/-- The real-valued first marginal of the actual joint probabilities. -/
theorem tensor_marginal_left (ρ : Matrix (m × n) (m × n) ℂ) (i : I) :
    (∑ j, (P.tensor Q).probability ρ (i,j)) =
      (Matrix.trace ((P.proj i ⊗ₖ (1 : Matrix n n ℂ)) * ρ)).re := by
  simp only [probability, ← Complex.re_sum, P.tensor_marginal_left_trace Q]

/-- The real-valued second marginal of the actual joint probabilities. -/
theorem tensor_marginal_right (ρ : Matrix (m × n) (m × n) ℂ) (j : J) :
    (∑ i, (P.tensor Q).probability ρ (i,j)) =
      (Matrix.trace (((1 : Matrix m m ℂ) ⊗ₖ Q.proj j) * ρ)).re := by
  simp only [probability, ← Complex.re_sum, P.tensor_marginal_right_trace Q]

/-- A positive trace-one joint state gives a normalized joint distribution.
This includes correlated and entangled states. -/
theorem tensor_probability_normalized (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.PosSemidef) (ht : Matrix.trace ρ = 1) :
    (∑ i, ∑ j, (P.tensor Q).probability ρ (i,j)) = 1 ∧
      ∀ i j, 0 ≤ (P.tensor Q).probability ρ (i,j) ∧
        (P.tensor Q).probability ρ (i,j) ≤ 1 := by
  obtain ⟨hs,hb⟩ := (P.tensor Q).probability_normalized ρ hρ ht
  exact ⟨by simpa only [Fintype.sum_prod_type] using hs, fun i j => hb (i,j)⟩

/-- Product-state factorization is a separate identity with the tensor
state hypothesis present in the statement. -/
theorem tensor_product_trace (σ : Matrix m m ℂ) (τ : Matrix n n ℂ) (i : I) (j : J) :
    Matrix.trace ((P.tensor Q).proj (i,j) * (σ ⊗ₖ τ)) =
      Matrix.trace (P.proj i * σ) * Matrix.trace (Q.proj j * τ) := by
  rw [tensor_proj, ← Matrix.mul_kronecker_mul, Matrix.trace_kronecker]

/-- Only for a product state do joint probabilities factor in this theorem.
Hermiticity discharges the reality of the two complex traces. -/
theorem tensor_product_probability (σ : Matrix m m ℂ) (τ : Matrix n n ℂ)
    (hσ : σ.conjTranspose = σ) (hτ : τ.conjTranspose = τ) (i : I) (j : J) :
    (P.tensor Q).probability (σ ⊗ₖ τ) (i,j) =
      P.probability σ i * Q.probability τ j := by
  rw [probability, P.tensor_product_trace Q]
  simp only [Complex.mul_re, P.trace_probability_real σ hσ,
    Q.trace_probability_real τ hτ, mul_zero, sub_zero, probability]

/-- The joint probability derivative comes from the actual joint von Neumann
flow. The Hamiltonian need not split into local terms. -/
theorem tensor_hasDerivAt_probability {H : Matrix (m × n) (m × n) ℂ}
    {ρ : ℝ → Matrix (m × n) (m × n) ℂ} {t : ℝ}
    (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t) (i : I) (j : J) :
    HasDerivAt (fun s => (P.tensor Q).probability (ρ s) (i,j))
      (∑ k, ∑ l, (P.tensor Q).current H (ρ t) (i,j) (k,l)) t := by
  simpa only [Fintype.sum_prod_type] using
    (P.tensor Q).hasDerivAt_probability hH hρt hρ (i,j)

end MixedTransfer.MatrixAtlas
end KomorebiPhysics
