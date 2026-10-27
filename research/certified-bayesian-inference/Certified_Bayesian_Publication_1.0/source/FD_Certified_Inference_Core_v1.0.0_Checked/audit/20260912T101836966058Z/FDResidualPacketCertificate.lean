import Komorebi.FDMatrixPacketEnergy
import Komorebi.FDResidualEnergyCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix Komorebi.PacketEnergy Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ α β : Type*} [Fintype ι] [Fintype κ] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ]

/-- Independently certified local energy upper bounds control the full residual energy. -/
theorem frobeniusSq_le_packet_majorants
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete) (A : Matrix ι κ ℝ)
    (b : α → β → ℝ) (hb : ∀ a c, frobeniusSq (E.proj a*A*D.proj c) ≤ b a c) :
    frobeniusSq A ≤ ∑ a, ∑ c, b a c := by
  rw [frobeniusSq_eq_sum_packets E D hE hD A]
  exact Finset.sum_le_sum (fun a _ => Finset.sum_le_sum (fun c _ => hb a c))

/-- Actual posterior-distance bound with a sum of nonnegative resolved residual energies.
The explicit residual uses the proposed gain, not the exact gain or exact posterior covariance. -/
theorem posterior_wasserstein2Sq_le_packet_residual_energy
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ : ℝ) (hσ : 0 < σ) (hfloor : QuadraticLowerBound R σ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete) :
    wasserstein2Sq (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal ((∑ a, ∑ c,
        frobeniusSq (E.proj a*gainResidual H P R B*D.proj c)) *
          (σ⁻¹+(σ⁻¹)^2*‖y-matrixCLM H m‖^2)) := by
  rw [← frobeniusSq_eq_sum_packets E D hE hD (gainResidual H P R B)]
  exact posterior_wasserstein2Sq_le_residual_energy H m P R B y hP hR σ hσ hfloor

/-- Square-root-free stopping condition with exact packet energies. -/
theorem posterior_wasserstein2_le_of_packet_tolerance
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ ε : ℝ) (hσ : 0 < σ) (hε : 0 ≤ ε) (hfloor : QuadraticLowerBound R σ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete)
    (hstop : (∑ a, ∑ c, frobeniusSq (E.proj a*gainResidual H P R B*D.proj c)) *
        (σ+‖y-matrixCLM H m‖^2) ≤ ε^2*σ^2) :
    wasserstein2 (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal ε := by
  rw [← frobeniusSq_eq_sum_packets E D hE hD (gainResidual H P R B)] at hstop
  exact posterior_wasserstein2_le_of_residual_tolerance
    H m P R B y hP hR σ ε hσ hε hfloor hstop

/-- Local upper enclosures, not exact local evaluations, suffice for the posterior tolerance.
Obtaining these enclosures by floating-point code is a separate obligation. -/
theorem posterior_wasserstein2_le_of_packet_majorants
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ ε : ℝ) (hσ : 0 < σ) (hε : 0 ≤ ε) (hfloor : QuadraticLowerBound R σ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (hE : E.Complete) (hD : D.Complete) (b : α → β → ℝ)
    (hb : ∀ a c, frobeniusSq (E.proj a*gainResidual H P R B*D.proj c) ≤ b a c)
    (hstop : (∑ a, ∑ c, b a c)*(σ+‖y-matrixCLM H m‖^2) ≤ ε^2*σ^2) :
    wasserstein2 (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal ε := by
  apply posterior_wasserstein2_le_of_residual_tolerance H m P R B y hP hR σ ε hσ hε hfloor
  exact (mul_le_mul_of_nonneg_right
    (frobeniusSq_le_packet_majorants E D hE hD _ b hb)
    (add_nonneg (le_of_lt hσ) (sq_nonneg _))).trans hstop

end Komorebi.FiniteDimensionalGaussianKalman
