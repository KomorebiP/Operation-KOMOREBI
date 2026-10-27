import PaperXI.AbstractHeisenberg
import PaperXI.CentralExtensionCocycle
import PaperXI.SymplecticCentralExtension

/-! The actual commutator of the abstract odd-characteristic Heisenberg extension
is the supplied alternating form, independently of the chosen quotient section. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.AbstractHeisenberg

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable (b : LinearMap.BilinForm K V)

/-- The abstract symplectic pairing is the actual central preimage of the group commutator. -/
theorem centralCommutator_eq (hb : b.IsAlt) (h2 : (2 : K) ≠ 0) (h k : Element b) :
    CentralExtension.centralCommutator (datum b) h k =
      Multiplicative.ofAdd (b h.vector k.vector) := by
  apply (datum b).i_injective
  rw [CentralExtension.i_centralCommutator, commutator b hb h2]
  rfl

/-- Any central character evaluates the scalar cocycle commutator through the actual form. -/
theorem scalar_commutator (hb : b.IsAlt) (h2 : (2 : K) ≠ 0)
    (ζ : Multiplicative K →* ℂˣ) (v w : Multiplicative V) :
    CocycleCommutator.commutator (CentralExtension.scalarCocycle (datum b) ζ) v w =
      ζ (Multiplicative.ofAdd (b v.toAdd w.toAdd)) := by
  have h := CentralExtension.scalar_commutator (datum b) ζ
    (⟨v.toAdd, 0⟩ : Element b) (⟨w.toAdd, 0⟩ : Element b)
  simpa [centralCommutator_eq b hb h2] using h

/-- The nontrivial additive character detects the supplied abstract symplectic form.
No faithfulness of the character, coordinate identification, or finite target is assumed. -/
theorem scalar_radical_eq_bot (hb : b.IsAlt) (h2 : (2 : K) ≠ 0)
    (hsep : b.SeparatingLeft) (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (ζ : Multiplicative K →* ℂˣ)
    (hζ : ∀ t : K, (ζ (Multiplicative.ofAdd t) : ℂ) = ψ t) :
    CocycleCommutator.radical (CentralExtension.scalarCocycle (datum b) ζ) = ⊥ := by
  apply SymplecticCentralExtension.radical_eq_bot (datum b) b hsep _ ψ hψ ζ hζ
  intro h k
  simpa using centralCommutator_eq b hb h2 h k

/-- Scalar nondegeneracy for the canonical unit-valued form of the given additive character. -/
theorem scalar_radical_eq_bot_scalarCharacter (hb : b.IsAlt) (h2 : (2 : K) ≠ 0)
    (hsep : b.SeparatingLeft) (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) :
    CocycleCommutator.radical (CentralExtension.scalarCocycle (datum b)
      (SymplecticCentralExtension.scalarCharacter ψ)) = ⊥ :=
  scalar_radical_eq_bot b hb h2 hsep ψ hψ
    (SymplecticCentralExtension.scalarCharacter ψ)
    (SymplecticCentralExtension.scalarCharacter_ofAdd ψ)

/-- The distinguished scalar subgroup is proved to be the full center. -/
theorem center_eq_inclusion_range (hb : b.IsAlt) (h2 : (2 : K) ≠ 0)
    (hsep : b.SeparatingLeft) (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) :
    Subgroup.center (Element b) = (inclusion b).range :=
  CentralExtension.center_eq_range (datum b) (SymplecticCentralExtension.scalarCharacter ψ)
    (scalar_radical_eq_bot_scalarCharacter b hb h2 hsep ψ hψ)

end PaperXI.AbstractHeisenberg
