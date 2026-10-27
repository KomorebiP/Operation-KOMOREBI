import PaperXI.OddEnvelopeHeisenberg
import PaperXI.DyadicHeisenbergLift
import PaperXI.CliffordEnvelope

/-! Source-facing Corollary 9.9. The form comes from the actual Clifford
multiplicity cocycle. Odd characteristic uses its intrinsic half-form group;
characteristic two retains a declared quadratic refinement and constructs a
bilinear lift. No irreducible Heisenberg representation is supplied as input. -/
set_option autoImplicit false
set_option maxHeartbeats 800000
set_option maxRecDepth 3000
noncomputable section
namespace PaperXI.CliffordHeisenbergAttachment
open scoped IsMulCommutative
open BilinearHeisenberg

variable {G W X : Type*} [Group G] [Finite G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]
variable (hIso : CliffordIrreducible.Isotypic N ρ π) (hρ : CliffordDatum.Invariant N ρ)

section Odd
variable {p : ℕ} [Fact p.Prime] [Fact (∀ a : G ⧸ N, a ^ p = 1)]

def oddFactor : LinearMap.BilinForm (ZMod p) (CliffordEnvelope.Space N ρ π hIso hρ) :=
  OddEnvelopeHeisenberg.factor (CliffordEnvelope.form (p := p) N ρ π hIso hρ)

/-- The actual extension commutator recovers the actual Clifford commutator
on the original quotient representatives with the source's character convention. -/
theorem odd_commutator_on_classes (hp : p ≠ 2) (a b : G ⧸ N) :
    ZMod.stdAddChar ((CentralExtension.centralCommutator
      (datum (oddFactor (p := p) N ρ π hIso hρ))
      ⟨Additive.ofMul (QuotientGroup.mk a), 0⟩
      ⟨Additive.ofMul (QuotientGroup.mk b), 0⟩).toAdd) =
    ((CocycleCommutator.commutator (CliffordSource.cocycle N ρ π hIso hρ) a b : ℂˣ) : ℂ) := by
  rw [BilinearHeisenberg.centralCommutator]
  exact (congrArg (fun t : ZMod p => ZMod.stdAddChar t)
    (OddEnvelopeHeisenberg.factor_commutator
      (CliffordEnvelope.form (p := p) N ρ π hIso hρ)
      (CliffordEnvelope.form_isAlt N ρ π hIso hρ)
      (HeisenbergPrime.two_ne_zero hp)
      (Additive.ofMul (QuotientGroup.mk a))
      (Additive.ofMul (QuotientGroup.mk b)))).trans
    (CliffordEnvelope.form_on_classes N ρ π hIso hρ a b)

/-- Odd source 9.9: the group and an irreducible representation are constructed
from the intrinsic one-break envelope and the declared nontrivial central character. -/
theorem odd_exists (hp : p ≠ 2) (ψ : AddChar (ZMod p) ℂ) (hψ : ψ ≠ 1) :
    let c := oddFactor (p := p) N ρ π hIso hρ
    let B : Type _ := CentralCharacter.Algebra (datum c)
      (SymplecticCentralExtension.scalarCharacter ψ)
    letI : Ring B := inferInstance
    letI : Algebra ℂ B := inferInstance
    ∃ I : Ideal B, ∃ σ : Representation ℂ (Element c) I,
      Representation.IsIrreducible σ ∧
      (∀ t : ZMod p, σ (i c (Multiplicative.ofAdd t)) = ψ t •
        (LinearMap.id : Module.End ℂ I)) ∧
      Module.finrank ℂ I = Nat.sqrt (Nat.card (CliffordEnvelope.Space N ρ π hIso hρ)) := by
  let : Fintype (CliffordEnvelope.Space N ρ π hIso hρ) := Fintype.ofFinite _
  simpa only [Nat.card_eq_fintype_card] using
    BilinearHeisenberg.exists_irreducible (oddFactor (p := p) N ρ π hIso hρ)
      (CliffordEnvelope.form (p := p) N ρ π hIso hρ)
      (OddEnvelopeHeisenberg.factor_commutator _ (CliffordEnvelope.form_isAlt N ρ π hIso hρ)
        (HeisenbergPrime.two_ne_zero hp))
      (CliffordEnvelope.form_nondegenerate (p := p) N ρ π hIso hρ).1 ψ hψ

variable {U U' : Type*} [AddCommGroup U] [Module ℂ U] [AddCommGroup U'] [Module ℂ U']

/-- The first comparison equivalence is a conclusion, on the constructed odd group. -/
theorem odd_unique (hp : p ≠ 2) (ψ : AddChar (ZMod p) ℂ) (hψ : ψ ≠ 1)
    (σ : Representation ℂ (Element (oddFactor (p := p) N ρ π hIso hρ)) U)
    (τ : Representation ℂ (Element (oddFactor (p := p) N ρ π hIso hρ)) U')
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ t, σ (i _ (Multiplicative.ofAdd t)) = ψ t • LinearMap.id)
    (hτ : ∀ t, τ (i _ (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    Nonempty (Representation.Equiv σ τ) := by
  let : Fintype (CliffordEnvelope.Space N ρ π hIso hρ) := Fintype.ofFinite _
  exact BilinearHeisenberg.exists_equiv (oddFactor (p := p) N ρ π hIso hρ)
    (CliffordEnvelope.form (p := p) N ρ π hIso hρ)
    (OddEnvelopeHeisenberg.factor_commutator _ (CliffordEnvelope.form_isAlt N ρ π hIso hρ)
      (HeisenbergPrime.two_ne_zero hp))
    (CliffordEnvelope.form_nondegenerate (p := p) N ρ π hIso hρ).1 ψ hψ σ τ hσ hτ

end Odd

section Dyadic
variable [Fact (∀ a : G ⧸ N, a ^ (2 : ℕ) = 1)]

def dyadicFactor (Q : DyadicAffine.Refinement (CliffordEnvelope.form (p := 2) N ρ π hIso hρ)) :
    LinearMap.BilinForm (ZMod 2) (CliffordEnvelope.Space N ρ π hIso hρ) :=
  DyadicHeisenbergLift.factor (CliffordEnvelope.form (p := 2) N ρ π hIso hρ)
    (CliffordEnvelope.form_isAlt N ρ π hIso hρ)
    (CliffordEnvelope.form_nondegenerate (p := 2) N ρ π hIso hρ).1 Q

/-- The declared refinement is exactly the square of each quotient lift. -/
theorem dyadic_square (Q : DyadicAffine.Refinement
    (CliffordEnvelope.form (p := 2) N ρ π hIso hρ))
    (h : Element (dyadicFactor N ρ π hIso hρ Q)) :
    h * h = i (dyadicFactor N ρ π hIso hρ Q) (Multiplicative.ofAdd (Q.value h.vector)) :=
  DyadicHeisenbergLift.square_profile _ _ _ Q h

/-- Dyadic source 9.9 at its corrected contract: the square-refined group and
its irreducible representation are constructed, not assumed. -/
theorem dyadic_exists (Q : DyadicAffine.Refinement
    (CliffordEnvelope.form (p := 2) N ρ π hIso hρ))
    (ψ : AddChar (ZMod 2) ℂ) (hψ : ψ ≠ 1) :
    let c := dyadicFactor N ρ π hIso hρ Q
    let B : Type _ := CentralCharacter.Algebra (datum c)
      (SymplecticCentralExtension.scalarCharacter ψ)
    letI : Ring B := inferInstance
    letI : Algebra ℂ B := inferInstance
    ∃ I : Ideal B, ∃ σ : Representation ℂ (Element c) I,
      Representation.IsIrreducible σ ∧
      (∀ t : ZMod 2, σ (i c (Multiplicative.ofAdd t)) = ψ t •
        (LinearMap.id : Module.End ℂ I)) ∧
      Module.finrank ℂ I = Nat.sqrt (Nat.card (CliffordEnvelope.Space N ρ π hIso hρ)) := by
  let : Fintype (CliffordEnvelope.Space N ρ π hIso hρ) := Fintype.ofFinite _
  simpa only [Nat.card_eq_fintype_card] using
    BilinearHeisenberg.exists_irreducible (dyadicFactor N ρ π hIso hρ Q)
      (CliffordEnvelope.form (p := 2) N ρ π hIso hρ)
      (DyadicHeisenbergLift.factor_commutator _ _ _ Q)
      (CliffordEnvelope.form_nondegenerate (p := 2) N ρ π hIso hρ).1 ψ hψ

variable {U U' : Type*} [AddCommGroup U] [Module ℂ U] [AddCommGroup U'] [Module ℂ U']

theorem dyadic_unique (Q : DyadicAffine.Refinement
    (CliffordEnvelope.form (p := 2) N ρ π hIso hρ))
    (ψ : AddChar (ZMod 2) ℂ) (hψ : ψ ≠ 1)
    (σ : Representation ℂ (Element (dyadicFactor N ρ π hIso hρ Q)) U)
    (τ : Representation ℂ (Element (dyadicFactor N ρ π hIso hρ Q)) U')
    [Representation.IsIrreducible σ] [Representation.IsIrreducible τ]
    (hσ : ∀ t, σ (i _ (Multiplicative.ofAdd t)) = ψ t • LinearMap.id)
    (hτ : ∀ t, τ (i _ (Multiplicative.ofAdd t)) = ψ t • LinearMap.id) :
    Nonempty (Representation.Equiv σ τ) := by
  let : Fintype (CliffordEnvelope.Space N ρ π hIso hρ) := Fintype.ofFinite _
  exact BilinearHeisenberg.exists_equiv (dyadicFactor N ρ π hIso hρ Q)
    (CliffordEnvelope.form (p := 2) N ρ π hIso hρ)
    (DyadicHeisenbergLift.factor_commutator _ _ _ Q)
    (CliffordEnvelope.form_nondegenerate (p := 2) N ρ π hIso hρ).1 ψ hψ σ τ hσ hτ

end Dyadic
end PaperXI.CliffordHeisenbergAttachment
