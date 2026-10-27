import KomorebiVerification.TopologicalCompletion

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperIRelease.PacketEquivalentNorm

open KomorebiVerification.TopologicalCompletion

variable {𝕜 X Y I : Type*} [NontriviallyNormedField 𝕜]
variable [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable [NormedAddCommGroup Y] [NormedSpace 𝕜 Y] [Fintype I]

/-- A linear identification carrying a norm equivalent to the canonical
finite product norm gives the same bounded inverse packet maps. The two
inequalities are exactly the declared norm equivalence, not bounds assumed
for the packet analysis or synthesis maps. -/
def packetEquivOfEquivalentNorm (P : BoundedProjectorFamily 𝕜 X I)
    (e : (∀ i, P.packet i) ≃ₗ[𝕜] Y) (C D : ℝ)
    (hC : ∀ z, ‖e z‖ ≤ C * ‖z‖)
    (hD : ∀ y, ‖e.symm y‖ ≤ D * ‖y‖) : X ≃L[𝕜] Y :=
  P.packetEquiv.trans
    (ContinuousLinearEquiv.equivOfInverse
      (e.toLinearMap.mkContinuous C hC)
      (e.symm.toLinearMap.mkContinuous D hD)
      e.symm_apply_apply e.apply_symm_apply)

/-- Closed packet ranges and bounded, mutually inverse analysis/synthesis
for every finite product norm equivalent to the maximum norm. -/
theorem finite_packet_equivalent_norm (P : BoundedProjectorFamily 𝕜 X I)
    (e : (∀ i, P.packet i) ≃ₗ[𝕜] Y) (C D : ℝ)
    (hC : ∀ z, ‖e z‖ ≤ C * ‖z‖)
    (hD : ∀ y, ‖e.symm y‖ ≤ D * ‖y‖) :
    (∀ i, IsClosed (P.packet i : Set X)) ∧
      ∃ f : X ≃L[𝕜] Y,
        (∀ x, f x = e (P.analysis x)) ∧
        (∀ y, f.symm y = P.synthesis (e.symm y)) := by
  exact ⟨P.isClosed_packet, packetEquivOfEquivalentNorm P e C D hC hD,
    fun _ => rfl, fun _ => rfl⟩

end Komorebi.PaperIRelease.PacketEquivalentNorm
