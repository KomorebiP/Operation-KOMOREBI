import PaperXI.HeisenbergTensor
import PaperXI.CentralProductCommutator
import PaperXI.TensorIrreducible

/-! Finite Heisenberg tensor factorization for the actual central product.
All factor spaces are actual irreducible representation spaces. Their finite
dimensions and nontriviality are derived, including zero quotient factors and
the empty family. The descended tensor action is proved irreducible before
Stone--von Neumann uniqueness is used. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergTensor
open CentralExtension CocycleCommutator TensorProduct
open scoped Classical

variable {S Z : Type*} [Fintype S] [CommGroup Z]
variable {H A V : S → Type*} [∀ s, Group (H s)] [∀ s, CommGroup (A s)]
variable [∀ s, Fintype (A s)] [∀ s, AddCommGroup (V s)] [∀ s, Module ℂ (V s)]
variable (D : ∀ s, Datum Z (H s) (A s)) (ζ : Z →* ℂˣ)
variable (hnd : ∀ s, radical (scalarCocycle (D s) ζ) = ⊥)
variable (σ : ∀ s, Representation ℂ (H s) (V s)) [∀ s, Representation.IsIrreducible (σ s)]
variable (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
include D ζ hnd σ hσ

omit [Fintype S] in
/-- Each factor's finite dimensionality follows from its actual irreducible action. -/
theorem factor_finiteDimensional (s : S) : FiniteDimensional ℂ (V s) :=
  CentralExtensionUniqueness.finiteDimensional (D s) ζ (hnd s) (σ s) (hσ s)

/-- Thus the actual finite tensor product is finite-dimensional. -/
theorem finiteDimensional : FiniteDimensional ℂ (PiTensorProduct ℂ V) := by
  let : ∀ s, FiniteDimensional ℂ (V s) := factor_finiteDimensional D ζ hnd σ hσ
  infer_instance

/-- The tensor product has the required nonzero space, also for an empty family. -/
theorem nontrivial : Nontrivial (PiTensorProduct ℂ V) := by
  let : ∀ s, FiniteDimensional ℂ (V s) := factor_finiteDimensional D ζ hnd σ hσ
  let : ∀ s, Nontrivial (V s) := fun s => GeneratedIrreducibility.nontrivial_space (σ s)
  exact FiniteTensor.nontrivial

/-- The actual tensor dimension squared equals the actual product quotient order. -/
theorem finrank_sq : Module.finrank ℂ (PiTensorProduct ℂ V) ^ 2 =
    Fintype.card (∀ s, A s) := by
  let : ∀ s, FiniteDimensional ℂ (V s) := factor_finiteDimensional D ζ hnd σ hσ
  rw [FiniteTensor.finrank, ← Finset.prod_pow, Fintype.card_pi]
  apply Finset.prod_congr rfl
  intro s _
  exact TensorIrreducible.finrank_sq_of_irreducible (D s) ζ (hnd s) (σ s) (hσ s)

/-- Irreducibility of the literal quotient action on the actual finite tensor product. -/
theorem irreducible : Representation.IsIrreducible (descend D ζ σ hσ) := by
  let : FiniteDimensional ℂ (PiTensorProduct ℂ V) := finiteDimensional D ζ hnd σ hσ
  let : Nontrivial (PiTensorProduct ℂ V) := nontrivial D ζ hnd σ hσ
  exact TensorIrreducible.irreducible (CentralProduct.datum D) ζ
    (CentralProduct.radical_eq_bot D ζ hnd) (descend D ζ σ hσ)
    (central D ζ σ hσ) (finrank_sq D ζ hnd σ hσ)

variable {W : Type*} [AddCommGroup W] [Module ℂ W]

/-- Source 15.2: equivalence of actual representations of the same total central extension. -/
theorem exists_factorization (τ : Representation ℂ (CentralProduct.Group D) W)
    [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ ((CentralProduct.datum D).i z) = (ζ z : ℂ) • LinearMap.id) :
    Nonempty (Representation.Equiv (descend D ζ σ hσ) τ) := by
  let : Representation.IsIrreducible (descend D ζ σ hσ) := irreducible D ζ hnd σ hσ
  exact CentralExtensionUniqueness.exists_equiv (CentralProduct.datum D) ζ
    (CentralProduct.radical_eq_bot D ζ hnd) (descend D ζ σ hσ) τ
    (central D ζ σ hσ) hτ

/-- A chosen invertible intertwiner witnessing the factorization. -/
def factorization (τ : Representation ℂ (CentralProduct.Group D) W)
    [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ ((CentralProduct.datum D).i z) = (ζ z : ℂ) • LinearMap.id) :
    Representation.Equiv (descend D ζ σ hσ) τ :=
  Classical.choice (exists_factorization D ζ hnd σ hσ τ hτ)

/-- The chosen tensor factorization intertwines every actual total group element. -/
theorem factorization_intertwines (τ : Representation ℂ (CentralProduct.Group D) W)
    [Representation.IsIrreducible τ]
    (hτ : ∀ z, τ ((CentralProduct.datum D).i z) = (ζ z : ℂ) • LinearMap.id)
    (g : CentralProduct.Group D) (x : PiTensorProduct ℂ V) :
    factorization D ζ hnd σ hσ τ hτ (descend D ζ σ hσ g x) =
      τ g (factorization D ζ hnd σ hσ τ hτ x) :=
  Representation.IntertwiningMap.isIntertwining _ _
    (factorization D ζ hnd σ hσ τ hτ).toIntertwiningMap g x

end PaperXI.HeisenbergTensor
