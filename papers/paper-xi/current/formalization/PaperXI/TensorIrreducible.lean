import PaperXI.CentralExtensionUniqueness
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-! A dimension criterion for irreducibility of an actual central-character
representation. Simplicity proves injectivity of its actual algebra action;
the dimension identity then proves surjectivity and irreducibility. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorIrreducible
open CentralExtension CentralCharacter CocycleCommutator

variable {Z H A W : Type*} [CommGroup Z] [Group H] [CommGroup A] [Fintype A]
variable [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W] [Nontrivial W]

omit [FiniteDimensional ℂ W] [Nontrivial W] in
/-- The square dimension identity for each actual irreducible factor. -/
theorem finrank_sq_of_irreducible (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H W) [Representation.IsIrreducible σ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Module.finrank ℂ W ^ 2 = Fintype.card A := by
  let φ := toAlgebraAction D ζ σ hσ
  let : IsSimpleModule (Algebra D ζ)
      (AlgebraActionModule.Space (B := ↥(Algebra D ζ)) φ) := simpleModule D ζ σ hσ
  rw [← (AlgebraActionModule.equiv (B := ↥(Algebra D ζ)) φ).finrank_eq]
  exact TwistedModules.finrank_sq (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)
    hnd (AlgebraActionModule.Space (B := ↥(Algebra D ζ)) φ)

omit [FiniteDimensional ℂ W] in
/-- The simple central-character algebra acts faithfully on every nonzero space. -/
theorem action_injective (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H W)
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Function.Injective (toAlgebraAction D ζ σ hσ) := by
  let : IsSimpleRing (Algebra D ζ) :=
    TwistedSimple.isSimpleRing (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) hnd
  exact RingHom.injective (R := ↥(Algebra D ζ)) (toAlgebraAction D ζ σ hσ).toRingHom

/-- The required dimension forces this literal action to fill every endomorphism. -/
theorem action_surjective (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H W)
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hdim : Module.finrank ℂ W ^ 2 = Fintype.card A) :
    Function.Surjective (toAlgebraAction D ζ σ hσ) := by
  have hd : Module.finrank ℂ (Algebra D ζ) = Module.finrank ℂ (Module.End ℂ W) := by
    rw [TwistedAlgebra.finrank_eq_card, Module.finrank_linearMap, ← pow_two, hdim]
  let F : Algebra D ζ →ₗ[ℂ] Module.End ℂ W := (toAlgebraAction D ζ σ hσ).toLinearMap
  have hf : Function.Injective F := action_injective D ζ hnd σ hσ
  change Function.Surjective F
  exact (LinearMap.injective_iff_surjective_of_finrank_eq_finrank
    (K := ℂ) (V := ↥(Algebra D ζ)) (V₂ := Module.End ℂ W) hd (f := F)).1 hf

/-- Equality of the Heisenberg dimension and central character is sufficient
because the actual action was proved surjective, not because uniqueness was assumed. -/
theorem irreducible (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H W)
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hdim : Module.finrank ℂ W ^ 2 = Fintype.card A) :
    Representation.IsIrreducible σ := by
  apply RepresentationStability.irreducible_of_stable
  intro S hS
  by_cases hbot : S = ⊥
  · exact Or.inl hbot
  · right
    obtain ⟨x, hx, hx0⟩ := Submodule.exists_mem_ne_zero_of_ne_bot hbot
    obtain ⟨f, hf⟩ := Module.Projective.exists_dual_eq_one ℂ hx0
    apply top_unique
    intro y _
    obtain ⟨b, hb⟩ := action_surjective D ζ hnd σ hσ hdim (f.smulRight y)
    have hmem := (action_stable_iff D ζ σ hσ S).2 hS b x hx
    rw [hb] at hmem
    simpa [hf] using hmem

end PaperXI.TensorIrreducible
