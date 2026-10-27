import RelativeAdequacyProjectorCapstone
import CocycleFiberSelector

namespace Komorebi.StrongArtin.RelativePreChebotarevCapstone

open Komorebi.StrongArtin.CocycleFiberSelector
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.FiniteProjectorProbeExtraction

noncomputable section

variable {k Γ W ι Gal R C : Type*}
  [Field k] [Group Γ] [Fintype Γ]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction Γ ι]
  [Group Gal]
  [DistribMulAction Gal
    (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))]
  [Group R] [Group C]

/-- Relative spectral detection supplies a pointwise detector for every nonzero
transverse coefficient vector. -/
theorem exists_centered_projector_probe_of_ne_zero
    (ρ : Representation k Γ W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (x : Module.End k W ⧸ (k ∙ (1 : Module.End k W)))
    (hx : x ≠ 0) :
    ∃ i : ι, centeredQuotientProjectorProbe P i0 href i x ≠ 0 := by
  have hsep :=
    centeredQuotientProjectorProbe_separates ρ P i0 href hP
      (spectralProjectorDetectsEverySimplePacket_of_offScalar ρ P i0 href hoff)
  by_contra hnone
  have hall : ∀ i : ι, centeredQuotientProjectorProbe P i0 href i x = 0 := by
    intro i
    by_contra hi
    exact hnone ⟨i, hi⟩
  exact hx (hsep x hall)

/-- **Relative pre-Chebotarev capstone.** Suppose a transverse cocycle survives
at an element `sigma` in the common kernels of the residual and cyclotomic
finite quotients. Relative spectral detection then chooses an actual centered
projector probe, and the two-candidate selector chooses `g` or `sigma * g`,
preserving both finite images while making that probe nonzero.

The remaining arithmetic step is exactly Chebotarev realization of the selected
finite conjugacy datum; it is not asserted here. -/
theorem exists_actual_projector_and_same_fiber_element
    (ρ : Representation k Γ W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (f : Gal → (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (hf : IsOneCocycle f)
    (res : Gal →* R) (chi : Gal →* C)
    (sigma g : Gal)
    (hfixed : ∀ x : Module.End k W ⧸ (k ∙ (1 : Module.End k W)),
      sigma • x = x)
    (hres : res sigma = 1)
    (hchiSigma : chi sigma = 1)
    (hchiG : chi g = 1)
    (hsigma : f sigma ≠ 0) :
    ∃ i : ι, ∃ gamma : Gal,
      (gamma = g ∨ gamma = sigma * g) ∧
      res gamma = res g ∧
      chi gamma = 1 ∧
      centeredQuotientProjectorProbe P i0 href i (f gamma) ≠ 0 := by
  have hsep : ∀ x : Module.End k W ⧸ (k ∙ (1 : Module.End k W)),
      x ≠ 0 → ∃ i : ι,
        centeredQuotientProjectorProbe P i0 href i x ≠ 0 := by
    intro x hx
    exact exists_centered_projector_probe_of_ne_zero
      ρ P i0 href hP hoff x hx
  exact exists_probe_and_detecting_in_character_kernel
    f hf (centeredQuotientProjectorProbe P i0 href) hsep
      res chi sigma g hfixed hres hchiSigma hchiG hsigma

end

end Komorebi.StrongArtin.RelativePreChebotarevCapstone
