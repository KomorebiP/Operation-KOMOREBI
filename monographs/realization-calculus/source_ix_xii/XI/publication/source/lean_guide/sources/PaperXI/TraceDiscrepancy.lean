import PaperXI.CharacterGenerators
import Mathlib.LinearAlgebra.Trace

/-! A checked normalization route from actual operator traces to discrepancy.
Nonzero normalizing traces are essential and are retained in every cancellation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TraceDiscrepancy

variable {K V W : Type*} [Field K]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- Scalar intertwining is a scalar conjugacy identity of the actual operators. -/
theorem conjugate_eq (U : V ≃ₗ[K] W) (R : Module.End K V) (T : Module.End K W)
    (d : K) (h : ∀ x, U (R x) = d • T (U x)) : U.conj R = d • T := by
  ext y
  simpa using h (U.symm y)

/-- Trace covariance is derived from scalar conjugacy, not assumed as a phase identity. -/
theorem trace_eq (U : V ≃ₗ[K] W) (R : Module.End K V) (T : Module.End K W)
    (d : K) (h : ∀ x, U (R x) = d • T (U x)) :
    LinearMap.trace K V R = d * LinearMap.trace K W T := by
  rw [← LinearMap.trace_conj' R U, conjugate_eq U R T d h, map_smul, smul_eq_mul]

/-- Equality of nonzero actual traces forces a scalar discrepancy to be one. -/
theorem scalar_eq_one (U : V ≃ₗ[K] W) (R : Module.End K V) (T : Module.End K W)
    (d : K) (h : ∀ x, U (R x) = d • T (U x))
    (ht : LinearMap.trace K V R = LinearMap.trace K W T)
    (hne : LinearMap.trace K W T ≠ 0) : d = 1 := by
  have hd := trace_eq U R T d h
  rw [ht] at hd
  exact (mul_right_cancel₀ hne (hd.symm.trans (one_mul _).symm))

/-- A shared nonzero normalization preserves the actual trace ratio. -/
theorem normalized_trace_eq (U : V ≃ₗ[K] W) (R : Module.End K V)
    (T : Module.End K W) (d n : K) (h : ∀ x, U (R x) = d • T (U x)) :
    LinearMap.trace K V R / n = d * (LinearMap.trace K W T / n) := by
  rw [trace_eq U R T d h]
  ring

theorem scalar_eq_one_of_normalized (U : V ≃ₗ[K] W) (R : Module.End K V)
    (T : Module.End K W) (d n : K) (hn : n ≠ 0)
    (h : ∀ x, U (R x) = d • T (U x))
    (ht : LinearMap.trace K V R / n = LinearMap.trace K W T / n)
    (hne : LinearMap.trace K W T ≠ 0) : d = 1 := by
  exact scalar_eq_one U R T d h ((div_left_inj' hn).mp ht) hne

variable {C : Type*} [Group C]

/-- A discrepancy character with equal nonzero generator traces is trivial. -/
theorem character_trivial (U : V ≃ₗ[K] W)
    (R : Representation K C V) (T : Representation K C W) (δ : C →* Kˣ)
    (hδ : ∀ g x, U (R g x) = (δ g : K) • T g (U x))
    (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (htrace : ∀ g ∈ S, LinearMap.trace K V (R g) = LinearMap.trace K W (T g))
    (hne : ∀ g ∈ S, LinearMap.trace K W (T g) ≠ 0) : ∀ g, δ g = 1 := by
  apply CharacterGenerators.trivial δ S hgen
  intro g hg
  apply Units.ext
  exact scalar_eq_one U (R g) (T g) (δ g : K) (hδ g) (htrace g hg) (hne g hg)

/-- The scalar cancellation fails when both traces vanish. -/
theorem zero_trace_cannot_detect_scalar (d : K) : (0 : K) = d * 0 := by simp

/-- Complete closure by trace phases, with the actual lift-covariance and
nonzero normalizer hypotheses exposed. -/
theorem bridge_from_traces {H : Type*} [Group H]
    [Module ℂ V] [Module ℂ W] [FiniteDimensional ℂ V]
    (ρ : Representation ℂ H V) [Representation.IsIrreducible ρ]
    (σ : Representation ℂ H W) (U : V ≃ₗ[ℂ] W)
    (hU : ∀ h x, U (ρ h x) = σ h (U x))
    (α : C →* MulAut H) (R : Representation ℂ C V) (T : Representation ℂ C W)
    (hR : ∀ g h x, R g (ρ h x) = ρ (α g h) (R g x))
    (hT : ∀ g h x, T g (σ h x) = σ (α g h) (T g x))
    (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (htrace : ∀ g ∈ S, LinearMap.trace ℂ V (R g) = LinearMap.trace ℂ W (T g))
    (hne : ∀ g ∈ S, LinearMap.trace ℂ W (T g) ≠ 0) :
    ∀ a x, U (CyclicBridge.semidirectRepresentation α ρ R hR a x) =
      CyclicBridge.semidirectRepresentation α σ T hT a (U x) := by
  obtain ⟨δ, hδ, hclose⟩ := CharacterGenerators.bridge_from_actions
    ρ σ U hU α R T hR hT S hgen
  exact hclose (fun g _ => character_trivial U R T δ hδ S hgen htrace hne g)

end PaperXI.TraceDiscrepancy
