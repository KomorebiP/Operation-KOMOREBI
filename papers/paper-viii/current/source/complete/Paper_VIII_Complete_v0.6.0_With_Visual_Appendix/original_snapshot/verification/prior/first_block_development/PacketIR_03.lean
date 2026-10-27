module

public import QuantumPacketCore
import all QuantumPacketCore
public import Mathlib.LinearAlgebra.Matrix.Kronecker

/-!
Author: Komorebi P.
Paper VIII (strengthened edition), exact packet semantics, items 2.3, 2.5, 2.6.
The unchanged Paper VII module supplies the algebraic projector calculus.
Active addresses below mean exact nonzero blocks, not thresholded numerical tests.
-/

public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators
open KomorebiPaperVII

section PacketSemantics
variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I)

/-- Target index precedes source index. The support is exact. -/
noncomputable def activeBlocks (A : R) : Finset (I × I) := by
  classical
  exact Finset.univ.filter (fun e => P.block A e.1 e.2 ≠ 0)

/-- Evaluation of the stored nonzero packet blocks. -/
noncomputable def evalActive (A : R) : R :=
  ∑ e ∈ activeBlocks P A, P.block A e.1 e.2

theorem active_iff (A : R) (b a : I) :
    (b, a) ∈ activeBlocks P A ↔ P.block A b a ≠ 0 := by
  classical
  simp [activeBlocks]

/-- Theorem 2.3: removing exact zero blocks preserves the actual operator. -/
theorem exact_active_evaluation (A : R) : evalActive P A = A := by
  classical
  have term (e : I × I) :
      (if P.block A e.1 e.2 ≠ 0 then P.block A e.1 e.2 else 0) =
      P.block A e.1 e.2 := by
    by_cases h : P.block A e.1 e.2 = 0 <;> simp [h]
  simp only [evalActive, activeBlocks, Finset.sum_filter]
  simp_rw [term]
  simpa only [Fintype.sum_prod_type] using P.reconstruct A

/-- The exact identity acts on arbitrary modules, including batches of columns. -/
theorem exact_active_action {M : Type*} [AddCommMonoid M] [Module R M]
    (A : R) (x : M) : A • x = ∑ e ∈ activeBlocks P A, P.block A e.1 e.2 • x := by
  rw [← Finset.sum_smul]
  exact congrArg (fun a : R => a • x) (exact_active_evaluation P A).symm

/-- Theorem 2.5: the actual product block, without assuming a sparsity pattern. -/
theorem exact_block_composition (A B : R) (b a : I) :
    P.block (A * B) b a = ∑ c, P.block A b c * P.block B c a :=
  P.compose_blocks A B b a

/-- Support composition is an inclusion. Cancellation can make it strict. -/
theorem product_support_inclusion (A B : R) (b a : I)
    (h : P.block (A * B) b a ≠ 0) :
    ∃ c, P.block A b c ≠ 0 ∧ P.block B c a ≠ 0 := by
  classical
  by_contra no
  apply h
  rw [P.compose_blocks]
  apply Finset.sum_eq_zero
  intro c _
  by_cases hc : P.block A b c = 0
  · simp [hc]
  · have hd : P.block B c a = 0 := by
      by_contra hd
      exact no ⟨c, hc, hd⟩
    simp [hd]

theorem block_sum {J : Type*} (s : Finset J) (A : J → R) (b a : I) :
    P.block (∑ j ∈ s, A j) b a = ∑ j ∈ s, P.block (A j) b a := by
  simp [PacketFamily.block, Finset.mul_sum, Finset.sum_mul]

theorem all_blocks_zero (A : R) (h : ∀ b a, P.block A b a = 0) : A = 0 := by
  rw [← P.reconstruct A]
  simp [h]

end PacketSemantics

section Adjoint
variable {R I : Type*} [Ring R] [StarRing R] [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I) (hstar : ∀ a, star (P.proj a) = P.proj a)
include hstar

/-- Corollary 2.6, adjoint half. Self-adjointness of the packet projectors is explicit. -/
theorem exact_adjoint_block (A : R) (b a : I) :
    star (P.block A b a) = P.block (star A) a b :=
  P.adjoint_block hstar A b a
end Adjoint

section Matrices
variable {K X Y I J : Type*} [CommRing K]
variable [Fintype X] [DecidableEq X] [Fintype Y] [DecidableEq Y]
variable [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]

/-- Actual coordinate projectors for any finite partition, with unequal or empty packets allowed. -/
def coordinatePackets (tag : X → I) : PacketFamily (Matrix X X K) I where
  proj i := Matrix.diagonal (fun x => if tag x = i then 1 else 0)
  mul_proj i j := by
    rw [Matrix.diagonal_mul_diagonal]
    by_cases h : i = j
    · subst j
      simp only [ite_true]
      congr 1
      funext x
      by_cases hx : tag x = i <;> simp [hx]
    · simp only [h, ite_false]
      ext x y
      by_cases hx : tag x = i
      · simp [Matrix.diagonal_apply, hx, h]
      · simp [Matrix.diagonal_apply, hx]
  sum_proj := by
    ext x y
    by_cases h : x = y
    · subst y
      simp [Matrix.sum_apply, Matrix.diagonal_apply]
    · simp [Matrix.sum_apply, Matrix.diagonal_apply, h]

/-- Coordinate projectors act by retaining precisely one packet's entries. -/
theorem coordinate_projector_apply (tag : X → I) (i : I) (x : X → K) (u : X) :
    ((coordinatePackets (K := K) tag).proj i).mulVec x u =
      if tag u = i then x u else 0 := by
  simp [coordinatePackets, Matrix.mulVec_diagonal]

/-- Corollary 2.6, actual Kronecker-product block identity. -/
theorem exact_tensor_block (P : PacketFamily (Matrix X X K) I)
    (Q : PacketFamily (Matrix Y Y K) J) (A : Matrix X X K) (B : Matrix Y Y K)
    (b a : I) (d c : J) :
    (Matrix.kronecker (P.proj b) (Q.proj d)) * (Matrix.kronecker A B) *
      (Matrix.kronecker (P.proj a) (Q.proj c)) =
      Matrix.kronecker (P.block A b a) (Q.block B d c) := by
  rw [← Matrix.mul_kronecker_mul, ← Matrix.mul_kronecker_mul]
  rfl

/-- Explicit rectangular right-hand-side version of Theorem 2.3. -/
theorem exact_matrix_batch {C : Type*} (P : PacketFamily (Matrix X X K) I)
    (A : Matrix X X K) (Z : Matrix X C K) :
    A * Z = ∑ e ∈ activeBlocks P A, (P.block A e.1 e.2) * Z := by
  rw [← Matrix.sum_mul]
  exact congrArg (fun a : Matrix X X K => a * Z) (exact_active_evaluation P A).symm
end Matrices

end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.active_iff
#print axioms KomorebiPaperVIII.exact_active_evaluation
#print axioms KomorebiPaperVIII.exact_active_action
#print axioms KomorebiPaperVIII.exact_block_composition
#print axioms KomorebiPaperVIII.product_support_inclusion
#print axioms KomorebiPaperVIII.block_sum
#print axioms KomorebiPaperVIII.all_blocks_zero
#print axioms KomorebiPaperVIII.exact_adjoint_block
#print axioms KomorebiPaperVIII.coordinate_projector_apply
#print axioms KomorebiPaperVIII.exact_tensor_block
#print axioms KomorebiPaperVIII.exact_matrix_batch
#print axioms KomorebiPaperVIII.coordinatePackets
