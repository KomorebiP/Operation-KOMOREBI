import PaperXI.CentralProductComparison
import PaperXI.HeisenbergTensorComparison
import PaperXI.BreakHeisenbergSum
import PaperXI.AbstractHeisenbergExtension

/-! Source 15.2: actual tensor factorization on the declared full group.
Compatible factor embeddings construct the group comparison. In the odd
symplectic branch both this comparison and scalar nondegeneracy are derived. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakTensorFactorization
open CentralExtension CocycleCommutator
open scoped Classical

section SuppliedExtensions
variable {S Z G : Type*} [Fintype S] [CommGroup Z] [Group G]
variable {H A V : S → Type*} [∀ s, Group (H s)] [∀ s, CommGroup (A s)]
variable [∀ s, Fintype (A s)] [∀ s, AddCommGroup (V s)] [∀ s, Module ℂ (V s)]
variable {W : Type*} [AddCommGroup W] [Module ℂ W]

/-- The full tensor representation and its equivalence to the given irreducible
representation are constructed from the actual commuting factor embeddings. -/
def source
    (D : ∀ s, Datum Z (H s) (A s)) (E : Datum Z G (∀ s, A s))
    (j : ∀ s, H s →* G)
    (hc : Pairwise fun s t => ∀ h k, Commute (j s h) (j t k))
    (hi : ∀ s z, j s ((D s).i z) = E.i z)
    (hq : ∀ s h, E.q (j s h) = Pi.mulSingle s ((D s).q h))
    (ζ : Z →* ℂˣ) (hnd : ∀ s, radical (scalarCocycle (D s) ζ) = ⊥)
    (σ : ∀ s, Representation ℂ (H s) (V s)) [∀ s, Representation.IsIrreducible (σ s)]
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (τ : Representation ℂ G W) [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ (E.i z) = (ζ z : ℂ) • LinearMap.id) :
    Representation.Equiv
      (HeisenbergTensor.onFullEnvelope D ζ σ hσ
        (CentralProductComparison.equiv D E j hc hi hq)) τ := by
  apply HeisenbergTensor.fullEnvelopeFactorization D ζ hnd σ hσ
  intro z
  simpa only [CentralProduct.datum_i, CentralProductComparison.equiv_center] using hτ z
end SuppliedExtensions

section Odd
variable {S K T : Type*} [Fintype S] [Field K] [Finite K]
variable {B V : S → Type*} [∀ s, AddCommGroup (B s)] [∀ s, Module K (B s)]
variable [∀ s, FiniteDimensional K (B s)]
variable [∀ s, AddCommGroup (V s)] [∀ s, Module ℂ (V s)]
variable [AddCommGroup T] [Module K T]
variable {W : Type*} [AddCommGroup W] [Module ℂ W]

/-- Odd symplectic source endpoint. Neither the full group comparison nor
scalar-cocycle nondegeneracy is assumed; both are constructed from the actual
orthogonal decomposition and the nontrivial additive central character. -/
theorem odd_source
    (b : ∀ s, LinearMap.BilinForm K (B s))
    (hb : ∀ s, (b s).IsAlt) (hbn : ∀ s, (b s).Nondegenerate) (h2 : (2 : K) ≠ 0)
    (c : LinearMap.BilinForm K T) (e : (∀ s, B s) ≃ₗ[K] T)
    (he : ∀ v w, c (e v) (e w) = BreakHeisenbergSum.form b v w)
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (σ : ∀ s, Representation ℂ (AbstractHeisenberg.Element (b s)) (V s))
    [∀ s, Representation.IsIrreducible (σ s)]
    (hσ : ∀ s z, σ s (AbstractHeisenberg.centralElement (b s) z) = ψ z • LinearMap.id)
    (τ : Representation ℂ (AbstractHeisenberg.Element c) W) [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ (AbstractHeisenberg.centralElement c z) = ψ z • LinearMap.id) :
    Nonempty (Representation.Equiv
      (HeisenbergTensor.onFullEnvelope (fun s => AbstractHeisenberg.datum (b s))
        (SymplecticCentralExtension.scalarCharacter ψ) σ (fun s z => hσ s z.toAdd)
        (BreakHeisenbergSum.decompositionEquiv b c e he)) τ) := by
  let : ∀ s, Finite (B s) := fun s => Module.finite_of_finite K
  let : ∀ s, Fintype (Multiplicative (B s)) := fun s => Fintype.ofFinite _
  refine ⟨HeisenbergTensor.fullEnvelopeFactorization _ _ (fun s =>
    AbstractHeisenberg.scalar_radical_eq_bot_scalarCharacter (b s) (hb s) h2 (hbn s).1 ψ hψ)
    σ (fun s z => hσ s z.toAdd) (BreakHeisenbergSum.decompositionEquiv b c e he) τ ?_⟩
  intro z
  rw [CentralProduct.datum_i, BreakHeisenbergSum.decompositionEquiv_center]
  exact hτ z.toAdd
end Odd
end PaperXI.BreakTensorFactorization
