import PaperXI.SymplecticCentralExtension
import PaperXI.CentralExtensionExistence
import Mathlib.Algebra.Group.TypeTags.Finite

/-! Finite Stone–von Neumann from an actual field-valued nondegenerate
commutator and a nontrivial additive character. This applies to supplied actual
central extensions in every characteristic, without assuming scalar
nondegeneracy, target dimensions, or a first intertwiner. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SymplecticHeisenbergUniqueness

open CentralExtension SymplecticCentralExtension
variable {K V H W U : Type*} [Field K] [AddCommGroup V] [Module K V] [Group H]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup U] [Module ℂ U]

omit [Module K V] in
/-- The stated additive central action is the actual unit-valued character action. -/
theorem central_action (D : Datum (Multiplicative K) H (Multiplicative V))
    (ψ : AddChar K ℂ) (σ : Representation ℂ H W)
    (hσ : ∀ t : K, σ (D.i (Multiplicative.ofAdd t)) = ψ t • LinearMap.id)
    (z : Multiplicative K) :
    σ (D.i z) = (scalarCharacter ψ z : ℂ) • LinearMap.id := hσ z.toAdd

variable [Fintype V]
variable (D : Datum (Multiplicative K) H (Multiplicative V))
variable (b : LinearMap.BilinForm K V) (hb : b.SeparatingLeft)
variable (hcomm : ∀ h k : H, centralCommutator D h k =
  Multiplicative.ofAdd (b (D.q h).toAdd (D.q k).toAdd))
variable (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
include D b hb hcomm ψ hψ

/-- Finite dimensionality follows for every actual irreducible representation
with the prescribed nontrivial central character. -/
theorem finiteDimensional (σ : Representation ℂ H W) [Representation.IsIrreducible σ]
    (hσ : ∀ t : K, σ (D.i (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    FiniteDimensional ℂ W :=
  CentralExtensionUniqueness.finiteDimensional D (scalarCharacter ψ)
    (radical_eq_bot_scalarCharacter D b hb hcomm ψ hψ) σ (central_action D ψ σ hσ)

/-- The dimension is the square root of the actual symplectic quotient order. -/
theorem finrank_sqrt (σ : Representation ℂ H W) [Representation.IsIrreducible σ]
    (hσ : ∀ t : K, σ (D.i (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    Module.finrank ℂ W = Nat.sqrt (Fintype.card V) := by
  simpa only [Fintype.card_multiplicative] using
    CentralExtensionUniqueness.finrank_sqrt D (scalarCharacter ψ)
      (radical_eq_bot_scalarCharacter D b hb hcomm ψ hψ) σ (central_action D ψ σ hσ)

/-- The first equivalence between any two such irreducibles is constructed.
Neither finite dimensionality nor an initial equivalence is assumed. -/
theorem exists_equiv (σ : Representation ℂ H W) (τ : Representation ℂ H U)
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ t : K, σ (D.i (Multiplicative.ofAdd t)) = ψ t • LinearMap.id)
    (hτ : ∀ t : K, τ (D.i (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    Nonempty (Representation.Equiv σ τ) :=
  CentralExtensionUniqueness.exists_equiv D (scalarCharacter ψ)
    (radical_eq_bot_scalarCharacter D b hb hcomm ψ hψ) σ τ
    (central_action D ψ σ hσ) (central_action D ψ τ hτ)

/-- The actual quotient order is a square, derived from the constructed algebra. -/
theorem card_eq_square : ∃ n : ℕ, 0 < n ∧ Fintype.card V = n ^ 2 := by
  obtain ⟨n, hn, hcard⟩ := TwistedMatrix.order_square
    (scalarCocycle D (scalarCharacter ψ)) (normalized_scalarCocycle D (scalarCharacter ψ))
    (radical_eq_bot_scalarCharacter D b hb hcomm ψ hψ)
  exact ⟨n, hn, by simpa only [Fintype.card_multiplicative] using hcard⟩

/-- An actual irreducible representation exists on an actual simple ideal of
the constructed twisted algebra, with the source central character and dimension. -/
theorem exists_irreducible :
    let B : Type _ := CentralCharacter.Algebra D (scalarCharacter ψ)
    letI : Ring B := inferInstance
    letI : Algebra ℂ B := inferInstance
    ∃ I : Ideal B, ∃ σ : Representation ℂ H I,
      Representation.IsIrreducible σ ∧
      (∀ t : K, σ (D.i (Multiplicative.ofAdd t)) = ψ t •
        (LinearMap.id : Module.End ℂ I)) ∧
      Module.finrank ℂ I = Nat.sqrt (Fintype.card V) := by
  obtain ⟨I, σ, hI, hc, hd⟩ := CentralExtensionExistence.exists_irreducible D
    (scalarCharacter ψ) (radical_eq_bot_scalarCharacter D b hb hcomm ψ hψ)
  refine ⟨I, σ, hI, ?_, ?_⟩
  · intro t
    exact hc (Multiplicative.ofAdd t)
  · simpa only [Fintype.card_multiplicative] using hd

end PaperXI.SymplecticHeisenbergUniqueness
