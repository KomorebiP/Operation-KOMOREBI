import Komorebi.PacketCoarsening
import Komorebi.FDMatrixEnergyBounds

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix Komorebi.PacketEnergy

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

/-- The independent packet geometry uses exactly the previously certified Frobenius normalization. -/
theorem matrixEnergy_eq_frobeniusSq (A : Matrix ι κ ℝ) : matrixEnergy A = frobeniusSq A := rfl

/-- Explicit coordinate vector energy is the genuine squared Euclidean norm. -/
theorem vectorEnergy_eq_norm_sq (v : EuclideanSpace ℝ ι) :
    vectorEnergy (fun i => v i) = ‖v‖^2 := by
  exact (EuclideanSpace.real_norm_sq_eq v).symm

/-- Mean errors decompose across a complete self-adjoint output resolution. -/
theorem norm_sq_eq_sum_packet_norms {α : Type*} [Fintype α] [DecidableEq ι]
    (E : SelfAdjointPackets ι α) (hE : E.Complete) (v : EuclideanSpace ℝ ι) :
    ‖v‖^2 = ∑ a, ‖matrixCLM (E.proj a) v‖^2 := by
  have h := vectorEnergy_eq_sum_packets E hE (fun i => v i)
  simpa only [← vectorEnergy_eq_norm_sq, matrixCLM_apply] using h

/-- Rectangular residuals and factor errors obey a square-sum, not an operator-norm sum. -/
theorem frobeniusSq_eq_sum_packets {α β : Type*} [Fintype α] [Fintype β]
    [DecidableEq ι] [DecidableEq κ]
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete) (A : Matrix ι κ ℝ) :
    frobeniusSq A = ∑ a, ∑ b, frobeniusSq (E.proj a * A * D.proj b) := by
  exact matrixEnergy_eq_sum_blocks E D hE hD A

/-- Exact local parent-to-descendant energy for the existing Frobenius convention. -/
theorem frobeniusSq_parent_eq_descendants {α β γ δ : Type*}
    [Fintype γ] [Fintype δ] [DecidableEq α] [DecidableEq β]
    (C : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (E : SelfAdjointPackets ι γ) (F : SelfAdjointPackets κ δ)
    (ρ : γ → α) (τ : δ → β) (hE : PacketRefines C E ρ) (hF : PacketRefines D F τ)
    (A : Matrix ι κ ℝ) (a : α) (b : β) :
    frobeniusSq (C.proj a*A*D.proj b) =
      ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ∑ d ∈ Finset.univ.filter (fun d => τ d = b),
          frobeniusSq (E.proj c*A*F.proj d) := by
  exact parent_energy_eq_descendants C D E F ρ τ hE hF A a b

end Komorebi.FiniteDimensionalGaussianKalman
