import PaperXI.GeneratedIrreducibility
import Mathlib.Analysis.Complex.Polynomial.Basic

/-! Scalar commutants and uniqueness of actual irreducible representation bridges. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchurScalar
open PaperXI.GeneratedIrreducibility
variable {G V W : Type*} [Group G]
variable [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable [AddCommGroup W] [Module ℂ W]

theorem commuting_scalar (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (F : Module.End ℂ V) (hF : ∀ g x, F (ρ g x) = ρ g (F x)) :
    ∃ c : ℂ, F = c • LinearMap.id := by
  let f : Representation.IntertwiningMap ρ ρ :=
    ⟨F, fun g => LinearMap.ext (hF g)⟩
  obtain ⟨c, hc⟩ := (Representation.IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
    (ρ := ρ)).surjective f
  refine ⟨c, ?_⟩
  have h := congrArg Representation.IntertwiningMap.toLinearMap hc
  exact h.symm

omit [FiniteDimensional ℂ V] in
theorem scalar_unique (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (F : Module.End ℂ V) {c d : ℂ} (hc : F = c • LinearMap.id) (hd : F = d • LinearMap.id) : c = d := by
  have : Nontrivial V := nontrivial_space ρ
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  have h := LinearMap.congr_fun (hc.symm.trans hd) v
  exact (smul_left_injective ℂ hv) h

/-- An invertible operator in the commutant has a nonzero scalar. -/
theorem commuting_unit (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (F : V ≃ₗ[ℂ] V) (hF : ∀ g x, F (ρ g x) = ρ g (F x)) :
    ∃ c : ℂˣ, ∀ x, F x = (c : ℂ) • x := by
  obtain ⟨c, hc⟩ := commuting_scalar ρ F.toLinearMap hF
  have : Nontrivial V := nontrivial_space ρ
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  have hc0 : c ≠ 0 := by
    intro hz
    have h : F v = 0 := by simpa [hz] using LinearMap.congr_fun hc v
    exact hv (F.injective (h.trans F.map_zero.symm))
  exact ⟨Units.mk0 c hc0, fun x => LinearMap.congr_fun hc x⟩

/-- Two actual invertible intertwiners differ by a unique nonzero scalar. -/
theorem bridge_unique (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (σ : Representation ℂ G W) (U T : V ≃ₗ[ℂ] W)
    (hU : ∀ g x, U (ρ g x) = σ g (U x))
    (hT : ∀ g x, T (ρ g x) = σ g (T x)) :
    ∃! c : ℂˣ, ∀ x, T x = (c : ℂ) • U x := by
  have hcomm (g : G) (x : V) : (T.trans U.symm) (ρ g x) = ρ g ((T.trans U.symm) x) := by
    apply U.injective
    simp only [LinearEquiv.trans_apply, U.apply_symm_apply, hT, hU]
  obtain ⟨c, hc⟩ := commuting_unit ρ (T.trans U.symm) hcomm
  have hct (x : V) : T x = (c : ℂ) • U x := by
    have h := congrArg U (hc x)
    simpa using h
  refine ⟨c, hct, ?_⟩
  intro d hd
  have : Nontrivial V := nontrivial_space ρ
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  have hUv : U v ≠ 0 := fun h => hv (U.injective (h.trans U.map_zero.symm))
  apply Units.ext
  exact (smul_left_injective ℂ hUv) ((hd v).symm.trans (hct v))

end PaperXI.SchurScalar
