import H1RestrictionInjective
import RelativePreChebotarevSelector

namespace Komorebi.StrongArtin.CohomologicalRelativePreChebotarev

open Komorebi.StrongArtin.H1RestrictionInjective
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.RelativePreChebotarevSelector

noncomputable section

universe u i c

variable {k G W : Type u} {ι : Type i} {C : Type c}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι] [Monoid C]

/-- **Cohomological relative pre-Chebotarev capstone.** Let `S` be a normal
subgroup with quotient order nonzero in `k`. A nonzero adjoint `H¹` class then
has a nonzero cocycle value on `S`. If `S` lies in both the residual and
cyclotomic kernels, and nonzero values on `S` are genuinely transverse to the
scalar cyclic line, relative spectral detection produces an actual centered
projector and a label-preserving pre-Chebotarev element.

The explicit `htransverse` hypothesis records the remaining interface between
cohomology in `End(W)` and the intended quotient coefficient module
`End(W) / k·1`; it is not silently inferred. -/
theorem exists_preChebotarev_element_from_nonzero_H1_class
    (ρ : Representation k G W)
    (S : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (f : groupCohomology.cocycles₁
      (Rep.of (conjugationRepresentation ρ)))
    (P : ι → Module.End k W) (i0 : ι)
    (cyc : G →* C)
    (g : G)
    (hquot : (Fintype.card (G ⧸ S) : k) ≠ 0)
    (hclass : groupCohomology.H1π
      (Rep.of (conjugationRepresentation ρ)) f ≠ 0)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (hresKernel : ∀ s : S, ρ s = (1 : Module.End k W))
    (hcycKernel : ∀ s : S, cyc s = 1)
    (htransverse : ∀ s : S, f s ≠ 0 →
      f s ∉ k ∙ (1 : Module.End k W))
    (hcycg : cyc g = 1) :
    ∃ i : ι, ∃ γ : G,
      ρ γ = ρ g ∧
      cyc γ = 1 ∧
      projectorTraceProbe (centeredProjector (P i) (P i0)) (f γ) ≠ 0 := by
  obtain ⟨s, hs⟩ :=
    exists_subgroup_element_with_nonzero_cocycle_value
      (Rep.of (conjugationRepresentation ρ)) S hquot f hclass
  obtain ⟨i, γ, _hchoice, hres, hcyc, hdet⟩ :=
    exists_preChebotarev_element_of_relative_detection
      ρ f P i0 cyc s g href hP hoff
      (hresKernel s) (hcycKernel s) hcycg (htransverse s hs)
  exact ⟨i, γ, hres, hcyc, hdet⟩

end
end Komorebi.StrongArtin.CohomologicalRelativePreChebotarev

#print axioms Komorebi.StrongArtin.CohomologicalRelativePreChebotarev.exists_preChebotarev_element_from_nonzero_H1_class
