module
public import PacketIR
import all PacketIR
import all QuantumPacketCore
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.LinearAlgebra.Matrix.Rank
public import Mathlib.Data.Matrix.ColumnRowPartitioned
public import Mathlib.Analysis.CStarAlgebra.Matrix
public import Mathlib.Tactic.Abel

/-!
Author: Komorebi P.
Paper VIII items 5.1 and 5.3: actual rectangular factors and actual matrix inverse.
Woodbury specializes Mathlib's classical identity; no novelty is claimed for it.
The inverse is not used as an invertibility assumption: update invertibility is proved.
-/

public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVIII
open scoped BigOperators
open KomorebiPaperVII

section Diagonal
variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]

/-- Diagonality is an exact vanishing condition, not a numerical threshold. -/
def PacketDiagonal (P : PacketFamily R I) (D : R) : Prop :=
  ∀ b a, b ≠ a → P.block D b a = 0

theorem packet_diagonal_product (P : PacketFamily R I) (D E : R)
    (hD : PacketDiagonal P D) (hE : PacketDiagonal P E) : PacketDiagonal P (D * E) := by
  intro b a hba
  rw [P.compose_blocks]
  apply Finset.sum_eq_zero
  intro c _
  by_cases hb : b = c
  · subst c
    rw [hE b a hba, mul_zero]
  · rw [hD b c hb, zero_mul]
end Diagonal

section Product
variable {K X RA RB : Type*} [Field K] [StarRing K]
variable [Fintype X] [DecidableEq X] [Fintype RA] [Fintype RB]

/-- The first factor has r_B+r_A columns, in the manuscript's displayed order. -/
def bdlrProductLeft (DA : Matrix X X K) (UA VA : Matrix X RA K) (UB : Matrix X RB K) :
    Matrix X (RB ⊕ RA) K := Matrix.fromCols (DA * UB + UA * (VA.conjTranspose * UB)) UA

def bdlrProductRight (DB : Matrix X X K) (VA : Matrix X RA K) (VB : Matrix X RB K) :
    Matrix X (RB ⊕ RA) K := Matrix.fromCols VB (DB.conjTranspose * VA)

/-- Theorem 5.1: multiplication without materializing an unstructured correction. -/
theorem bdlr_product (DA DB : Matrix X X K) (UA VA : Matrix X RA K)
    (UB VB : Matrix X RB K) :
    (DA + UA * VA.conjTranspose) * (DB + UB * VB.conjTranspose) =
      DA * DB + bdlrProductLeft DA UA VA UB * (bdlrProductRight DB VA VB).conjTranspose := by
  simp only [bdlrProductLeft, bdlrProductRight,
    Matrix.conjTranspose_fromCols_eq_fromRows_conjTranspose,
    Matrix.fromCols_mul_fromRows, Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose,
    Matrix.add_mul, Matrix.mul_add, Matrix.mul_assoc]
  abel

/-- The rank statement is actual matrix rank, not only a count of allocated columns. -/
theorem bdlr_product_rank_bound (DA DB : Matrix X X K) (UA VA : Matrix X RA K)
    (UB VB : Matrix X RB K) :
    ((DA + UA * VA.conjTranspose) * (DB + UB * VB.conjTranspose) - DA * DB).rank ≤
      Fintype.card RA + Fintype.card RB := by
  rw [bdlr_product, add_sub_cancel_left]
  calc
    _ ≤ (bdlrProductLeft DA UA VA UB).rank := Matrix.rank_mul_le_left _ _
    _ ≤ Fintype.card (RB ⊕ RA) := Matrix.rank_le_card_width _
    _ = _ := by simp [Nat.add_comm]

/-- An arbitrary batch of right-hand sides uses the two thin factors directly. -/
theorem bdlr_apply {C : Type*} (D : Matrix X X K) (U V : Matrix X RA K) (Z : Matrix X C K) :
    (D + U * V.conjTranspose) * Z = D * Z + U * (V.conjTranspose * Z) := by
  simp only [Matrix.add_mul, Matrix.mul_assoc]
end Product

section Inverse
variable {K X Rk : Type*} [Field K] [StarRing K]
variable [Fintype X] [DecidableEq X] [Fintype Rk] [DecidableEq Rk]

/-- Theorem 5.3: this is the ordinary nonsingular matrix inverse, with both needed hypotheses. -/
theorem bdlr_woodbury (D : Matrix X X K) (U V : Matrix X Rk K)
    (hD : IsUnit D) (hS : IsUnit (1 + V.conjTranspose * D⁻¹ * U)) :
    (D + U * V.conjTranspose)⁻¹ =
      D⁻¹ - D⁻¹ * U * (1 + V.conjTranspose * D⁻¹ * U)⁻¹ * V.conjTranspose * D⁻¹ := by
  simpa using Matrix.add_mul_mul_inv_eq_sub D U (1 : Matrix Rk Rk K)
    V.conjTranspose hD isUnit_one (by simpa using hS)

/-- The update really is invertible. The conclusion is not smuggled in as an assumption. -/
theorem bdlr_update_isUnit (D : Matrix X X K) (U V : Matrix X Rk K)
    (hD : IsUnit D) (hS : IsUnit (1 + V.conjTranspose * D⁻¹ * U)) :
    IsUnit (D + U * V.conjTranspose) := by
  classical
  obtain ⟨_⟩ := hD.nonempty_invertible
  have hs : IsUnit (⅟(1 : Matrix Rk Rk K) + V.conjTranspose * ⅟D * U) := by
    simpa only [invOf_one, Matrix.invOf_eq_nonsing_inv] using hS
  obtain ⟨_⟩ := hs.nonempty_invertible
  letI := Matrix.invertibleAddMulMul D U (1 : Matrix Rk Rk K) V.conjTranspose
  simpa using (isUnit_of_invertible (D + U * (1 : Matrix Rk Rk K) * V.conjTranspose))

/-- The proposed inverse solves the actual updated system, for every batch Z. -/
theorem bdlr_woodbury_solve {C : Type*} (D : Matrix X X K) (U V : Matrix X Rk K)
    (hD : IsUnit D) (hS : IsUnit (1 + V.conjTranspose * D⁻¹ * U)) (Z : Matrix X C K) :
    (D + U * V.conjTranspose) *
      ((D⁻¹ - D⁻¹ * U * (1 + V.conjTranspose * D⁻¹ * U)⁻¹ * V.conjTranspose * D⁻¹) * Z) = Z := by
  rw [← bdlr_woodbury D U V hD hS, ← Matrix.mul_assoc]
  have hu := bdlr_update_isUnit D U V hD hS
  rw [Matrix.mul_nonsing_inv _ ((Matrix.isUnit_iff_isUnit_det _).mp hu), Matrix.one_mul]
end Inverse


section InverseNorm
open scoped Matrix.Norms.L2Operator
variable {K X Rk : Type*} [RCLike K]
variable [Fintype X] [DecidableEq X] [Fintype Rk] [DecidableEq Rk]

/-- Corollary 5.4 in the Hilbert-space operator norm, including rectangular thin factors. -/
theorem bdlr_inverse_norm_bound (D : Matrix X X K) (U V : Matrix X Rk K)
    (hD : IsUnit D) (hS : IsUnit (1 + V.conjTranspose * D⁻¹ * U)) :
    ‖(D + U * V.conjTranspose)⁻¹‖ ≤ ‖D⁻¹‖ + ‖D⁻¹ * U‖ *
      ‖(1 + V.conjTranspose * D⁻¹ * U)⁻¹‖ * ‖V.conjTranspose * D⁻¹‖ := by
  rw [bdlr_woodbury D U V hD hS]
  have hfactor : D⁻¹ * U * (1 + V.conjTranspose * D⁻¹ * U)⁻¹ * V.conjTranspose * D⁻¹ =
      (D⁻¹ * U) * (1 + V.conjTranspose * D⁻¹ * U)⁻¹ * (V.conjTranspose * D⁻¹) := by
    simp only [Matrix.mul_assoc]
  rw [hfactor]
  apply (norm_sub_le _ _).trans
  apply add_le_add_left
  exact (Matrix.l2_opNorm_mul _ _).trans
    (mul_le_mul_of_nonneg_right (Matrix.l2_opNorm_mul _ _) (norm_nonneg _))
end InverseNorm

end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.packet_diagonal_product
#print axioms KomorebiPaperVIII.bdlr_product
#print axioms KomorebiPaperVIII.bdlr_product_rank_bound
#print axioms KomorebiPaperVIII.bdlr_apply
#print axioms KomorebiPaperVIII.bdlr_woodbury
#print axioms KomorebiPaperVIII.bdlr_update_isUnit
#print axioms KomorebiPaperVIII.bdlr_woodbury_solve

#print axioms KomorebiPaperVIII.bdlr_inverse_norm_bound
