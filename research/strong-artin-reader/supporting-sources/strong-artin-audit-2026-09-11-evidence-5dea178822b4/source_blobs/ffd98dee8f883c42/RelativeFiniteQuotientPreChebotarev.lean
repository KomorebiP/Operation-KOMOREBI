import RelativePreChebotarevCapstone
import FiniteQuotientCocycleDescent
import RepresentationCocycleFiberSelector
import ConjugationQuotientNoInvariants

namespace Komorebi.StrongArtin.RelativeFiniteQuotientPreChebotarev

open Komorebi.StrongArtin.FiniteGroupCocycleAveraging
open Komorebi.StrongArtin.FiniteQuotientCocycleDescent
open Komorebi.StrongArtin.RepresentationCocycleFiberSelector
open Komorebi.StrongArtin.RelativePreChebotarevCapstone
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.FiniteProjectorProbeExtraction
open Komorebi.StrongArtin.ConjugationQuotientNoInvariants

noncomputable section

variable {k Γ W ι Gal : Type*}
  [Field k] [Group Γ] [Fintype Γ]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction Γ ι]
  [Group Gal]

/-- The conjugation representation on endomorphisms modulo the scalar line. -/
def transverseConjugationRepresentation
    (ρ : Representation k Γ W) :
    Representation k Γ
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W))) :=
  (conjugationRepresentation ρ).quotient
    (k ∙ (1 : Module.End k W)) (scalarLine_stable ρ)

/-- **Finite-quotient pre-Chebotarev capstone.** Work inside an ambient Galois
group already cut down to the required cyclotomic level. Suppose its action on
the transverse adjoint module factors through a finite quotient `Γ` whose order
is invertible in `k`. A nontrivial cocycle class then has a nonzero value in the
residual kernel. Relative spectral detection selects an actual centered
projector, and one of `g` or `sigma * g` preserves the prescribed residual image
while giving nonzero local evaluation.

The only subsequent arithmetic step is Chebotarev realization of this finite
conjugacy datum. -/
theorem exists_projector_and_preChebotarev_element_of_nontrivial_class
    (ρ : Representation k Γ W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (ρGal : Representation k Gal
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (res : Gal →* Γ) (hresSurj : Function.Surjective res)
    (haction : ∀ g : Gal,
      ρGal g = transverseConjugationRepresentation ρ (res g))
    (f : Gal → (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (hf : IsRepresentationCocycle ρGal f)
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (hnontrivial : ¬ IsRepresentationCoboundary ρGal f)
    (g : Gal) :
    ∃ i : ι, ∃ sigma gamma : Gal,
      res sigma = 1 ∧
      f sigma ≠ 0 ∧
      (gamma = g ∨ gamma = sigma * g) ∧
      res gamma = res g ∧
      centeredQuotientProjectorProbe P i0 href i (f gamma) ≠ 0 := by
  obtain ⟨sigma, hresSigma, hfsigma⟩ :=
    exists_nonzero_value_in_quotient_kernel
      ρGal (transverseConjugationRepresentation ρ)
      res hresSurj haction f hf hcard hnontrivial
  have hactionSigma : ρGal sigma = 1 := by
    rw [haction sigma, hresSigma]
    exact map_one (transverseConjugationRepresentation ρ)
  have hsep :
      ∀ x : Module.End k W ⧸ (k ∙ (1 : Module.End k W)),
        x ≠ 0 → ∃ i : ι,
          centeredQuotientProjectorProbe P i0 href i x ≠ 0 := by
    intro x hx
    exact exists_centered_projector_probe_of_ne_zero
      ρ P i0 href hP hoff x hx
  obtain ⟨i, gamma, hchoice, hresGamma, hprobe⟩ :=
    exists_probe_and_detecting_same_quotient_fiber
      ρGal f hf (centeredQuotientProjectorProbe P i0 href) hsep
      res sigma g hactionSigma hresSigma hfsigma
  exact ⟨i, sigma, gamma, hresSigma, hfsigma,
    hchoice, hresGamma, hprobe⟩

end

end Komorebi.StrongArtin.RelativeFiniteQuotientPreChebotarev
