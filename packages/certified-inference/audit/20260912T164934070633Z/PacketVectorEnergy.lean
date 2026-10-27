import Komorebi.PacketEnergyDecomposition

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix SelfAdjointPackets

variable {ι : Type*} [Fintype ι]

/-- Squared Euclidean energy, expressed without choosing a norm instance on functions. -/
def vectorEnergy (v : ι → ℝ) : ℝ := ∑ i, (v i)^2

theorem vectorEnergy_nonneg (v : ι → ℝ) : 0 ≤ vectorEnergy v := by
  exact Finset.sum_nonneg (fun i _ => sq_nonneg (v i))

/-- Column embedding identifies vector energy with rectangular matrix energy. -/
theorem matrixEnergy_column (v : ι → ℝ) :
    matrixEnergy (Matrix.replicateCol Unit v) = vectorEnergy v := by
  simp [matrixEnergy, vectorEnergy]

theorem mul_column (P : Matrix ι ι ℝ) (v : ι → ℝ) :
    P * Matrix.replicateCol Unit v = Matrix.replicateCol Unit (P *ᵥ v) := by
  ext i j
  rfl

theorem vectorEnergy_sumOn {α : Type*} (E : SelfAdjointPackets ι α) (s : Finset α)
    (v : ι → ℝ) :
    vectorEnergy (E.sumOn s *ᵥ v) = ∑ a ∈ s, vectorEnergy (E.proj a *ᵥ v) := by
  have h := matrixEnergy_sumOn_left E s (Matrix.replicateCol Unit v)
  simpa only [mul_column, matrixEnergy_column] using h

theorem vectorEnergy_eq_sum_packets {α : Type*} [Fintype α] [DecidableEq ι]
    (E : SelfAdjointPackets ι α) (hE : E.Complete) (v : ι → ℝ) :
    vectorEnergy v = ∑ a, vectorEnergy (E.proj a *ᵥ v) := by
  unfold SelfAdjointPackets.Complete at hE
  simpa only [hE, Matrix.one_mulVec] using vectorEnergy_sumOn E Finset.univ v

end Komorebi.PacketEnergy
