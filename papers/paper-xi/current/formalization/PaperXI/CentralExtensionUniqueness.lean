import PaperXI.CentralCharacterIrreducible
import PaperXI.TwistedModules
import PaperXI.SchurScalar

/-! Finite Stone–von Neumann for actual central extensions with nondegenerate
scalar commutator. Only the quotient is required finite. The argument works
in every characteristic and derives the dimensions of the given irreducibles. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtensionUniqueness
open CentralExtension CentralCharacter AlgebraActionModule CocycleCommutator

variable {Z H A V W : Type*} [CommGroup Z] [Group H] [CommGroup A] [Fintype A]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- Every irreducible representation with the prescribed central action is
finite-dimensional; this is not a hypothesis on its space. -/
theorem finiteDimensional (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H W) [Representation.IsIrreducible σ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    FiniteDimensional ℂ W := by
  let φ := toAlgebraAction D ζ σ hσ
  let : IsSimpleModule (CentralCharacter.Algebra D ζ) (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ) := simpleModule D ζ σ hσ
  let : IsSimpleRing (CentralCharacter.Algebra D ζ) :=
    TwistedSimple.isSimpleRing (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) hnd
  let : FiniteDimensional ℂ (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ) :=
    SimpleModuleClassification.finiteDimensional (CentralCharacter.Algebra D ζ) (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ)
  exact FiniteDimensional.of_injective (AlgebraActionModule.equiv (B := ↥(CentralCharacter.Algebra D ζ)) φ).symm.toLinearMap
    (AlgebraActionModule.equiv (B := ↥(CentralCharacter.Algebra D ζ)) φ).symm.injective

/-- The dimension of each actual irreducible is the square root of the quotient order. -/
theorem finrank_sqrt (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H W) [Representation.IsIrreducible σ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Module.finrank ℂ W = Nat.sqrt (Fintype.card A) := by
  let φ := toAlgebraAction D ζ σ hσ
  let : IsSimpleModule (CentralCharacter.Algebra D ζ) (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ) := simpleModule D ζ σ hσ
  rw [← (AlgebraActionModule.equiv (B := ↥(CentralCharacter.Algebra D ζ)) φ).finrank_eq]
  exact TwistedModules.finrank_sqrt (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)
    hnd (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ)

set_option backward.isDefEq.respectTransparency false in
/-- The first equivalence between arbitrary irreducibles is constructed from
the equivalence of their actual simple twisted-algebra modules. -/
theorem exists_equiv (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H V) (τ : Representation ℂ H W)
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hτ : ∀ z, τ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Nonempty (Representation.Equiv σ τ) := by
  let φ := toAlgebraAction D ζ σ hσ
  let χ := toAlgebraAction D ζ τ hτ
  let : IsSimpleModule (CentralCharacter.Algebra D ζ) (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ) := simpleModule D ζ σ hσ
  let : IsSimpleModule (CentralCharacter.Algebra D ζ) (Space (B := ↥(CentralCharacter.Algebra D ζ)) χ) := simpleModule D ζ τ hτ
  obtain ⟨e⟩ := TwistedModules.equivalent (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)
    hnd (Space (B := ↥(CentralCharacter.Algebra D ζ)) φ) (Space (B := ↥(CentralCharacter.Algebra D ζ)) χ)
  let U : V ≃ₗ[ℂ] W := e.restrictScalars ℂ
  have hU : ∀ h v, U (σ h v) = τ h (U v) :=
    (action_intertwines_iff D ζ σ τ hσ hτ U.toLinearMap).mpr
      (fun b v => e.map_smul b v)
  let F : Representation.IntertwiningMap σ τ := ⟨U.toLinearMap, fun h => LinearMap.ext (hU h)⟩
  exact ⟨F.ofBijective U.bijective⟩

/-- A chosen equivalence supplied by the existence theorem. -/
def equiv (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H V) (τ : Representation ℂ H W)
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hτ : ∀ z, τ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Representation.Equiv σ τ := Classical.choice (exists_equiv D ζ hnd σ τ hσ hτ)

theorem equiv_intertwines (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H V) (τ : Representation ℂ H W)
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hτ : ∀ z, τ (D.i z) = (ζ z : ℂ) • LinearMap.id) (h : H) (v : V) :
    equiv D ζ hnd σ τ hσ hτ (σ h v) = τ h (equiv D ζ hnd σ τ hσ hτ v) :=
  Representation.IntertwiningMap.isIntertwining σ τ
    (equiv D ζ hnd σ τ hσ hτ).toIntertwiningMap h v

/-- Every other invertible intertwiner differs by a unique nonzero scalar. -/
theorem unique_scalar (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥)
    (σ : Representation ℂ H V) (τ : Representation ℂ H W)
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hτ : ∀ z, τ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (T : V ≃ₗ[ℂ] W) (hT : ∀ h v, T (σ h v) = τ h (T v)) :
    ∃! c : ℂˣ, ∀ v, T v = (c : ℂ) • equiv D ζ hnd σ τ hσ hτ v := by
  let : FiniteDimensional ℂ V := finiteDimensional D ζ hnd σ hσ
  exact SchurScalar.bridge_unique σ τ (equiv D ζ hnd σ τ hσ hτ).toLinearEquiv T
    (equiv_intertwines D ζ hnd σ τ hσ hτ) hT

end PaperXI.CentralExtensionUniqueness
