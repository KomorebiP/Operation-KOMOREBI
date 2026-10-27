import PaperXI.CentralExtensionComparison
import PaperXI.AbstractHeisenbergExtension
import PaperXI.SymplecticCentralExtension

/-! Source 11.2: the initial bridge between the supplied Heisenberg envelopes.
The odd branch constructs the lift on arbitrary abstract symplectic spaces.
The dyadic branch retains the supplied isomorphism of actual central
extensions. Neither branch assumes an initial intertwiner, scalar-cocycle
nondegeneracy, or finite-dimensionality of either representation space. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.RestrictedHeisenbergBridge

open CentralExtension SymplecticCentralExtension
variable {K V V' W W' : Type*} [Field K] [Finite K]
variable [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable [AddCommGroup V'] [Module K V']
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup W'] [Module ℂ W']

/-- Odd-characteristic source bridge on arbitrary abstract symplectic spaces.
The group lift is constructed from the supplied linear isometry. The
nontrivial character and field-valued nondegenerate form supply the scalar
nondegeneracy required by the uniqueness theorem. -/
theorem odd_source
    (b : LinearMap.BilinForm K V) (b' : LinearMap.BilinForm K V')
    (hb : b.IsAlt) (hbn : b.Nondegenerate) (h2 : (2 : K) ≠ 0)
    (ι : V ≃ₗ[K] V') (hι : ∀ v w, b' (ι v) (ι w) = b v w)
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (ρ : Representation ℂ (AbstractHeisenberg.Element b) W)
    (σ : Representation ℂ (AbstractHeisenberg.Element b') W')
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z : K, ρ (AbstractHeisenberg.centralElement b z) = ψ z • LinearMap.id)
    (hσ : ∀ z : K, σ (AbstractHeisenberg.centralElement b' z) = ψ z • LinearMap.id) :
    ∃ U : W ≃ₗ[ℂ] W', U.toLinearMap ≠ 0 ∧
      (∀ h w, U (ρ h w) = σ (AbstractHeisenberg.lift b b' ι hι h) (U w)) ∧
      ∀ T : W ≃ₗ[ℂ] W',
        (∀ h w, T (ρ h w) = σ (AbstractHeisenberg.lift b b' ι hι h) (T w)) →
          ∃! c : ℂˣ, ∀ w, T w = (c : ℂ) • U w := by
  let : Finite V := Module.finite_of_finite K
  let : Fintype (Multiplicative V) := Fintype.ofFinite _
  apply CentralExtensionComparison.exists_unique_along (AbstractHeisenberg.datum b)
    (scalarCharacter ψ)
    (AbstractHeisenberg.scalar_radical_eq_bot_scalarCharacter b hb h2 hbn.1 ψ hψ)
    (AbstractHeisenberg.lift b b' ι hι) ρ σ
  · intro z
    exact hρ z.toAdd
  · intro z
    rw [AbstractHeisenberg.lift_inclusion]
    exact hσ z.toAdd

variable {H H' : Type*} [Group H] [Group H']

omit [Module K V'] in
/-- The source branch for supplied actual extensions, including residue
characteristic two. The actual lift is an input from the compatible dyadic
extension data; an alternating form is not used to manufacture that lift.
The argument works in every characteristic and never divides by two. -/
theorem dyadic_source
    (D : Datum (Multiplicative K) H (Multiplicative V))
    (D' : Datum (Multiplicative K) H' (Multiplicative V'))
    (b : LinearMap.BilinForm K V) (hbn : b.Nondegenerate)
    (hcomm : ∀ h k : H, centralCommutator D h k =
      Multiplicative.ofAdd (b (D.q h).toAdd (D.q k).toAdd))
    (e : H ≃* H') (he : ∀ z : Multiplicative K, e (D.i z) = D'.i z)
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (ρ : Representation ℂ H W) (σ : Representation ℂ H' W')
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (hρ : ∀ z : K, ρ (D.i (Multiplicative.ofAdd z)) = ψ z • LinearMap.id)
    (hσ : ∀ z : K, σ (D'.i (Multiplicative.ofAdd z)) = ψ z • LinearMap.id) :
    ∃ U : W ≃ₗ[ℂ] W', U.toLinearMap ≠ 0 ∧
      (∀ h w, U (ρ h w) = σ (e h) (U w)) ∧
      ∀ T : W ≃ₗ[ℂ] W', (∀ h w, T (ρ h w) = σ (e h) (T w)) →
        ∃! c : ℂˣ, ∀ w, T w = (c : ℂ) • U w := by
  let : Finite V := Module.finite_of_finite K
  let : Fintype (Multiplicative V) := Fintype.ofFinite _
  apply CentralExtensionComparison.exists_unique_along D (scalarCharacter ψ)
    (radical_eq_bot_scalarCharacter D b hbn.1 hcomm ψ hψ) e ρ σ
  · intro z
    exact hρ z.toAdd
  · intro z
    rw [he]
    exact hσ z.toAdd

end PaperXI.RestrictedHeisenbergBridge
