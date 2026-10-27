import Komorebi.SelfAdjointPackets

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix SelfAdjointPackets

variable {ι κ α β : Type*} [Fintype ι] [Fintype κ]

/-- Exact energy of any finite orthogonal output-packet sum; completeness is not needed. -/
theorem matrixEnergy_sumOn_left (E : SelfAdjointPackets ι α) (s : Finset α)
    (A : Matrix ι κ ℝ) :
    matrixEnergy (E.sumOn s * A) = ∑ a ∈ s, matrixEnergy (E.proj a * A) := by
  calc
    _ = (A.transpose * E.sumOn s * A).trace :=
      matrixEnergy_left_projector _ A (E.sumOn_transpose s) (E.sumOn_idempotent s)
    _ = ∑ a ∈ s, (A.transpose * E.proj a * A).trace := by
      simp only [SelfAdjointPackets.sumOn, Matrix.mul_sum, Matrix.sum_mul, Matrix.trace_sum]
    _ = _ := by
      apply Finset.sum_congr rfl
      intro a _
      exact (matrixEnergy_left_projector _ A (E.symmetric a) (E.idempotent a)).symm

/-- Input-packet version obtained by transpose, with its own self-adjoint geometry. -/
theorem matrixEnergy_sumOn_right (D : SelfAdjointPackets κ β) (t : Finset β)
    (A : Matrix ι κ ℝ) :
    matrixEnergy (A * D.sumOn t) = ∑ b ∈ t, matrixEnergy (A * D.proj b) := by
  calc
    _ = matrixEnergy (D.sumOn t * A.transpose) := by
      rw [← matrixEnergy_transpose (A*D.sumOn t), Matrix.transpose_mul, D.sumOn_transpose]
    _ = ∑ b ∈ t, matrixEnergy (D.proj b * A.transpose) :=
      matrixEnergy_sumOn_left D t A.transpose
    _ = _ := by
      apply Finset.sum_congr rfl
      intro b _
      rw [← matrixEnergy_transpose (A*D.proj b), Matrix.transpose_mul, D.symmetric]

/-- Exact rectangular parent energy is the sum of its two-sided descendant energies. -/
theorem matrixEnergy_sumOn_both (E : SelfAdjointPackets ι α)
    (D : SelfAdjointPackets κ β) (s : Finset α) (t : Finset β) (A : Matrix ι κ ℝ) :
    matrixEnergy (E.sumOn s * A * D.sumOn t) =
      ∑ a ∈ s, ∑ b ∈ t, matrixEnergy (E.proj a * A * D.proj b) := by
  rw [Matrix.mul_assoc, matrixEnergy_sumOn_left]
  apply Finset.sum_congr rfl
  intro a _
  rw [← Matrix.mul_assoc, matrixEnergy_sumOn_right]

/-- Completeness on both spaces accounts for the entire residual energy. -/
theorem matrixEnergy_eq_sum_blocks [Fintype α] [Fintype β]
    [DecidableEq ι] [DecidableEq κ]
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete) (A : Matrix ι κ ℝ) :
    matrixEnergy A = ∑ a, ∑ b, matrixEnergy (E.proj a * A * D.proj b) := by
  have h := matrixEnergy_sumOn_both E D Finset.univ Finset.univ A
  simpa only [hE, hD, Matrix.one_mul, Matrix.mul_one] using h

/-- Partial accounting cannot exceed the whole energy of the same fixed residual. -/
theorem sum_block_energies_le [Fintype α] [Fintype β]
    [DecidableEq ι] [DecidableEq κ]
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete) (s : Finset α) (t : Finset β)
    (A : Matrix ι κ ℝ) :
    (∑ a ∈ s, ∑ b ∈ t, matrixEnergy (E.proj a*A*D.proj b)) ≤ matrixEnergy A := by
  rw [matrixEnergy_eq_sum_blocks E D hE hD A]
  apply (Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ s)
    (fun a _ _ => Finset.sum_nonneg (fun b _ => matrixEnergy_nonneg _))).trans
  apply Finset.sum_le_sum
  intro a _
  exact Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ t)
    (fun b _ _ => matrixEnergy_nonneg _)

end Komorebi.PacketEnergy
