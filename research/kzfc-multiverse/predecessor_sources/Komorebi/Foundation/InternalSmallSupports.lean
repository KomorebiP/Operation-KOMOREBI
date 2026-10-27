import Komorebi.Foundation.InternalFineCompactness

/-!
# Internal small supports and the cardinal-arithmetic boundary

All graphs, subsets, families and unions here are elements of the model.
SmallUnionClosed and SmallProductClosed are explicit mathematical predicates,
not new fields of AxiomSemantics and not postulated axioms.
-/

universe u v

namespace Komorebi.InternalSmallSupports

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport InternalConstraints InternalUltrafilterSelection InternalFineCompactness

variable {M : Type u} [language.Structure M]

/-- Inclusion has an internally constructed identity graph. -/
theorem embeds_of_subset (h : AxiomSemantics M) {x y : M} (hxy : subset x y) :
    Embeds x y := by
  let φ : language.Formula (Option (Option (Fin 0))) := eqF none (some none)
  obtain ⟨g,p,hp,hgp,hg⟩ := relationSet_exists h φ ![] x y
  have hg' : ∀ a b : M, PairMember a b g ↔ member a x ∧ member b y ∧ a = b := by
    intro a b
    simpa [φ,assign] using hg a b
  refine ⟨g,⟨⟨p,hp,hgp⟩,?_⟩,?_⟩
  · intro a ha
    exact ⟨a,(hg' a a).mpr ⟨ha,hxy a ha,rfl⟩,
      fun b hb => ((hg' a b).mp hb).2.2.symm⟩
  · intro a _ b _ c hac hbc
    exact ((hg' a c).mp hac).2.2.trans ((hg' b c).mp hbc).2.2.symm

theorem small_of_subset (h : AxiomSemantics M) {k x y : M}
    (hxy : subset x y) (hy : Small k y) : Small k x :=
  small_of_embeds h (embeds_of_subset h hxy) hy

theorem member_small (h : AxiomSemantics M) {k a : M} (ha : member a k) :
    Small k a := ⟨a,ha,embeds_of_subset h (fun _ hz => hz)⟩

theorem empty_small (h : AxiomSemantics M) {k e : M}
    (hk : HasInductiveMember k) (he : IsEmpty e) : Small k e := by
  obtain ⟨w,hw,_⟩ := hk
  exact ⟨w,hw,embeds_of_subset h (fun z hz => False.elim (he z hz))⟩

/-- A pair embeds into the internally existing inductive member, even when its
entries coincide. The graph is obtained by an actual Separation instance. -/
theorem pair_small (h : AxiomSemantics M) {k p x y : M}
    (hk : HasInductiveMember k) (hp : IsPair p x y) : Small k p := by
  classical
  obtain ⟨w,hw,⟨⟨z,hz,hzw⟩,hsucc⟩⟩ := hk
  obtain ⟨o,ho,how⟩ := hsucc z hzw
  have hzo : z ≠ o := by
    intro he
    have hmem : member z o := (ho z).mpr (Or.inl rfl)
    exact hz z (he.symm ▸ hmem)
  let φ : language.Formula (Option (Option (Fin 3))) :=
    (eqF none (some (some 0)) ⊓ eqF (some none) (some (some 1))) ⊔
      ((eqF none (some (some 0))).not ⊓ eqF (some none) (some (some 2)))
  obtain ⟨g,b,hb,hgb,hg⟩ := relationSet_exists h φ ![x,z,o] p w
  have hg' : ∀ a c : M, PairMember a c g ↔ member a p ∧ member c w ∧
      ((a = x ∧ c = z) ∨ (a ≠ x ∧ c = o)) := by
    intro a c
    simpa [φ,assign] using hg a c
  refine ⟨w,hw,g,⟨⟨b,hb,hgb⟩,?_⟩,?_⟩
  · intro a ha
    by_cases hax : a = x
    · refine ⟨z,(hg' a z).mpr ⟨ha,hzw,Or.inl ⟨hax,rfl⟩⟩,?_⟩
      intro c hc
      rcases ((hg' a c).mp hc).2.2 with hc | hc
      · exact hc.2
      · exact False.elim (hc.1 hax)
    · refine ⟨o,(hg' a o).mpr ⟨ha,how,Or.inr ⟨hax,rfl⟩⟩,?_⟩
      intro c hc
      rcases ((hg' a c).mp hc).2.2 with hc | hc
      · exact False.elim (hax hc.1)
      · exact hc.2
  · intro a ha b hb c hac hbc
    rcases ((hg' a c).mp hac).2.2 with ha' | ha'
    · rcases ((hg' b c).mp hbc).2.2 with hb' | hb'
      · exact ha'.1.trans hb'.1.symm
      · exact False.elim (hzo (ha'.2.symm.trans hb'.2))
    · rcases ((hg' b c).mp hbc).2.2 with hb' | hb'
      · exact False.elim (hzo (hb'.2.symm.trans ha'.2))
      · have hay : a = y := ((hp a).mp ha).resolve_left ha'.1
        have hby : b = y := ((hp b).mp hb).resolve_left hb'.1
        exact hay.trans hby.symm

theorem singleton_small (h : AxiomSemantics M) {k s x : M}
    (hk : HasInductiveMember k) (hs : IsSingleton s x) : Small k s :=
  pair_small (x := x) (y := x) h hk (fun z => (hs z).trans (Iff.of_eq (or_self _).symm))

/-- Internal union closure is a set-quantified property. No external family
may be supplied in place of the internally existing indexing set. -/
def SmallUnionClosed (k : M) : Prop :=
  ∀ b r : M, Small k b → (∀ s : M, member s b → Small k s) →
    IsUnion r b → Small k r

/-- This is the explicit remaining internal cardinal-product lemma. -/
def SmallProductClosed (k : M) : Prop :=
  ∀ x y p : M, Small k x → Small k y → Product p x y → Small k p

theorem binary_union_small (h : AxiomSemantics M) {k x y : M}
    (hk : HasInductiveMember k) (hun : SmallUnionClosed k)
    (hx : Small k x) (hy : Small k y) :
    ∃ r : M, Small k r ∧ ∀ z : M, member z r ↔ member z x ∨ member z y := by
  obtain ⟨b,hb⟩ := h.pairing x y
  obtain ⟨r,hr⟩ := h.union b
  have hbsmall : Small k b := pair_small h hk hb
  refine ⟨r,hun b r hbsmall ?_ hr,?_⟩
  · intro s hs
    rcases (hb s).mp hs with rfl | rfl
    · exact hx
    · exact hy
  · intro z
    refine (hr z).trans ?_
    constructor
    · rintro ⟨s,hs,hzs⟩
      rcases (hb s).mp hs with rfl | rfl
      · exact Or.inl hzs
      · exact Or.inr hzs
    · rintro (hz | hz)
      · exact ⟨x,(hb x).mpr (Or.inl rfl),hz⟩
      · exact ⟨y,(hb y).mpr (Or.inr rfl),hz⟩

/-- The original regularity guard already proves small unions for families of
ordinal members of K, without any internal cardinal multiplication theorem. -/
theorem union_small_of_family_subset_cardinal (h : AxiomSemantics M) {k b r : M}
    (hg : Guard k) (hb : subset b k) (hs : Small k b) (hr : IsUnion r b) :
    Small k r := by
  obtain ⟨bound,hbk,hbb⟩ := hg.2.2 b hb hs
  have htrans : Transitive bound := hg.1.1.2 bound hbk
  have hrbound : subset r bound := by
    intro z hz
    obtain ⟨s,hsb,hzs⟩ := (hr z).mp hz
    exact htrans s (hbb s hsb) z hzs
  exact small_of_subset h hrbound (member_small h hbk)

end Komorebi.InternalSmallSupports
