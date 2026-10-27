import PaperXI.BreakTensorMap
import PaperXI.HeisenbergTensor
import PaperXI.CharacterGenerators

/-! Finite break tensor bridges on the actual central quotient. The total
stabilizer phase is the product of the actual factor discrepancies. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakBridge

variable {ι Z : Type*} [Fintype ι] [CommGroup Z]
variable {H A V W : ι → Type*} [∀ i, Group (H i)] [∀ i, CommGroup (A i)]
variable [∀ i, AddCommGroup (V i)] [∀ i, Module ℂ (V i)]
variable [∀ i, AddCommGroup (W i)] [∀ i, Module ℂ (W i)]

omit [Fintype ι] in
/-- The tensor map intertwines the retained center and all original factors. -/
theorem ambient_intertwines (ζ : Z →* ℂˣ)
    (ρ : ∀ i, Representation ℂ (H i) (V i))
    (σ : ∀ i, Representation ℂ (H i) (W i)) (U : ∀ i, V i ≃ₗ[ℂ] W i)
    (hU : ∀ i h x, U i (ρ i h x) = σ i h (U i x))
    (h : Z × (∀ i, H i)) (x : PiTensorProduct ℂ V) :
    BreakTensorMap.tensor U (HeisenbergTensor.ambient ζ ρ h x) =
      HeisenbergTensor.ambient ζ σ h (BreakTensorMap.tensor U x) := by
  rcases h with ⟨z, h⟩
  simp only [HeisenbergTensor.ambient_apply, map_smul]
  rw [BreakTensorMap.intertwines ρ σ U hU]

/-- The actual quotient descent, with no assumed quotient intertwining conclusion. -/
theorem quotient_intertwines (D : ∀ i, CentralExtension.Datum Z (H i) (A i))
    (ζ : Z →* ℂˣ) (ρ : ∀ i, Representation ℂ (H i) (V i))
    (σ : ∀ i, Representation ℂ (H i) (W i))
    (hρ : ∀ i z, ρ i ((D i).i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ i z, σ i ((D i).i z) = (ζ z : ℂ) • LinearMap.id)
    (U : ∀ i, V i ≃ₗ[ℂ] W i)
    (hU : ∀ i h x, U i (ρ i h x) = σ i h (U i x)) :
    ∀ h x, BreakTensorMap.tensor U (HeisenbergTensor.descend D ζ ρ hρ h x) =
      HeisenbergTensor.descend D ζ σ hσ h (BreakTensorMap.tensor U x) := by
  apply BreakTensorMap.descends (CentralProduct.mk D) (CentralProduct.mk_surjective D)
  intro h x
  simpa only [HeisenbergTensor.descend_mk] using ambient_intertwines ζ ρ σ U hU h x

variable {C : Type*} [Group C]

/-- Agreement of the total phase on generators closes the tensor stabilizer action.
Individual factor phases may be nontrivial and cancel in their product. -/
theorem stabilizer_intertwines
    (R : ∀ i, Representation ℂ C (V i)) (T : ∀ i, Representation ℂ C (W i))
    (U : ∀ i, V i ≃ₗ[ℂ] W i) (δ : ι → C →* ℂˣ)
    (hδ : ∀ i g x, U i (R i g x) = (δ i g : ℂ) • T i g (U i x))
    (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (hphase : ∀ g ∈ S, ∏ i, δ i g = 1) :
    ∀ g x, BreakTensorMap.tensor U (BreakTensorMap.stabilizer R g x) =
      BreakTensorMap.stabilizer T g (BreakTensorMap.tensor U x) := by
  have hone := CharacterGenerators.trivial (BreakTensorMap.productCharacter δ) S hgen hphase
  intro g x
  simpa only [hone g, Units.val_one, one_smul] using
    BreakTensorMap.scalar_intertwines R T U δ hδ g x

/-- Factorwise phase equality is a sufficient special case of total phase equality. -/
theorem stabilizer_intertwines_of_factor_phases
    (R : ∀ i, Representation ℂ C (V i)) (T : ∀ i, Representation ℂ C (W i))
    (U : ∀ i, V i ≃ₗ[ℂ] W i) (δ : ι → C →* ℂˣ)
    (hδ : ∀ i g x, U i (R i g x) = (δ i g : ℂ) • T i g (U i x))
    (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (hphase : ∀ i g, g ∈ S → δ i g = 1) :
    ∀ g x, BreakTensorMap.tensor U (BreakTensorMap.stabilizer R g x) =
      BreakTensorMap.stabilizer T g (BreakTensorMap.tensor U x) := by
  apply stabilizer_intertwines R T U δ hδ S hgen
  intro g hg
  simp [hphase, hg]

/-- Full finite-envelope endpoint once the honest actions implement the declared
actual automorphisms of the central quotient. These are lift-covariance hypotheses. -/
theorem semidirect_intertwines
    (D : ∀ i, CentralExtension.Datum Z (H i) (A i))
    (ζ : Z →* ℂˣ) (ρ : ∀ i, Representation ℂ (H i) (V i))
    (σ : ∀ i, Representation ℂ (H i) (W i))
    (hρ : ∀ i z, ρ i ((D i).i z) = (ζ z : ℂ) • LinearMap.id)
    (hσ : ∀ i z, σ i ((D i).i z) = (ζ z : ℂ) • LinearMap.id)
    (U : ∀ i, V i ≃ₗ[ℂ] W i)
    (hU : ∀ i h x, U i (ρ i h x) = σ i h (U i x))
    (α : C →* MulAut (CentralProduct.Group D))
    (R : ∀ i, Representation ℂ C (V i)) (T : ∀ i, Representation ℂ C (W i))
    (hR : ∀ g h x, BreakTensorMap.stabilizer R g (HeisenbergTensor.descend D ζ ρ hρ h x) =
      HeisenbergTensor.descend D ζ ρ hρ (α g h) (BreakTensorMap.stabilizer R g x))
    (hT : ∀ g h x, BreakTensorMap.stabilizer T g (HeisenbergTensor.descend D ζ σ hσ h x) =
      HeisenbergTensor.descend D ζ σ hσ (α g h) (BreakTensorMap.stabilizer T g x))
    (δ : ι → C →* ℂˣ)
    (hδ : ∀ i g x, U i (R i g x) = (δ i g : ℂ) • T i g (U i x))
    (S : Set C) (hgen : Subgroup.closure S = ⊤)
    (hphase : ∀ g ∈ S, ∏ i, δ i g = 1) :
    ∀ a x, BreakTensorMap.tensor U
        (CyclicBridge.semidirectRepresentation α (HeisenbergTensor.descend D ζ ρ hρ)
          (BreakTensorMap.stabilizer R) hR a x) =
      CyclicBridge.semidirectRepresentation α (HeisenbergTensor.descend D ζ σ hσ)
        (BreakTensorMap.stabilizer T) hT a (BreakTensorMap.tensor U x) := by
  apply CyclicBridge.semidirect_intertwining α _ _ (BreakTensorMap.tensor U)
  · simpa only [CyclicBridge.semidirectRepresentation_inl] using
      quotient_intertwines D ζ ρ σ hρ hσ U hU
  · simpa only [CyclicBridge.semidirectRepresentation_inr] using
      stabilizer_intertwines R T U δ hδ S hgen hphase

end PaperXI.BreakBridge
