import PaperX.IrreducibleCharacterRigidity
import PaperX.CofiniteConjugacyCoverage

/-! Isomorphism at one coefficient prime reflects componentwise isomorphism
of compatible irreducible systems. Comparisons use each pair's good-place
overlap. Arithmetic Frobenius density is still an explicit input. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CompatibleSystemRigidity
open PaperX.IrreducibleCharacterRigidity

variable {Λ I G X E : Type*} [Group G] [Field E] [TopologicalSpace G]
variable {K : Λ → Type*} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
  [∀ l, TopologicalSpace (K l)] [∀ l, T2Space (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)] [∀ l i, FiniteDimensional (K l) (W l i)]
variable (ρ : (l : Λ) → (i : I) → Representation (K l) G (W l i))
variable [∀ l i, (ρ l i).IsIrreducible]
variable (hc : ∀ l i, Continuous (ρ l i).character)
variable (emb : (l : Λ) → E →+* K l) (t : I → X → E)
variable (good : Λ → X → Prop) (s : X → G)
variable (compat : ∀ l i x, good l x → (ρ l i).character (s x) = emb l (t i x))
variable (overlap : ∀ l m, DenseRange
  (fun p : {x : X // good l x ∧ good m x} × G => p.2 * s p.1 * p.2⁻¹))

/-- Equivalence of systems means actual representation equivalence at every
coefficient index, not equality of optional labels or record fields. -/
def MemberwiseEquiv (i j : I) : Prop := ∀ l, Nonempty ((ρ l i).Equiv (ρ l j))

include compat in
/-- An isomorphism reflects common algebraic trace equality at all places good
for that member, because the coefficient-field embedding is injective. -/
theorem common_trace_eq_of_member_equiv (l : Λ) (i j : I)
    (h : Nonempty ((ρ l i).Equiv (ρ l j))) (x : X) (hx : good l x) :
    t i x = t j x := by
  apply (emb l).injective
  rw [← compat l i x hx, ← compat l j x hx]
  exact congrFun (character_eq_of_equiv (ρ l i) (ρ l j) h) (s x)

include hc compat overlap in
/-- Common trace agreement on one member's good set propagates to actual
isomorphisms at every member, using the appropriate good-place overlaps. -/
theorem memberwiseEquiv_of_common_traces (l₀ : Λ) (i j : I)
    (ht : ∀ x, good l₀ x → t i x = t j x) : MemberwiseEquiv ρ i j := by
  intro l
  apply equiv_of_dense_character_eq (ρ l i) (ρ l j) (hc l i) (hc l j)
    (fun x : {x : X // good l₀ x ∧ good l x} => s x) (overlap l₀ l)
  intro x
  rw [compat l i x x.property.2, compat l j x x.property.2,
    ht x x.property.1]

include hc compat overlap in
/-- The previously missing system-to-member bridge, at the exact componentwise
notion of equivalence and with overlap density explicitly retained. -/
theorem memberwiseEquiv_of_member (l₀ : Λ) (i j : I)
    (h : Nonempty ((ρ l₀ i).Equiv (ρ l₀ j))) : MemberwiseEquiv ρ i j := by
  apply memberwiseEquiv_of_common_traces ρ hc emb t good s compat overlap l₀ i j
  exact common_trace_eq_of_member_equiv ρ emb t good s compat l₀ i j h

include hc compat overlap in
theorem memberwiseEquiv_iff_member (l₀ : Λ) (i j : I) :
    MemberwiseEquiv ρ i j ↔ Nonempty ((ρ l₀ i).Equiv (ρ l₀ j)) :=
  ⟨fun h => h l₀, memberwiseEquiv_of_member ρ hc emb t good s compat overlap l₀ i j⟩

include hc compat overlap in
/-- Pairwise nonisomorphic systems give pairwise nonisomorphic representations
at any selected coefficient prime. This is derived rather than assumed twice. -/
theorem nonisomorphic_members (hne : ∀ i j, MemberwiseEquiv ρ i j → i = j)
    (l₀ : Λ) : ∀ i j, Nonempty ((ρ l₀ i).Equiv (ρ l₀ j)) → i = j := by
  intro i j h
  exact hne i j (memberwiseEquiv_of_member ρ hc emb t good s compat overlap l₀ i j h)

end PaperX.CompatibleSystemRigidity
