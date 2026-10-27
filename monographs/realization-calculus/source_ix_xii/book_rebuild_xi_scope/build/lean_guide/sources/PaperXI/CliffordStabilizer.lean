import PaperXI.CliffordDatum
import PaperXI.CliffordSource
import PaperXI.CliffordEnvelope
import PaperXI.CliffordTransport
import PaperXI.ElementaryEnvelopeTransport
import Mathlib.GroupTheory.QuotientGroup.Basic

/-! The honest action induced on a normal quotient by ambient group
automorphisms. No coherent choices of representation intertwiners enter. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordStabilizer
open CocycleCommutator
open scoped IsMulCommutative

variable {G C : Type*} [Group G] [Group C]

/-- Actual ambient automorphisms preserving a normal subgroup give an honest
quotient action. Its group law is inherited from the ambient action. -/
def quotientAction (N : Subgroup G) [N.Normal] (α : C →* MulAut G)
    (hN : ∀ g, N.map (α g).toMonoidHom = N) : C →* MulAut (G ⧸ N) where
  toFun g := QuotientGroup.congr N N (α g) (hN g)
  map_one' := by
    ext x
    induction x using QuotientGroup.induction_on with | H a =>
      change QuotientGroup.mk (α 1 a) = QuotientGroup.mk a
      rw [map_one]
      rfl
  map_mul' g h := by
    ext x
    induction x using QuotientGroup.induction_on with | H a =>
      change QuotientGroup.mk (α (g * h) a) = QuotientGroup.mk (α g (α h a))
      rw [map_mul]
      rfl

@[simp] theorem quotientAction_mk (N : Subgroup G) [N.Normal] (α : C →* MulAut G)
    (hN : ∀ g, N.map (α g).toMonoidHom = N) (g : C) (a : G) :
    quotientAction N α hN g (QuotientGroup.mk a) = QuotientGroup.mk (α g a) := rfl

/-- The induced quotient action intertwines the original quotient homomorphism. -/
theorem quotientAction_comp (N : Subgroup G) [N.Normal] (α : C →* MulAut G)
    (hN : ∀ g, N.map (α g).toMonoidHom = N) (g : C) :
    (quotientAction N α hN g).toMonoidHom.comp (QuotientGroup.mk' N) =
      (QuotientGroup.mk' N).comp (α g).toMonoidHom := rfl

/-- No auxiliary representation choices can change the induced quotient action. -/
theorem quotientAction_unique (N : Subgroup G) [N.Normal] (α : C →* MulAut G)
    (hN : ∀ g, N.map (α g).toMonoidHom = N) (β : C →* MulAut (G ⧸ N))
    (hβ : ∀ g a, β g (QuotientGroup.mk a) = QuotientGroup.mk (α g a)) :
    β = quotientAction N α hN := by
  apply MonoidHom.ext
  intro g
  ext x
  induction x using QuotientGroup.induction_on with | H a => exact hβ g a

section Envelope
variable {p : ℕ} [Fact p.Prime]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
variable [Fact (∀ a : G ⧸ N, a ^ p = 1)]
variable (c : Cocycle (G ⧸ N) ℂˣ) (α : C →* MulAut G)
variable (hN : ∀ g, N.map (α g).toMonoidHom = N)
variable (hα : ∀ g a b, commutator c (quotientAction N α hN g a)
  (quotientAction N α hN g b) = commutator c a b)

/-- The ambient quotient action descends further to the actual linear envelope
once preservation of its intrinsic scalar pairing has been established. -/
def envelopeAction : C →* (ElementaryEnvelope.Space c ≃ₗ[ZMod p] ElementaryEnvelope.Space c) :=
  ElementaryEnvelope.action c (quotientAction N α hN) hα

@[simp] theorem envelopeAction_mk (g : C) (a : G) :
    envelopeAction (p := p) N c α hN hα g
      (Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N a))) =
      Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N (α g a))) := rfl

/-- Every induced envelope automorphism preserves its actual alternating form. -/
theorem envelopeAction_form (g : C) (x y : ElementaryEnvelope.Space c) :
    ElementaryEnvelope.form (p := p) c
      (envelopeAction (p := p) N c α hN hα g x)
      (envelopeAction (p := p) N c α hN hα g y) =
      ElementaryEnvelope.form (p := p) c x y :=
  ElementaryEnvelope.action_form c (quotientAction N α hN) hα g x y

end Envelope
section Equivariance
variable {G' : Type*} [Group G'] {p : ℕ} [Fact p.Prime]

/-- Isomorphisms intertwining the original ambient actions intertwine the
constructed linear envelope actions on every quotient vector. -/
theorem envelopeAction_equivariant
    (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
    (N' : Subgroup G') [N'.Normal] [IsMulCommutative (G' ⧸ N')]
    [Fact (∀ a : G ⧸ N, a ^ p = 1)] [Fact (∀ a : G' ⧸ N', a ^ p = 1)]
    (c : Cocycle (G ⧸ N) ℂˣ) (d : Cocycle (G' ⧸ N') ℂˣ)
    (α : C →* MulAut G) (β : C →* MulAut G')
    (hN : ∀ g, N.map (α g).toMonoidHom = N)
    (hN' : ∀ g, N'.map (β g).toMonoidHom = N')
    (hα : ∀ g a b, commutator c (quotientAction N α hN g a)
      (quotientAction N α hN g b) = commutator c a b)
    (hβ : ∀ g a b, commutator d (quotientAction N' β hN' g a)
      (quotientAction N' β hN' g b) = commutator d a b)
    (e : G ≃* G') (heN : N.map e.toMonoidHom = N')
    (he : ∀ a b, commutator d (CliffordTransport.quotientEquiv N N' e heN a)
      (CliffordTransport.quotientEquiv N N' e heN b) = commutator c a b)
    (hEquiv : ∀ g a, e (α g a) = β g (e a))
    (g : C) (x : ElementaryEnvelope.Space c) :
    ElementaryEnvelope.linearEquiv (p := p) c d
      (CliffordTransport.quotientEquiv N N' e heN) he
      (envelopeAction (p := p) N c α hN hα g x) =
    envelopeAction (p := p) N' d β hN' hβ g
      (ElementaryEnvelope.linearEquiv (p := p) c d
        (CliffordTransport.quotientEquiv N N' e heN) he x) := by
  apply ElementaryEnvelope.space_induction_on c x
  intro a
  induction a using QuotientGroup.induction_on with | H t =>
    change Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N' (e (α g t)))) =
      Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N' (β g (e t))))
    rw [hEquiv]

end Equivariance

section Source
variable {W X : Type*} [AddCommGroup W] [Module ℂ W]
variable [AddCommGroup X] [Module ℂ X] [Finite G]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
variable (ρ : Representation ℂ N W) (π : Representation ℂ G X)
variable [Representation.IsIrreducible ρ] [Representation.IsIrreducible π]
variable (hIso : CliffordIrreducible.Isotypic N ρ π) (hρ : CliffordDatum.Invariant N ρ)
variable (α : C →* MulAut G) (hN : ∀ g, N.map (α g).toMonoidHom = N)
variable (E : ∀ g, Representation.Equiv ρ
  (ρ.comp (CliffordTransport.subgroupEquiv N N (α g) (hN g)).toMonoidHom))
variable (F : ∀ g, Representation.Equiv π (π.comp (α g).toMonoidHom))

include E F

/-- Actual automorphisms of the original representation datum preserve the
intrinsic Clifford commutator. The comparison intertwiners need no group law. -/
theorem source_commutator_preserved (g : C) (a b : G ⧸ N) :
    commutator (CliffordSource.cocycle N ρ π hIso hρ)
      (quotientAction N α hN g a) (quotientAction N α hN g b) =
      commutator (CliffordSource.cocycle N ρ π hIso hρ) a b := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : Nontrivial (CliffordMultiplicity.Space N ρ π) :=
    CliffordIrreducible.multiplicity_nontrivial N ρ π hIso
  exact CliffordTransport.commutator_preserved N N (α g) (hN g)
    ρ ρ π π (E g) (F g) hρ hρ a b

variable {p : ℕ} [Fact p.Prime] [Fact (∀ a : G ⧸ N, a ^ p = 1)]

/-- Source 9.8: the original datum automorphisms give a genuine linear action
on the actual Clifford envelope. Auxiliary intertwiners are only witnesses. -/
def sourceAction : C →*
    (ElementaryEnvelope.Space (CliffordSource.cocycle N ρ π hIso hρ) ≃ₗ[ZMod p]
      ElementaryEnvelope.Space (CliffordSource.cocycle N ρ π hIso hρ)) :=
  envelopeAction N (CliffordSource.cocycle N ρ π hIso hρ) α hN
    (source_commutator_preserved N ρ π hIso hρ α hN E F)

@[simp] theorem sourceAction_mk (g : C) (a : G) :
    sourceAction (p := p) N ρ π hIso hρ α hN E F g
      (Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N a))) =
      Additive.ofMul (QuotientGroup.mk (QuotientGroup.mk' N (α g a))) := rfl

/-- Every actual stabilizer element preserves the constructed symplectic form. -/
theorem sourceAction_form (g : C)
    (x y : ElementaryEnvelope.Space (CliffordSource.cocycle N ρ π hIso hρ)) :
    ElementaryEnvelope.form (p := p) (CliffordSource.cocycle N ρ π hIso hρ)
      (sourceAction (p := p) N ρ π hIso hρ α hN E F g x)
      (sourceAction (p := p) N ρ π hIso hρ α hN E F g y) =
      ElementaryEnvelope.form (p := p) (CliffordSource.cocycle N ρ π hIso hρ) x y :=
  envelopeAction_form N (CliffordSource.cocycle N ρ π hIso hρ) α hN
    (source_commutator_preserved N ρ π hIso hρ α hN E F) g x y

/-- Changing the individual representation comparison witnesses leaves the
genuine envelope action unchanged, even without coherent witness choices. -/
theorem sourceAction_independent
    (E' : ∀ g, Representation.Equiv ρ
      (ρ.comp (CliffordTransport.subgroupEquiv N N (α g) (hN g)).toMonoidHom))
    (F' : ∀ g, Representation.Equiv π (π.comp (α g).toMonoidHom)) :
    sourceAction (p := p) N ρ π hIso hρ α hN E F =
      sourceAction (p := p) N ρ π hIso hρ α hN E' F' := rfl

section Transport
variable {G' W' X' : Type*} [Group G'] [Finite G']
variable [AddCommGroup W'] [Module ℂ W'] [AddCommGroup X'] [Module ℂ X']
variable (N' : Subgroup G') [N'.Normal] [IsMulCommutative (G' ⧸ N')]
variable (ρ' : Representation ℂ N' W') (π' : Representation ℂ G' X')
variable [Representation.IsIrreducible ρ'] [Representation.IsIrreducible π']
variable (hIso' : CliffordIrreducible.Isotypic N' ρ' π') (hρ' : CliffordDatum.Invariant N' ρ')
variable [Fact (∀ a : G' ⧸ N', a ^ p = 1)]
variable (β : C →* MulAut G') (hN' : ∀ g, N'.map (β g).toMonoidHom = N')
variable (E' : ∀ g, Representation.Equiv ρ'
  (ρ'.comp (CliffordTransport.subgroupEquiv N' N' (β g) (hN' g)).toMonoidHom))
variable (F' : ∀ g, Representation.Equiv π' (π'.comp (β g).toMonoidHom))
variable (e : G ≃* G') (heN : N.map e.toMonoidHom = N')
variable (E₀ : Representation.Equiv ρ
  (ρ'.comp (CliffordTransport.subgroupEquiv N N' e heN).toMonoidHom))
variable (F₀ : Representation.Equiv π (π'.comp e.toMonoidHom))

/-- The source datum isometry is equivariant for the actual stabilizer actions
whenever the original ambient datum isomorphism intertwines those actions. -/
theorem sourceAction_equivariant (hEquiv : ∀ g a, e (α g a) = β g (e a))
    (g : C) (x : CliffordEnvelope.Space N ρ π hIso hρ) :
    CliffordEnvelope.equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e heN E₀ F₀
      (sourceAction (p := p) N ρ π hIso hρ α hN E F g x) =
    sourceAction (p := p) N' ρ' π' hIso' hρ' β hN' E' F' g
      (CliffordEnvelope.equiv (p := p) N ρ π hIso hρ N' ρ' π' hIso' hρ' e heN E₀ F₀ x) := by
  exact envelopeAction_equivariant N N'
    (CliffordSource.cocycle N ρ π hIso hρ) (CliffordSource.cocycle N' ρ' π' hIso' hρ')
    α β hN hN'
    (source_commutator_preserved N ρ π hIso hρ α hN E F)
    (source_commutator_preserved N' ρ' π' hIso' hρ' β hN' E' F')
    e heN (CliffordEnvelope.commutator_preserved N ρ π hIso hρ
      N' ρ' π' hIso' hρ' e heN E₀ F₀) hEquiv g x

end Transport
end Source
end PaperXI.CliffordStabilizer
