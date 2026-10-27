import PreChebotarevSelector
import ConjugationProjectorProbes

namespace Komorebi.StrongArtin.ProjectorPreChebotarevSelector

open Komorebi.StrongArtin.PreChebotarevSelector
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ConjugationProjectorProbes

noncomputable section

universe u w c

variable {k G : Type u} {W : Type w} {C : Type c}
  [Field k] [Group G]
  [AddCommGroup W] [Module k W]
  [Monoid C]

/-- An element acting trivially in the residual representation also acts
trivially on the adjoint/conjugation coefficient representation. -/
theorem conjugation_action_eq_one_of_residual_eq_one
    (ρ : Representation k G W) (σ : G)
    (hσ : ρ σ = (1 : Module.End k W)) :
    conjugationRepresentation ρ σ = 1 := by
  have hinv : ρ σ⁻¹ = (1 : Module.End k W) := by
    ext x
    have h := Representation.inv_self_apply ρ σ x
    rw [hσ] at h
    simpa using h
  ext X x
  simp [conjugationRepresentation_apply, hσ, hinv]

/-- **Projector-valued pre-Chebotarev selector.** Let `f` be a one-cocycle with
coefficients in the adjoint representation. If an element `σ` lies in the
residual kernel, is cyclotomically trivial, and its cocycle value is detected
by the trace probe associated with an actual endomorphism `P`, then for any
prescribed residual element `g` with trivial cyclotomic label there is a choice
`γ = g` or `γ = σ * g` which has:

* the same residual matrix as `g`;
* trivial cyclotomic label;
* nonzero projector-trace evaluation on `f γ`.

This is the exact algebraic element-selection step needed immediately before a
Chebotarev realization argument. -/
theorem exists_same_residual_cyclotomic_trivial_projector_detected
    (ρ : Representation k G W)
    (f : groupCohomology.cocycles₁
      (Rep.of (conjugationRepresentation ρ)))
    (P : Module.End k W)
    (cyc : G →* C)
    (σ g : G)
    (hρσ : ρ σ = (1 : Module.End k W))
    (hcycσ : cyc σ = 1)
    (hcycg : cyc g = 1)
    (hdetect : projectorTraceProbe P (f σ) ≠ 0) :
    ∃ γ : G,
      (γ = g ∨ γ = σ * g) ∧
      ρ γ = ρ g ∧
      cyc γ = 1 ∧
      projectorTraceProbe P (f γ) ≠ 0 := by
  apply exists_label_preserving_detected_element
    (A := Rep.of (conjugationRepresentation ρ))
    f (projectorTraceProbe P) ρ cyc σ g
  · exact conjugation_action_eq_one_of_residual_eq_one ρ σ hρσ
  · exact hρσ
  · exact hcycσ
  · exact hcycg
  · exact hdetect


/-- A cocycle value outside the scalar defect line is detected by at least one
centered actual-projector trace whenever the raw projector traces separate all
endomorphisms. -/
theorem exists_centered_projector_detecting_nonscalar_value
    {ι : Type*}
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hsep : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0)
    (X : Module.End k W)
    (hX : X ∉ k ∙ (1 : Module.End k W)) :
    ∃ i : ι,
      projectorTraceProbe (centeredProjector (P i) (P i0)) X ≠ 0 := by
  by_contra h
  push Not at h
  have hm : X ∈ {Y : Module.End k W |
      ∀ i : ι,
        projectorTraceProbe (centeredProjector (P i) (P i0)) Y = 0} := h
  rw [centeredProjectorProbes_joint_kernel_eq_scalarLine P i0 href hsep] at hm
  exact hX hm

/-- **Relative pre-Chebotarev projector selector.** Raw projector separation and
one nonzero-trace reference projector turn any nonscalar cocycle value on a
residual-kernel element into a label-preserving detected element. The selected
probe is an actual centered projector trace, so it is already transverse to the
scalar cyclic defect. -/
theorem exists_centered_projector_and_label_preserving_detected_element
    {ι : Type*}
    (ρ : Representation k G W)
    (f : groupCohomology.cocycles₁
      (Rep.of (conjugationRepresentation ρ)))
    (P : ι → Module.End k W) (i0 : ι)
    (cyc : G →* C)
    (σ g : G)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hsep : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0)
    (hρσ : ρ σ = (1 : Module.End k W))
    (hcycσ : cyc σ = 1)
    (hcycg : cyc g = 1)
    (hnonscalar : f σ ∉ k ∙ (1 : Module.End k W)) :
    ∃ i : ι, ∃ γ : G,
      (γ = g ∨ γ = σ * g) ∧
      ρ γ = ρ g ∧
      cyc γ = 1 ∧
      projectorTraceProbe (centeredProjector (P i) (P i0)) (f γ) ≠ 0 := by
  obtain ⟨i, hi⟩ :=
    exists_centered_projector_detecting_nonscalar_value P i0 href hsep (f σ) hnonscalar
  obtain ⟨γ, hchoice, hres, hcyc, hdet⟩ :=
    exists_same_residual_cyclotomic_trivial_projector_detected
      ρ f (centeredProjector (P i) (P i0)) cyc σ g hρσ hcycσ hcycg hi
  exact ⟨i, γ, hchoice, hres, hcyc, hdet⟩

end
end Komorebi.StrongArtin.ProjectorPreChebotarevSelector

#print axioms Komorebi.StrongArtin.ProjectorPreChebotarevSelector.conjugation_action_eq_one_of_residual_eq_one
#print axioms Komorebi.StrongArtin.ProjectorPreChebotarevSelector.exists_same_residual_cyclotomic_trivial_projector_detected
#print axioms Komorebi.StrongArtin.ProjectorPreChebotarevSelector.exists_centered_projector_detecting_nonscalar_value
#print axioms Komorebi.StrongArtin.ProjectorPreChebotarevSelector.exists_centered_projector_and_label_preserving_detected_element
