import PaperXI.CliffordSource
import PaperXI.CliffordTransport
import PaperXI.ElementaryEnvelopeTransport

/-! The actual elementary commutator envelope of the source Clifford datum.
No cocycle, projective operator family, bilinear form or transport on the
multiplicity space is supplied in place of its construction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordEnvelope
open CocycleCommutator
open scoped IsMulCommutative

variable {G W X : Type*} [Group G] [Finite G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]
variable (hIso : CliffordIrreducible.Isotypic N ρ π) (hρ : CliffordDatum.Invariant N ρ)
variable {p : ℕ} [Fact (∀ a : G ⧸ N, a ^ p = 1)]

/-- The actual scalar commutator, bundled in the pth roots of unity. -/
def pairing : (G ⧸ N) →* ((G ⧸ N) →* rootsOfUnity p ℂ) :=
  ElementaryEnvelope.rootCommutator (CliffordSource.cocycle N ρ π hIso hρ) Fact.out

@[simp] theorem pairing_coe (a b : G ⧸ N) :
    (pairing (p := p) N ρ π hIso hρ a b : ℂˣ) =
      (CliffordSource.cocycle N ρ π hIso hρ).coeff a b /
        (CliffordSource.cocycle N ρ π hIso hρ).coeff b a := rfl

theorem pairing_self (a : G ⧸ N) : pairing (p := p) N ρ π hIso hρ a a = 1 :=
  ElementaryEnvelope.rootCommutator_self _ _ a

/-- The original Clifford datum's actual additive radical quotient. -/
abbrev Space := ElementaryEnvelope.Space (CliffordSource.cocycle N ρ π hIso hρ)

variable [Fact p.Prime]

/-- The form is constructed by the fixed standard additive character. -/
def form : LinearMap.BilinForm (ZMod p) (Space N ρ π hIso hρ) :=
  ElementaryEnvelope.form (CliffordSource.cocycle N ρ π hIso hρ)

theorem form_isAlt : (form (p := p) N ρ π hIso hρ).IsAlt :=
  ElementaryEnvelope.form_isAlt _

theorem form_nondegenerate : (form (p := p) N ρ π hIso hρ).Nondegenerate :=
  ElementaryEnvelope.form_nondegenerate _

theorem finiteDimensional : FiniteDimensional (ZMod p) (Space N ρ π hIso hρ) :=
  inferInstance

/-- The constructed prime-field form recovers the actual multiplicity commutator
on every pair of original quotient representatives. -/
theorem form_on_classes (a b : G ⧸ N) :
    ZMod.stdAddChar (form (p := p) N ρ π hIso hρ
      (Additive.ofMul (QuotientGroup.mk a)) (Additive.ofMul (QuotientGroup.mk b))) =
      ((CocycleCommutator.commutator (CliffordSource.cocycle N ρ π hIso hρ) a b : ℂˣ) : ℂ) :=
  ElementaryEnvelope.form_stdAddChar _ _ _

section Transport
variable {G' W' X' : Type*} [Group G'] [Finite G']
variable [AddCommGroup W'] [Module ℂ W'] [AddCommGroup X'] [Module ℂ X']
variable (N' : Subgroup G') [N'.Normal] [IsMulCommutative (G' ⧸ N')]
variable (ρ' : Representation ℂ N' W') (π' : Representation ℂ G' X')
variable [Representation.IsIrreducible ρ'] [Representation.IsIrreducible π']
variable (hIso' : CliffordIrreducible.Isotypic N' ρ' π') (hρ' : CliffordDatum.Invariant N' ρ')
variable [Fact (∀ a : G' ⧸ N', a ^ p = 1)]
variable (e : G ≃* G') (hN : N.map e.toMonoidHom = N')
variable (E : Representation.Equiv ρ
  (ρ'.comp (CliffordTransport.subgroupEquiv N N' e hN).toMonoidHom))
variable (F : Representation.Equiv π (π'.comp e.toMonoidHom))

include E F

/-- Actual isomorphisms of the original subgroup and ambient representations
preserve the intrinsic scalar pairing. -/
theorem commutator_preserved (a b : G ⧸ N) :
    commutator (CliffordSource.cocycle N' ρ' π' hIso' hρ')
      (CliffordTransport.quotientEquiv N N' e hN a)
      (CliffordTransport.quotientEquiv N N' e hN b) =
      commutator (CliffordSource.cocycle N ρ π hIso hρ) a b := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ W' := FiniteRepresentation.finiteDimensional ρ'
  let : Nontrivial (CliffordMultiplicity.Space N ρ π) :=
    CliffordIrreducible.multiplicity_nontrivial N ρ π hIso
  let : Nontrivial (CliffordMultiplicity.Space N' ρ' π') :=
    CliffordIrreducible.multiplicity_nontrivial N' ρ' π' hIso'
  exact CliffordTransport.commutator_preserved N N' e hN ρ ρ' π π' E F hρ hρ' a b

/-- The actual datum isomorphism also preserves the cocycle class, witnessed
by a constructed normalized scalar cochain on the actual quotient. -/
theorem exists_normalized_cochain :
    ∃ s : (G ⧸ N) → ℂˣ, s 1 = 1 ∧ ∀ a b : G ⧸ N,
      (CliffordSource.cocycle N' ρ' π' hIso' hρ').coeff
        (CliffordTransport.quotientEquiv N N' e hN a)
        (CliffordTransport.quotientEquiv N N' e hN b) =
      s a * s b / s (a * b) * (CliffordSource.cocycle N ρ π hIso hρ).coeff a b := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ W' := FiniteRepresentation.finiteDimensional ρ'
  let : Nontrivial (CliffordMultiplicity.Space N ρ π) :=
    CliffordIrreducible.multiplicity_nontrivial N ρ π hIso
  let : Nontrivial (CliffordMultiplicity.Space N' ρ' π') :=
    CliffordIrreducible.multiplicity_nontrivial N' ρ' π' hIso'
  exact ⟨CliffordTransport.cochain N N' e hN ρ ρ' E hρ hρ',
    CliffordTransport.cochain_one N N' e hN ρ ρ' π π' E F hρ hρ',
    CliffordTransport.cocycle_transport N N' e hN ρ ρ' π π' E F hρ hρ'⟩

omit [Fact p.Prime] in
/-- The target μp-valued bicharacter is the transport of the source one. -/
theorem pairing_preserved (a b : G ⧸ N) :
    pairing (p := p) N' ρ' π' hIso' hρ'
      (CliffordTransport.quotientEquiv N N' e hN a)
      (CliffordTransport.quotientEquiv N N' e hN b) =
      pairing (p := p) N ρ π hIso hρ a b :=
  Subtype.ext (commutator_preserved N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E F a b)

/-- The actual datum map induces the prime-field equivalence of its constructed envelopes. -/
def equiv : Space N ρ π hIso hρ ≃ₗ[ZMod p] Space N' ρ' π' hIso' hρ' :=
  ElementaryEnvelope.linearEquiv
    (CliffordSource.cocycle N ρ π hIso hρ) (CliffordSource.cocycle N' ρ' π' hIso' hρ')
    (CliffordTransport.quotientEquiv N N' e hN)
    (commutator_preserved N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E F)

@[simp] theorem equiv_mk (a : G) :
    equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E F
      (Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N a))) =
      Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N' (e a))) := rfl

/-- Source 9.7: the map induced by an isomorphism of the actual Clifford data
is an isometry for the same standard root-coordinate convention. -/
theorem equiv_form (x y : Space N ρ π hIso hρ) :
    form (p := p) N' ρ' π' hIso' hρ'
      (equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E F x)
      (equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E F y) =
      form (p := p) N ρ π hIso hρ x y :=
  ElementaryEnvelope.linearEquiv_form _ _ _ _ x y

/-- Auxiliary representation equivalences do not change the induced quotient map. -/
theorem equiv_independent
    (E' : Representation.Equiv ρ
      (ρ'.comp (CliffordTransport.subgroupEquiv N N' e hN).toMonoidHom))
    (F' : Representation.Equiv π (π'.comp e.toMonoidHom)) :
    equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E F =
      equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e hN E' F' := rfl

end Transport
end PaperXI.CliffordEnvelope
