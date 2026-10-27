import Komorebi.FDMatrixPacketEnergy
import Komorebi.FDPosteriorFactorCoupling
import Komorebi.QuadraticTransportBounds

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman.FactoredGaussianModel
open Matrix Komorebi.PacketEnergy Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ τ δ α β γ : Type*}
variable [Fintype ι] [Fintype κ] [Fintype τ] [Fintype δ]
variable [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq τ] [DecidableEq δ]

/-- Packet-resolved quadratic cost for the same specified shared-noise coupling.
Output packets resolve the mean; both output and latent packets resolve each factor error. -/
def packetFactorErrorBudget (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets τ β) (F : SelfAdjointPackets δ γ) : ℝ :=
  (∑ a, ‖matrixCLM (E.proj a) (M.meanAt y-M0.meanAt y0)‖^2) +
    (∑ a, ∑ b, frobeniusSq (E.proj a*(M.stateFactor-M0.stateFactor)*D.proj b)) +
    (∑ a, ∑ c, frobeniusSq (E.proj a*(M.obsFactor-M0.obsFactor)*F.proj c))

/-- Complete packet accounting preserves the full chosen-coupling cost exactly. -/
theorem packetFactorErrorBudget_eq (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets τ β) (F : SelfAdjointPackets δ γ)
    (hE : E.Complete) (hD : D.Complete) (hF : F.Complete) :
    M.packetFactorErrorBudget M0 y y0 E D F = M.factorErrorBudget M0 y y0 := by
  unfold packetFactorErrorBudget factorErrorBudget
  rw [← norm_sq_eq_sum_packet_norms E hE (M.meanAt y-M0.meanAt y0),
    ← frobeniusSq_eq_sum_packets E D hE hD (M.stateFactor-M0.stateFactor),
    ← frobeniusSq_eq_sum_packets E F hE hF (M.obsFactor-M0.obsFactor)]

/-- This is equality to the cost of an actual transport plan, not a decomposition of an optimum. -/
theorem factorCoupling_cost_eq_packets (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets τ β) (F : SelfAdjointPackets δ γ)
    (hE : E.Complete) (hD : D.Complete) (hF : F.Complete) :
    quadraticCost (M.factorCoupling M0 y y0) =
      ENNReal.ofReal (M.packetFactorErrorBudget M0 y y0 E D F) := by
  rw [M.packetFactorErrorBudget_eq M0 y y0 E D F hE hD hF]
  exact M.factorCoupling_cost M0 y y0

/-- Packet-energy upper bound on distance between two actual Bayesian posterior versions. -/
theorem posterior_wasserstein2Sq_le_packet_factors (M M0 : FactoredGaussianModel ι κ τ δ)
    (y y0 : EuclideanSpace ℝ κ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets τ β) (F : SelfAdjointPackets δ γ)
    (hE : E.Complete) (hD : D.Complete) (hF : F.Complete) :
    wasserstein2Sq (M.posteriorLaw y) (M0.posteriorLaw y0) ≤
      ENNReal.ofReal (M.packetFactorErrorBudget M0 y y0 E D F) := by
  rw [M.packetFactorErrorBudget_eq M0 y y0 E D F hE hD hF]
  exact M.posterior_wasserstein2Sq_le_factors M0 y y0

/-- Squared packet-energy tolerance implies the requested distribution-distance tolerance. -/
theorem posterior_wasserstein2_le_of_packet_factor_tolerance
    (M M0 : FactoredGaussianModel ι κ τ δ) (y y0 : EuclideanSpace ℝ κ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets τ β) (F : SelfAdjointPackets δ γ)
    (hE : E.Complete) (hD : D.Complete) (hF : F.Complete)
    (ε : ℝ) (hε : 0 ≤ ε)
    (hstop : M.packetFactorErrorBudget M0 y y0 E D F ≤ ε^2) :
    wasserstein2 (M.posteriorLaw y) (M0.posteriorLaw y0) ≤ ENNReal.ofReal ε := by
  apply wasserstein2_le_of_sq_le _ _ ε hε
  exact (M.posterior_wasserstein2Sq_le_packet_factors M0 y y0 E D F hE hD hF).trans
    (ENNReal.ofReal_le_ofReal hstop)

omit [DecidableEq τ] [DecidableEq δ] in
/-- Certified local mean and factor upper bounds can replace exact packet evaluations. -/
theorem packetFactorErrorBudget_le_majorants
    (M M0 : FactoredGaussianModel ι κ τ δ) (y y0 : EuclideanSpace ℝ κ)
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets τ β) (F : SelfAdjointPackets δ γ)
    (bMean : α → ℝ) (bState : α → β → ℝ) (bNoise : α → γ → ℝ)
    (hm : ∀ a, ‖matrixCLM (E.proj a) (M.meanAt y-M0.meanAt y0)‖^2 ≤ bMean a)
    (hs : ∀ a b, frobeniusSq (E.proj a*(M.stateFactor-M0.stateFactor)*D.proj b) ≤ bState a b)
    (hn : ∀ a c, frobeniusSq (E.proj a*(M.obsFactor-M0.obsFactor)*F.proj c) ≤ bNoise a c) :
    M.packetFactorErrorBudget M0 y y0 E D F ≤
      (∑ a, bMean a) + (∑ a, ∑ b, bState a b) + (∑ a, ∑ c, bNoise a c) := by
  apply add_le_add
  · apply add_le_add
    · exact Finset.sum_le_sum (fun a _ => hm a)
    · exact Finset.sum_le_sum (fun a _ => Finset.sum_le_sum (fun b _ => hs a b))
  · exact Finset.sum_le_sum (fun a _ => Finset.sum_le_sum (fun c _ => hn a c))

end Komorebi.FiniteDimensionalGaussianKalman.FactoredGaussianModel
