import PaperXI.BreakBridge
import PaperXI.CentralProductMap
import PaperXI.HeisenbergTensorFactorization

/-! Tensor bridges between different actual break extensions, with discrepancy
characters derived from the chosen honest stabilizer actions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakBridgeAlong

variable {S Z C : Type*} [Fintype S] [CommGroup Z] [Group C]
variable {H A H' A' V W : S → Type*}
variable [∀ s, Group (H s)] [∀ s, CommGroup (A s)]
variable [∀ s, Group (H' s)] [∀ s, CommGroup (A' s)]
variable [∀ s, AddCommGroup (V s)] [∀ s, Module ℂ (V s)]
variable [∀ s, AddCommGroup (W s)] [∀ s, Module ℂ (W s)]

/-- Actual group isomorphisms of the factors induce the tensor quotient bridge. -/
theorem quotient_intertwines
    (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (E : ∀ s, CentralExtension.Datum Z (H' s) (A' s))
    (f : ∀ s, H s ≃* H' s) (hf : ∀ s z, f s ((D s).i z) = (E s).i z)
    (ζ : Z →* ℂˣ) (ρ : ∀ s, Representation ℂ (H s) (V s))
    (σ : ∀ s, Representation ℂ (H' s) (W s))
    (hρ : ∀ s z, ρ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ s z, σ s ((E s).i z) = (ζ z : ℂ) • LinearMap.id)
    (U : ∀ s, V s ≃ₗ[ℂ] W s)
    (hU : ∀ s h x, U s (ρ s h x) = σ s (f s h) (U s x))
    (h : CentralProduct.Group D) (x : PiTensorProduct ℂ V) :
    BreakTensorMap.tensor U (HeisenbergTensor.descend D ζ ρ hρ h x) =
      HeisenbergTensor.descend E ζ σ hσ (CentralProduct.congr D E f hf h)
        (BreakTensorMap.tensor U x) := by
  obtain ⟨⟨z,h⟩, rfl⟩ := CentralProduct.mk_surjective D h
  have he : (BreakTensorMap.tensor U).toLinearMap.comp (HeisenbergTensor.ambient ζ ρ (z,h)) =
      (HeisenbergTensor.ambient ζ σ (z, fun s => f s (h s))).comp
        (BreakTensorMap.tensor U).toLinearMap := by
    apply PiTensorProduct.ext
    ext v
    simp [hU]
  exact DFunLike.congr_fun he x

/-- The factor discrepancies are produced by Schur from the actual lift
covariance. Only their product must vanish on generators. Finite dimensionality
is derived from the original Heisenberg representations. -/
theorem source [∀ s, Fintype (A s)]
    (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (E : ∀ s, CentralExtension.Datum Z (H' s) (A' s))
    (f : ∀ s, H s ≃* H' s) (hf : ∀ s z, f s ((D s).i z) = (E s).i z)
    (ζ : Z →* ℂˣ)
    (hnd : ∀ s, CocycleCommutator.radical (CentralExtension.scalarCocycle (D s) ζ) = ⊥)
    (ρ : ∀ s, Representation ℂ (H s) (V s)) [∀ s, Representation.IsIrreducible (ρ s)]
    (σ : ∀ s, Representation ℂ (H' s) (W s))
    (hρ : ∀ s z, ρ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ s z, σ s ((E s).i z) = (ζ z : ℂ) • LinearMap.id)
    (U : ∀ s, V s ≃ₗ[ℂ] W s)
    (hU : ∀ s h x, U s (ρ s h x) = σ s (f s h) (U s x))
    (α : ∀ s, C →* MulAut (H s))
    (R : ∀ s, Representation ℂ C (V s)) (T : ∀ s, Representation ℂ C (W s))
    (hR : ∀ s g h x, R s g (ρ s h x) = ρ s (α s g h) (R s g x))
    (hT : ∀ s g h x, T s g (σ s (f s h) x) = σ s (f s (α s g h)) (T s g x))
    (gens : Set C) (hgen : Subgroup.closure gens = ⊤) :
    ∃ δ : S → C →* ℂˣ,
      (∀ s g x, U s (R s g x) = (δ s g : ℂ) • T s g (U s x)) ∧
      ((∀ g ∈ gens, ∏ s, δ s g = 1) →
        (∀ h x, BreakTensorMap.tensor U (HeisenbergTensor.descend D ζ ρ hρ h x) =
          HeisenbergTensor.descend E ζ σ hσ (CentralProduct.congr D E f hf h)
            (BreakTensorMap.tensor U x)) ∧
        (∀ g x, BreakTensorMap.tensor U (BreakTensorMap.stabilizer R g x) =
          BreakTensorMap.stabilizer T g (BreakTensorMap.tensor U x))) := by
  let : ∀ s, FiniteDimensional ℂ (V s) :=
    HeisenbergTensor.factor_finiteDimensional D ζ hnd ρ hρ
  have hd (s : S) : ∃ δ : C →* ℂˣ,
      ∀ g x, U s (R s g x) = (δ g : ℂ) • T s g (U s x) :=
    DiscrepancyCharacter.exists_character (ρ s) ((σ s).comp (f s).toMonoidHom)
      (U s) (hU s) (α s) (R s) (T s) (hR s) (hT s)
  choose δ hδ using hd
  exact ⟨δ, hδ, fun hphase => ⟨quotient_intertwines D E f hf ζ ρ σ hρ hσ U hU,
    BreakBridge.stabilizer_intertwines R T U δ hδ gens hgen hphase⟩⟩

end PaperXI.BreakBridgeAlong
