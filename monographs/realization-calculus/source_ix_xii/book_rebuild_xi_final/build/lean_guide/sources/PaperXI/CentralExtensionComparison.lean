import PaperXI.CentralExtensionUniqueness
import PaperXI.HeisenbergTransport

/-! The initial representation comparison along an actual extension lift,
without an odd-characteristic or coordinate-group restriction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtensionComparison
open CentralExtension CocycleCommutator HeisenbergTransport

variable {Z H A G V W : Type*} [CommGroup Z] [Group H] [CommGroup A] [Fintype A]
variable [Group G] [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- Construct the first representation equivalence along the actual group lift. -/
def equivAlong (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥) (e : H ≃* G)
    (ρ : Representation ℂ H V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ z, σ (e (D.i z)) = (ζ z : ℂ) • LinearMap.id) :
    Representation.Equiv ρ (pullback e σ) := by
  letI := pullback_irreducible e σ
  exact CentralExtensionUniqueness.equiv D ζ hnd ρ (pullback e σ) hρ hσ

theorem equivAlong_intertwines (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥) (e : H ≃* G)
    (ρ : Representation ℂ H V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ z, σ (e (D.i z)) = (ζ z : ℂ) • LinearMap.id) (h : H) (v : V) :
    equivAlong D ζ hnd e ρ σ hρ hσ (ρ h v) =
      σ (e h) (equivAlong D ζ hnd e ρ σ hρ hσ v) :=
  Representation.IntertwiningMap.isIntertwining ρ (pullback e σ)
    (equivAlong D ζ hnd e ρ σ hρ hσ).toIntertwiningMap h v

/-- An actual lift and matching central actions determine an invertible
intertwiner, unique up to a unique nonzero complex scalar. -/
theorem exists_unique_along (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥) (e : H ≃* G)
    (ρ : Representation ℂ H V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ z, σ (e (D.i z)) = (ζ z : ℂ) • LinearMap.id) :
    ∃ U : V ≃ₗ[ℂ] W, U.toLinearMap ≠ 0 ∧
      (∀ h v, U (ρ h v) = σ (e h) (U v)) ∧
      ∀ T : V ≃ₗ[ℂ] W, (∀ h v, T (ρ h v) = σ (e h) (T v)) →
        ∃! c : ℂˣ, ∀ v, T v = (c : ℂ) • U v := by
  let U := (equivAlong D ζ hnd e ρ σ hρ hσ).toLinearEquiv
  have hU : ∀ h v, U (ρ h v) = σ (e h) (U v) :=
    equivAlong_intertwines D ζ hnd e ρ σ hρ hσ
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space ρ
  let : FiniteDimensional ℂ V := CentralExtensionUniqueness.finiteDimensional D ζ hnd ρ hρ
  refine ⟨U, ?_, hU, ?_⟩
  · intro h
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have hz : U v = 0 := LinearMap.congr_fun h v
    exact hv (U.injective (hz.trans U.map_zero.symm))
  · intro T hT
    exact SchurScalar.bridge_unique ρ (pullback e σ) U T hU hT

end PaperXI.CentralExtensionComparison
