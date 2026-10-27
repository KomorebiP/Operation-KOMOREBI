import PaperXI.HeisenbergTransport
import PaperXI.SchrodingerUniversal

/-! The first actual intertwiner between arbitrary irreducible actions along
a group equivalence from the odd-characteristic coordinate Heisenberg group.
The coordinate isometry specialization constructs that group equivalence.
Abstract symplectic coordinates, source quotient actions, and the dyadic
extension branch are not supplied by this module. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergComparison

open Heisenberg HeisenbergTransport

variable {K X G V W : Type*} [Field K] [AddCommGroup X] [Module K X]
variable [Fintype X] [Fintype (Module.Dual K X)] [FiniteDimensional K X]
variable [Group G] [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- Construct the first equivalence between arbitrary irreducible actions,
by comparing both actions to the model after pulling back the second one. -/
def equivAlong (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (e : Element K X ≃* G)
    (ρ : Representation ℂ (Element K X) V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (centralElement z) = ψ z • LinearMap.id)
    (hσ : ∀ z, σ (e (centralElement z)) = ψ z • LinearMap.id) :
    Representation.Equiv ρ (pullback e σ) := by
  letI := pullback_irreducible e σ
  exact (SchrodingerUniversal.equiv ψ hψ h2 ρ hρ).symm.trans
    (SchrodingerUniversal.equiv ψ hψ h2 (pullback e σ) hσ)

theorem equivAlong_intertwines (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (e : Element K X ≃* G)
    (ρ : Representation ℂ (Element K X) V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (centralElement z) = ψ z • LinearMap.id)
    (hσ : ∀ z, σ (e (centralElement z)) = ψ z • LinearMap.id)
    (g : Element K X) (v : V) :
    equivAlong ψ hψ h2 e ρ σ hρ hσ (ρ g v) =
      σ (e g) (equivAlong ψ hψ h2 e ρ σ hρ hσ v) :=
  Representation.IntertwiningMap.isIntertwining ρ (pullback e σ)
    (equivAlong ψ hψ h2 e ρ σ hρ hσ).toIntertwiningMap g v

/-- Existence does not assume a starting intertwiner or finite dimensionality
of either representation space. The scalar comparison is uniquely invertible. -/
theorem exists_unique_along (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (e : Element K X ≃* G)
    (ρ : Representation ℂ (Element K X) V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (centralElement z) = ψ z • LinearMap.id)
    (hσ : ∀ z, σ (e (centralElement z)) = ψ z • LinearMap.id) :
    ∃ U : V ≃ₗ[ℂ] W, U.toLinearMap ≠ 0 ∧
      (∀ g v, U (ρ g v) = σ (e g) (U v)) ∧
      ∀ T : V ≃ₗ[ℂ] W, (∀ g v, T (ρ g v) = σ (e g) (T v)) →
        ∃! c : ℂˣ, ∀ v, T v = (c : ℂ) • U v := by
  let U := (equivAlong ψ hψ h2 e ρ σ hρ hσ).toLinearEquiv
  have hU : ∀ g v, U (ρ g v) = σ (e g) (U v) :=
    equivAlong_intertwines ψ hψ h2 e ρ σ hρ hσ
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space ρ
  let : FiniteDimensional ℂ V := SchrodingerUniversal.finiteDimensional ψ hψ h2 ρ hρ
  refine ⟨U, ?_, hU, ?_⟩
  · intro h
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have hz : U v = 0 := LinearMap.congr_fun h v
    exact hv (U.injective (hz.trans U.map_zero.symm))
  · intro T hT
    exact SchurScalar.bridge_unique ρ (pullback e σ) U T hU hT

section Coordinates

variable {Y : Type*} [AddCommGroup Y] [Module K Y]

/-- Lift the supplied form-preserving linear equivalence, then construct the
first nonzero intertwiner between the two actual arbitrary irreducibles. -/
theorem exists_unique_of_isometry
    (e : (X × Module.Dual K X) ≃ₗ[K] (Y × Module.Dual K Y)) (he : PreservesForm e)
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (ρ : Representation ℂ (Element K X) V) (σ : Representation ℂ (Element K Y) W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z, ρ (centralElement z) = ψ z • LinearMap.id)
    (hσ : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    ∃ U : V ≃ₗ[ℂ] W, U.toLinearMap ≠ 0 ∧
      (∀ g v, U (ρ g v) = σ (liftIsometry e he g) (U v)) ∧
      ∀ T : V ≃ₗ[ℂ] W, (∀ g v, T (ρ g v) = σ (liftIsometry e he g) (T v)) →
        ∃! c : ℂˣ, ∀ v, T v = (c : ℂ) • U v := by
  apply exists_unique_along ψ hψ h2 (liftIsometry e he) ρ σ hρ
  intro z
  simpa using hσ z

end Coordinates

end PaperXI.HeisenbergComparison
