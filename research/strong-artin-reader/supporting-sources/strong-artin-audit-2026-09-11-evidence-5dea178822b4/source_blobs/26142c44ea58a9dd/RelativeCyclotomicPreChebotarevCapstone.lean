import CommonKernelCocycleSurvival
import RelativeFiniteQuotientPreChebotarev

namespace Komorebi.StrongArtin.RelativeCyclotomicPreChebotarevCapstone

open Komorebi.StrongArtin.FiniteGroupCocycleAveraging
open Komorebi.StrongArtin.FiniteQuotientCocycleDescent
open Komorebi.StrongArtin.CommonKernelCocycleSurvival
open Komorebi.StrongArtin.RepresentationCocycleFiberSelector
open Komorebi.StrongArtin.RelativePreChebotarevCapstone
open Komorebi.StrongArtin.RelativeFiniteQuotientPreChebotarev
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.FiniteProjectorProbeExtraction
open Komorebi.StrongArtin.ConjugationQuotientNoInvariants

noncomputable section

variable {k Γ W ι Gal C : Type*}
  [Field k] [Group Γ] [Fintype Γ]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction Γ ι]
  [Group Gal] [CommGroup C]

/-- **Relative cyclotomic pre-Chebotarev capstone.** A nontrivial transverse
cocycle class yields a nonzero value in the common residual/cyclotomic kernel.
Relative spectral detection chooses an actual centered projector, and one of
`g` or `sigma * g` has the prescribed residual image, remains cyclotomic
trivial, and is detected nontrivially.

Thus, under the stated finite-image and no-invariants hypotheses, the next
unproved implication is precisely Chebotarev realization of the selected finite
conjugacy datum (together with the local Taylor--Wiles pairing interpretation). -/
theorem exists_projector_and_cyclotomic_preChebotarev_element
    (ρ : Representation k Γ W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (ρGal : Representation k Gal
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (res : Gal →* Γ) (hresSurj : Function.Surjective res)
    (chi : Gal →* C)
    (haction : ∀ g : Gal,
      ρGal g = transverseConjugationRepresentation ρ (res g))
    (hnoinv : ∀ x : Module.End k W ⧸ (k ∙ (1 : Module.End k W)),
      (∀ a : Γ, transverseConjugationRepresentation ρ a x = x) → x = 0)
    (f : Gal → (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (hf : IsRepresentationCocycle ρGal f)
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (hnontrivial : ¬ IsRepresentationCoboundary ρGal f)
    (g : Gal) (hchiG : chi g = 1) :
    ∃ i : ι, ∃ sigma gamma : Gal,
      res sigma = 1 ∧
      chi sigma = 1 ∧
      f sigma ≠ 0 ∧
      (gamma = g ∨ gamma = sigma * g) ∧
      res gamma = res g ∧
      chi gamma = 1 ∧
      centeredQuotientProjectorProbe P i0 href i (f gamma) ≠ 0 := by
  obtain ⟨sigma, hresSigma, hchiSigma, hfsigma⟩ :=
    exists_nonzero_value_in_common_kernel
      ρGal (transverseConjugationRepresentation ρ)
      res hresSurj chi haction hnoinv f hf hcard hnontrivial
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
  have hchiGamma : chi gamma = 1 := by
    rcases hchoice with rfl | rfl
    · exact hchiG
    · simp [hchiSigma, hchiG]
  exact ⟨i, sigma, gamma, hresSigma, hchiSigma, hfsigma,
    hchoice, hresGamma, hchiGamma, hprobe⟩

/-- In the algebraically closed irreducible prime-to-characteristic regime,
the no-invariants hypothesis in the preceding capstone is automatic by Schur's
lemma and normalized averaging. -/
theorem exists_projector_and_cyclotomic_preChebotarev_element_of_irreducible
    [IsAlgClosed k]
    (ρ : Representation k Γ W) [ρ.IsIrreducible]
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (ρGal : Representation k Gal
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (res : Gal →* Γ) (hresSurj : Function.Surjective res)
    (chi : Gal →* C)
    (haction : ∀ g : Gal,
      ρGal g = transverseConjugationRepresentation ρ (res g))
    (f : Gal → (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))
    (hf : IsRepresentationCocycle ρGal f)
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (hnontrivial : ¬ IsRepresentationCoboundary ρGal f)
    (g : Gal) (hchiG : chi g = 1) :
    ∃ i : ι, ∃ sigma gamma : Gal,
      res sigma = 1 ∧
      chi sigma = 1 ∧
      f sigma ≠ 0 ∧
      (gamma = g ∨ gamma = sigma * g) ∧
      res gamma = res g ∧
      chi gamma = 1 ∧
      centeredQuotientProjectorProbe P i0 href i (f gamma) ≠ 0 := by
  apply exists_projector_and_cyclotomic_preChebotarev_element
    ρ P i0 href hP hoff ρGal res hresSurj chi haction
  · exact quotient_by_scalars_has_no_invariants ρ hcard
  · exact hf
  · exact hcard
  · exact hnontrivial
  · exact hchiG

end

end Komorebi.StrongArtin.RelativeCyclotomicPreChebotarevCapstone
