import ProjectorPreChebotarevSelector
import RelativeAdequacyProjectorCapstone

namespace Komorebi.StrongArtin.RelativePreChebotarevSelector

open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone
open Komorebi.StrongArtin.ProjectorPreChebotarevSelector

noncomputable section

universe u w i c

variable {k G : Type u} {W : Type w} {ι : Type i} {C : Type c}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι] [Monoid C]

/-- **Relative spectral pre-Chebotarev selector.** Assume the actual projector
family is conjugation-covariant, detects every simple conjugation packet outside
the scalar cyclic line, and contains one nonzero-trace reference projector.
Then every nonscalar value of an adjoint one-cocycle on a residual-kernel,
cyclotomically trivial element produces an actual centered projector and a
choice `γ = g` or `γ = σ * g` which simultaneously:

* has the prescribed residual matrix `ρ g`;
* remains trivial under the cyclotomic label;
* has nonzero centered projector-trace cocycle evaluation.

No Chebotarev theorem, local Tate-duality identification, or global Selmer
statement is asserted here. This theorem closes the finite algebraic element-
selection implication between relative spectral detection and those external
arithmetic steps. -/
theorem exists_preChebotarev_element_of_relative_detection
    (ρ : Representation k G W)
    (f : groupCohomology.cocycles₁
      (Rep.of (conjugationRepresentation ρ)))
    (P : ι → Module.End k W) (i0 : ι)
    (cyc : G →* C)
    (σ g : G)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (hρσ : ρ σ = (1 : Module.End k W))
    (hcycσ : cyc σ = 1)
    (hcycg : cyc g = 1)
    (hnonscalar : f σ ∉ k ∙ (1 : Module.End k W)) :
    ∃ i : ι, ∃ γ : G,
      (γ = g ∨ γ = σ * g) ∧
      ρ γ = ρ g ∧
      cyc γ = 1 ∧
      projectorTraceProbe (centeredProjector (P i) (P i0)) (f γ) ≠ 0 := by
  have hsep : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0 :=
    raw_separation_of_relative_spectral_detection ρ P i0 href hP hoff
  exact exists_centered_projector_and_label_preserving_detected_element
    ρ f P i0 cyc σ g href hsep hρσ hcycσ hcycg hnonscalar

end
end Komorebi.StrongArtin.RelativePreChebotarevSelector

#print axioms Komorebi.StrongArtin.RelativePreChebotarevSelector.exists_preChebotarev_element_of_relative_detection
