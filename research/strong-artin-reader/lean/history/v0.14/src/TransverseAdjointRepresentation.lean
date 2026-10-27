import RelativePreChebotarevSelector

namespace Komorebi.StrongArtin.TransverseAdjointRepresentation

open Komorebi.StrongArtin.ProjectorProbeSurjectivity
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone

noncomputable section

universe u i

variable {k G W : Type u} {ι : Type i}
  [Field k] [Group G]
  [AddCommGroup W] [Module k W]

/-- The scalar/cyclic line in the adjoint endomorphism space. -/
abbrev scalarLine : Submodule k (Module.End k W) :=
  k ∙ (1 : Module.End k W)

/-- Conjugation preserves the scalar line. -/
theorem scalarLine_invariant (ρ : Representation k G W) :
    ∀ g : G, scalarLine (k := k) (W := W) ≤
      (scalarLine (k := k) (W := W)).comap (conjugationRepresentation ρ g) := by
  intro g X hX
  rw [Submodule.mem_comap]
  rw [Submodule.mem_span_singleton] at hX ⊢
  rcases hX with ⟨a, rfl⟩
  refine ⟨a, ?_⟩
  ext x
  simp [conjugationRepresentation_apply, Representation.self_inv_apply]

/-- The adjoint representation modulo the retained scalar/cyclic line. -/
abbrev transverseAdjointRep (ρ : Representation k G W) : Rep.{u} k G :=
  (Rep.of (conjugationRepresentation ρ)).quotient
    (scalarLine (k := k) (W := W)) (scalarLine_invariant ρ)

/-- A residual-kernel element acts trivially on the transverse adjoint quotient. -/
theorem transverseAdjoint_action_eq_one_of_residual_eq_one
    (ρ : Representation k G W) (σ : G)
    (hρσ : ρ σ = (1 : Module.End k W)) :
    (transverseAdjointRep ρ).ρ σ = 1 := by
  change (conjugationRepresentation ρ).quotient
      (scalarLine (k := k) (W := W)) (scalarLine_invariant ρ) σ = 1
  rw [Representation.quotient_apply]
  apply LinearMap.ext
  intro q
  rcases (scalarLine (k := k) (W := W)).mkQ_surjective q with ⟨X, rfl⟩
  rw [Submodule.mkQ_apply, Submodule.mapQ_apply]
  have hinv : ρ σ⁻¹ = (1 : Module.End k W) := by
    ext x
    have h := Representation.inv_self_apply ρ σ x
    rw [hρσ] at h
    simpa using h
  simp [hρσ, hinv, conjugationRepresentation_apply]


end
end Komorebi.StrongArtin.TransverseAdjointRepresentation

#print axioms Komorebi.StrongArtin.TransverseAdjointRepresentation.scalarLine_invariant
#print axioms Komorebi.StrongArtin.TransverseAdjointRepresentation.transverseAdjoint_action_eq_one_of_residual_eq_one
