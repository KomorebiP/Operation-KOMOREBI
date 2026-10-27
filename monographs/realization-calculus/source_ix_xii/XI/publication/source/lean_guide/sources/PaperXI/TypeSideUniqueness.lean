import PaperXI.TypeSideExtension
import PaperXI.CentralExtensionUniqueness

/-! Uniqueness and dimension for the original actual type-side actions.
Character containment is converted to scalar restriction and quotient
descent by proved constructions. The source simple-character structure and
nondegenerate pairing remain explicit inputs. The first intertwiner and
the representation dimensions are conclusions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeSideUniqueness

open TypeSideDescent TypeSideExtension
open scoped IsMulCommutative

variable {G V W : Type*} [Group G]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- Finite dimensionality of the actual representation is derived after
descending its proved character kernel to the constructed central extension. -/
theorem finiteDimensional (H : Subgroup G) [H.Normal] [IsMulCommutative (G ⧸ H)]
    [Finite (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (hnd : CocycleCommutator.radical
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) = ⊥)
    (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) : FiniteDimensional ℂ V := by
  let : Fintype (G ⧸ H) := Fintype.ofFinite _
  let : Representation.IsIrreducible (representation H θ hθ η hcontains) :=
    representation_irreducible H θ hθ η hcontains
  exact CentralExtensionUniqueness.finiteDimensional (datum H θ hθ) (centralCharacter H θ)
    hnd (representation H θ hθ η hcontains) (representation_central_action H θ hθ η hcontains)

/-- The dimension formula is for the original supplied representation space. -/
theorem finrank_sqrt (H : Subgroup G) [H.Normal] [IsMulCommutative (G ⧸ H)]
    [Finite (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (hnd : CocycleCommutator.radical
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) = ⊥)
    (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) :
    Module.finrank ℂ V = Nat.sqrt (Nat.card (G ⧸ H)) := by
  let : Fintype (G ⧸ H) := Fintype.ofFinite _
  let : Representation.IsIrreducible (representation H θ hθ η hcontains) :=
    representation_irreducible H θ hθ η hcontains
  simpa only [Nat.card_eq_fintype_card] using
    CentralExtensionUniqueness.finrank_sqrt (datum H θ hθ) (centralCharacter H θ)
      hnd (representation H θ hθ η hcontains) (representation_central_action H θ hθ η hcontains)

/-- Construct an equivalence of the original actual representations, not
merely an equivalence of two separately assumed quotient actions. -/
theorem exists_equiv (H : Subgroup G) [H.Normal] [IsMulCommutative (G ⧸ H)]
    [Finite (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (hnd : CocycleCommutator.radical
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) = ⊥)
    (η : Representation ℂ G V) (τ : Representation ℂ G W)
    [Representation.IsIrreducible η] [Representation.IsIrreducible τ]
    (hη : Contains H θ η) (hτ : Contains H θ τ) :
    Nonempty (Representation.Equiv η τ) := by
  let : Fintype (G ⧸ H) := Fintype.ofFinite _
  let : Representation.IsIrreducible (representation H θ hθ η hη) :=
    representation_irreducible H θ hθ η hη
  let : Representation.IsIrreducible (representation H θ hθ τ hτ) :=
    representation_irreducible H θ hθ τ hτ
  obtain ⟨U⟩ := CentralExtensionUniqueness.exists_equiv (datum H θ hθ) (centralCharacter H θ)
    hnd (representation H θ hθ η hη) (representation H θ hθ τ hτ)
    (representation_central_action H θ hθ η hη) (representation_central_action H θ hθ τ hτ)
  exact ⟨Representation.Equiv.mk U.toLinearEquiv
    (fun g => U.toIntertwiningMap.isIntertwining' (QuotientGroup.mk' (characterKernel H θ hθ) g))⟩

/-- The first nonzero invertible comparison and its unique unit-scalar
ambiguity, on all original group elements and original representation vectors. -/
theorem exists_unique_intertwiner (H : Subgroup G) [H.Normal]
    [IsMulCommutative (G ⧸ H)] [Finite (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (hnd : CocycleCommutator.radical
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) = ⊥)
    (η : Representation ℂ G V) (τ : Representation ℂ G W)
    [Representation.IsIrreducible η] [Representation.IsIrreducible τ]
    (hη : Contains H θ η) (hτ : Contains H θ τ) :
    ∃ U : V ≃ₗ[ℂ] W, U.toLinearMap ≠ 0 ∧
      (∀ g v, U (η g v) = τ g (U v)) ∧
      ∀ T : V ≃ₗ[ℂ] W, (∀ g v, T (η g v) = τ g (T v)) →
        ∃! c : ℂˣ, ∀ v, T v = (c : ℂ) • U v := by
  obtain ⟨E⟩ := exists_equiv H θ hθ hnd η τ hη hτ
  let U := E.toLinearEquiv
  have hU : ∀ g v, U (η g v) = τ g (U v) :=
    Representation.IntertwiningMap.isIntertwining η τ E.toIntertwiningMap
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space η
  let : FiniteDimensional ℂ V := finiteDimensional H θ hθ hnd η hη
  refine ⟨U, ?_, hU, ?_⟩
  · intro hzero
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have hz : U v = 0 := LinearMap.congr_fun hzero v
    exact hv (U.injective (hz.trans U.map_zero.symm))
  · intro T hT
    exact SchurScalar.bridge_unique η τ U T hU hT

end PaperXI.TypeSideUniqueness
