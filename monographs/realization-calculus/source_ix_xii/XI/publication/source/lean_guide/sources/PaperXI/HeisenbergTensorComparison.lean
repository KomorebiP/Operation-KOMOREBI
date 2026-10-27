import PaperXI.HeisenbergTensorFactorization
import PaperXI.CentralExtensionComparison

/-! Tensor factorization transported along an actual equivalence to a declared
full central extension. The comparisons intertwine actual group actions, not
only vector-space dimensions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergTensor
open CentralExtension CocycleCommutator
open scoped Classical

variable {S Z : Type*} [Fintype S] [CommGroup Z]
variable {H A V : S → Type*} [∀ s, Group (H s)] [∀ s, CommGroup (A s)]
variable [∀ s, Fintype (A s)] [∀ s, AddCommGroup (V s)] [∀ s, Module ℂ (V s)]
variable (D : ∀ s, Datum Z (H s) (A s)) (ζ : Z →* ℂˣ)
variable (hnd : ∀ s, radical (scalarCocycle (D s) ζ) = ⊥)
variable (σ : ∀ s, Representation ℂ (H s) (V s)) [∀ s, Representation.IsIrreducible (σ s)]
variable (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
variable {G W : Type*} [Group G] [AddCommGroup W] [Module ℂ W]

/-- The total representation is compared through an actual central-extension equivalence. -/
def factorizationAlong (e : CentralProduct.Group D ≃* G)
    (τ : Representation ℂ G W) [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ (e ((CentralProduct.datum D).i z)) = (ζ z : ℂ) • LinearMap.id) :
    Representation.Equiv (descend D ζ σ hσ) (HeisenbergTransport.pullback e τ) := by
  let : Representation.IsIrreducible (descend D ζ σ hσ) := irreducible D ζ hnd σ hσ
  exact CentralExtensionComparison.equivAlong (CentralProduct.datum D) ζ
    (CentralProduct.radical_eq_bot D ζ hnd) e (descend D ζ σ hσ) τ
    (central D ζ σ hσ) hτ

/-- Actual covariance of the tensor comparison along the declared group equivalence. -/
theorem factorizationAlong_intertwines (e : CentralProduct.Group D ≃* G)
    (τ : Representation ℂ G W) [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ (e ((CentralProduct.datum D).i z)) = (ζ z : ℂ) • LinearMap.id)
    (g : CentralProduct.Group D) (x : PiTensorProduct ℂ V) :
    factorizationAlong D ζ hnd σ hσ e τ hτ (descend D ζ σ hσ g x) =
      τ (e g) (factorizationAlong D ζ hnd σ hσ e τ hτ x) :=
  Representation.IntertwiningMap.isIntertwining _ _
    (factorizationAlong D ζ hnd σ hσ e τ hτ).toIntertwiningMap g x

/-- The actual tensor action as a representation of the full declared group. -/
def onFullEnvelope (e : CentralProduct.Group D ≃* G) :
    Representation ℂ G (PiTensorProduct ℂ V) :=
  (descend D ζ σ hσ).comp e.symm.toMonoidHom

/-- Factorization as an equivalence of representations of the very same full group. -/
def fullEnvelopeFactorization (e : CentralProduct.Group D ≃* G)
    (τ : Representation ℂ G W) [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ (e ((CentralProduct.datum D).i z)) = (ζ z : ℂ) • LinearMap.id) :
    Representation.Equiv (onFullEnvelope D ζ σ hσ e) τ := by
  let U := (factorizationAlong D ζ hnd σ hσ e τ hτ).toLinearEquiv
  let F : Representation.IntertwiningMap (onFullEnvelope D ζ σ hσ e) τ :=
    ⟨U.toLinearMap, fun g => LinearMap.ext (fun x => by
      have h := factorizationAlong_intertwines D ζ hnd σ hσ e τ hτ (e.symm g) x
      simpa [onFullEnvelope, U] using h)⟩
  exact F.ofBijective U.bijective

/-- Every full-envelope operator is intertwined by the constructed factorization. -/
theorem fullEnvelopeFactorization_intertwines (e : CentralProduct.Group D ≃* G)
    (τ : Representation ℂ G W) [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ (e ((CentralProduct.datum D).i z)) = (ζ z : ℂ) • LinearMap.id)
    (g : G) (x : PiTensorProduct ℂ V) :
    fullEnvelopeFactorization D ζ hnd σ hσ e τ hτ
        (onFullEnvelope D ζ σ hσ e g x) =
      τ g (fullEnvelopeFactorization D ζ hnd σ hσ e τ hτ x) :=
  Representation.IntertwiningMap.isIntertwining _ _
    (fullEnvelopeFactorization D ζ hnd σ hσ e τ hτ).toIntertwiningMap g x

end PaperXI.HeisenbergTensor
