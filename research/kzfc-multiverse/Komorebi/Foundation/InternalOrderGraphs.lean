import Komorebi.Foundation.InternalOrdinalOrder

/-! # Internal graph operations and internally quantified well-orders -/

universe u v

namespace Komorebi.InternalOrderGraphs

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder

variable {M : Type u} [language.Structure M]

/-- Both graph bounds can change when all entries satisfy the new bounds. -/
theorem graph_retype (h : AxiomSemantics M) {x y g x' y' : M}
    (hg : FunctionGraph x y g)
    (hb : ∀ a b : M, PairMember a b g → member a x' ∧ member b y')
    (ht : ∀ a : M, member a x' → ∃ b : M, PairMember a b g) :
    FunctionGraph x' y' g := by
  obtain ⟨p,hp⟩ := product_exists h x' y'
  refine ⟨⟨p,hp,?_⟩,?_⟩
  · intro q hq
    obtain ⟨old,hold,hgOld⟩ := hg.1
    obtain ⟨a,_,b,_,hqab⟩ := (hold q).mp (hgOld q hq)
    have hab : PairMember a b g := ⟨q,hqab,hq⟩
    exact (hp q).mpr ⟨a,(hb a b hab).1,b,(hb a b hab).2,hqab⟩
  · intro a ha
    obtain ⟨b,hab⟩ := ht a ha
    exact ⟨b,hab,fun c hac => functionGraph_value_unique hg hac hab⟩

theorem function_range (h : AxiomSemantics M) {x y f : M}
    (hf : FunctionGraph x y f) :
    ∃ r : M, subset r y ∧ FunctionGraph x r f ∧
      ∀ b : M, member b r ↔ ∃ a : M, member a x ∧ PairMember a b f := by
  let φ : language.Formula (Option (Fin 2)) :=
    exF (memF none (some (some 0)) ⊓ pairMemF none (some none) (some (some 1)))
  obtain ⟨r,hr⟩ := h.separation 2 φ ![x,f] y
  have hr' : ∀ b : M, member b r ↔ ∃ a : M, member a x ∧ PairMember a b f := by
    intro b
    have he : member b r ↔ member b y ∧ ∃ a : M, member a x ∧ PairMember a b f := by
      simpa [φ,assign] using hr b
    refine he.trans ?_
    constructor
    · exact fun hb => hb.2
    · rintro ⟨a,ha,hab⟩
      exact ⟨(functionGraph_pair_bounds hf hab).2,a,ha,hab⟩
  have hry : subset r y := by
    intro b hb
    obtain ⟨a,_,hab⟩ := (hr' b).mp hb
    exact (functionGraph_pair_bounds hf hab).2
  refine ⟨r,hry,graph_retype h hf ?_ ?_,hr'⟩
  · intro a b hab
    have ha := (functionGraph_pair_bounds hf hab).1
    exact ⟨ha,(hr' b).mpr ⟨a,ha,hab⟩⟩
  · intro a ha
    obtain ⟨b,hab,_⟩ := hf.2 a ha
    exact ⟨b,hab⟩

theorem function_range_small (h : AxiomSemantics M) {k x y f : M}
    (hf : FunctionGraph x y f) (hx : Small k x) :
    ∃ r : M, subset r y ∧ Small k r ∧
      ∀ b : M, member b r ↔ ∃ a : M, member a x ∧ PairMember a b f := by
  obtain ⟨r,hry,hfr,hr⟩ := function_range h hf
  have hs : Small k r := small_of_surjection h hfr hx (fun b hb => (hr b).mp hb)
  exact ⟨r,hry,hs,hr⟩

theorem subset_pairMember {f g a b : M} (hfg : subset f g)
    (hab : PairMember a b f) : PairMember a b g := by
  obtain ⟨p,hp,hpf⟩ := hab
  exact ⟨p,hp,hfg p hpf⟩

/-- The set obtained by adding one Kuratowski pair has the exact graph entries. -/
theorem graph_append (h : AxiomSemantics M) (g x y : M) :
    ∃ f : M, subset g f ∧
      (∀ q : M, member q f ↔ member q g ∨ IsOrderedPair q x y) ∧
      ∀ a b : M, PairMember a b f ↔ PairMember a b g ∨ (a = x ∧ b = y) := by
  obtain ⟨p,hp⟩ := orderedPair_exists h x y
  obtain ⟨one,hone⟩ := singleton_exists h p
  obtain ⟨two,htwo⟩ := h.pairing g one
  obtain ⟨f,hf⟩ := h.union two
  have hf' : ∀ q : M, member q f ↔ member q g ∨ IsOrderedPair q x y := by
    intro q
    constructor
    · intro hq
      obtain ⟨s,hs,hqs⟩ := (hf q).mp hq
      rcases (htwo s).mp hs with rfl | rfl
      · exact Or.inl hqs
      · have he : q = p := (hone q).mp hqs
        exact Or.inr (he.symm ▸ hp)
    · rintro (hq | hq)
      · exact (hf q).mpr ⟨g,(htwo g).mpr (Or.inl rfl),hq⟩
      · have he : q = p := orderedPair_unique h hq hp
        exact (hf q).mpr ⟨one,(htwo one).mpr (Or.inr rfl),(hone q).mpr he⟩
  refine ⟨f,fun q hq => (hf' q).mpr (Or.inl hq),hf',?_⟩
  intro a b
  constructor
  · rintro ⟨q,hq,hqf⟩
    rcases (hf' q).mp hqf with hqg | hq'
    · exact Or.inl ⟨q,hq,hqg⟩
    · exact Or.inr (orderedPair_injective hq hq')
  · rintro (hab | ⟨rfl,rfl⟩)
    · obtain ⟨q,hq,hqg⟩ := hab
      exact ⟨q,hq,(hf' q).mpr (Or.inl hqg)⟩
    · exact ⟨p,hp,(hf' p).mpr (Or.inr hp)⟩

/-- Least elements are required only for subsets represented by elements of M. -/
structure WellOrderOn (w r : M) : Prop where
  bounds : ∀ a b : M, PairMember a b r → member a w ∧ member b w
  irrefl : ∀ a : M, ¬ PairMember a a r
  trans : ∀ a b c : M, PairMember a b r → PairMember b c r → PairMember a c r
  total : ∀ a b : M, member a w → member b w →
    PairMember a b r ∨ a = b ∨ PairMember b a r
  least : ∀ s : M, subset s w → (∃ a : M, member a s) →
    ∃ a : M, member a s ∧ ∀ b : M, member b s → ¬ PairMember b a r

theorem order_asymm {w r a b : M} (hr : WellOrderOn w r)
    (hab : PairMember a b r) : ¬ PairMember b a r := by
  intro hba
  exact hr.irrefl a (hr.trans a b a hab hba)

def Predecessors (p w r x : M) : Prop :=
  ∀ a : M, member a p ↔ member a w ∧ PairMember a x r

def predecessorsF {α : Type v} (p w r x : α) : language.Formula α :=
  allF ((memF none (some p)).iff
    (memF none (some w) ⊓ pairMemF none (some x) (some r)))

@[simp]
theorem predecessorsF_realize {α : Type v} (p w r x : α) (e : α → M) :
    (predecessorsF p w r x).Realize e ↔ Predecessors (e p) (e w) (e r) (e x) := by
  simp [predecessorsF,Predecessors,assign]

theorem predecessors_exists (h : AxiomSemantics M) (w r x : M) :
    ∃ p : M, Predecessors p w r x := by
  let φ : language.Formula (Option (Fin 2)) := pairMemF none (some 0) (some 1)
  obtain ⟨p,hp⟩ := h.separation 2 φ ![x,r] w
  exact ⟨p,fun a => by simpa [φ,assign] using hp a⟩

theorem ordinal_wellOrder (h : AxiomSemantics M) {w : M} (hw : OrdinalPredicate w) :
    ∃ r : M, WellOrderOn w r ∧
      ∀ a b : M, PairMember a b r ↔ member a w ∧ member b w ∧ member a b := by
  let φ : language.Formula (Option (Option (Fin 0))) := memF none (some none)
  obtain ⟨r,_,_,_,hr⟩ := relationSet_exists h φ ![] w w
  have hr' : ∀ a b : M, PairMember a b r ↔ member a w ∧ member b w ∧ member a b := by
    intro a b
    simpa [φ,assign] using hr a b
  refine ⟨r,⟨?_,?_,?_,?_,?_⟩,hr'⟩
  · intro a b hab
    exact ⟨((hr' a b).mp hab).1,((hr' a b).mp hab).2.1⟩
  · intro a haa
    exact InternalOrdinalOrder.member_irrefl h a ((hr' a a).mp haa).2.2
  · intro a b c hab hbc
    have hab' := (hr' a b).mp hab
    have hbc' := (hr' b c).mp hbc
    exact (hr' a c).mpr ⟨hab'.1,hbc'.2.1,
      (ordinal_member hw hbc'.2.1).1 b hbc'.2.2 a hab'.2.2⟩
  · intro a b ha hb
    rcases ordinal_comparable h (ordinal_member hw ha) (ordinal_member hw hb) with hab | he | hba
    · exact Or.inl ((hr' a b).mpr ⟨ha,hb,hab⟩)
    · exact Or.inr (Or.inl he)
    · exact Or.inr (Or.inr ((hr' b a).mpr ⟨hb,ha,hba⟩))
  · intro s hsw hs
    obtain ⟨a,ha,hmin⟩ := h.foundation s hs
    exact ⟨a,ha,fun b hb hba => hmin b ⟨hb,((hr' b a).mp hba).2.2⟩⟩

end Komorebi.InternalOrderGraphs
