module
public import LowRankAlgebra
import all LowRankAlgebra
import all PacketIR
import all QuantumPacketCore
public import ProductChainError
import all ProductChainError

/-!
Author: Komorebi P.
Paper VIII 5.2: explicit factor construction for arbitrary product length,
variable per-factor ranks, including rank zero and the empty product.
The correction-rank bound is actual matrix rank, not only a storage count.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVIII
open scoped BigOperators
open KomorebiPaperVII

/-- Columns are concatenated at every multiplication, without recompression. -/
def ChainColumns (r : ℕ → ℕ) : ℕ → Type
  | 0 => Fin 0
  | n + 1 => ChainColumns r n ⊕ Fin (r n)

instance chainColumnsFintype (r : ℕ → ℕ) : (n : ℕ) → Fintype (ChainColumns r n)
  | 0 => inferInstanceAs (Fintype (Fin 0))
  | n + 1 =>
    letI := chainColumnsFintype r n
    inferInstanceAs (Fintype (ChainColumns r n ⊕ Fin (r n)))

theorem chainColumns_card (r : ℕ → ℕ) (n : ℕ) :
    Fintype.card (ChainColumns r n) = ∑ j ∈ Finset.range n, r j := by
  induction n with
  | zero => simp [ChainColumns]
  | succ n ih =>
    change Fintype.card (ChainColumns r n ⊕ Fin (r n)) = _
    simp only [Fintype.card_sum, Fintype.card_fin, ih, Finset.sum_range_succ]

section FactorConstruction
variable {K X : Type*} [Field K] [StarRing K] [Fintype X] [DecidableEq X]
variable (r : ℕ → ℕ) (D : ℕ → Matrix X X K)
variable (U V : (j : ℕ) → Matrix X (Fin (r j)) K)

/-- The actual pair of thin factors is recursively constructed using the checked two-factor rule. -/
def chainFactors : (n : ℕ) → Matrix X (ChainColumns r n) K × Matrix X (ChainColumns r n) K
  | 0 => (0, 0)
  | n + 1 =>
    let prior := chainFactors n
    (bdlrProductLeft (D n) (U n) (V n) prior.1,
      bdlrProductRight (chainProduct D n) (V n) prior.2)

/-- The constructed factors represent the exact product, not a low-rank approximation. -/
theorem chainFactors_correct (n : ℕ) :
    chainProduct (fun j => D j + U j * (V j).conjTranspose) n =
      chainProduct D n + (chainFactors r D U V n).1 * (chainFactors r D U V n).2.conjTranspose := by
  induction n with
  | zero =>
    ext i j
    simp [chainProduct, chainFactors, Matrix.mul_apply, ChainColumns]
  | succ n ih =>
    rw [chainProduct, ih]
    exact bdlr_product (D n) (chainProduct D n) (U n) (V n)
      (chainFactors r D U V n).1 (chainFactors r D U V n).2

/-- Corollary 5.2: actual matrix rank of the complete correction is bounded additively. -/
theorem bdlr_chain_rank_bound (n : ℕ) :
    (chainProduct (fun j => D j + U j * (V j).conjTranspose) n - chainProduct D n).rank ≤
      ∑ j ∈ Finset.range n, r j := by
  rw [chainFactors_correct, add_sub_cancel_left]
  calc
    _ ≤ (chainFactors r D U V n).1.rank := Matrix.rank_mul_le_left _ _
    _ ≤ Fintype.card (ChainColumns r n) := Matrix.rank_le_card_width _
    _ = _ := chainColumns_card r n
end FactorConstruction

section Diagonal
variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]

theorem packet_diagonal_one (P : PacketFamily R I) : PacketDiagonal P (1 : R) := by
  intro b a hba
  simp [PacketFamily.block, P.mul_proj, hba]

/-- The base part stays packet diagonal at every length, including the identity. -/
theorem packet_diagonal_chain (P : PacketFamily R I) (D : ℕ → R)
    (hD : ∀ j, PacketDiagonal P (D j)) (n : ℕ) : PacketDiagonal P (chainProduct D n) := by
  induction n with
  | zero => exact packet_diagonal_one P
  | succ n ih => exact packet_diagonal_product P (D n) (chainProduct D n) (hD n) ih
end Diagonal
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.chainColumns_card
#print axioms KomorebiPaperVIII.chainFactors_correct
#print axioms KomorebiPaperVIII.bdlr_chain_rank_bound
#print axioms KomorebiPaperVIII.packet_diagonal_one
#print axioms KomorebiPaperVIII.packet_diagonal_chain
#print axioms KomorebiPaperVIII.chainFactors
