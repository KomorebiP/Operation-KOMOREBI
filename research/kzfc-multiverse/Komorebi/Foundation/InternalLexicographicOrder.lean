import Komorebi.Foundation.InternalFiniteUnions
import Komorebi.Foundation.InternalSupportEquivalence

/-!
# Internal lexicographic order of ordinal rectangles

Only subsets represented inside the model are used for least-element selection.
The relation itself is obtained by an actual Separation instance.
-/

universe u v

namespace Komorebi.InternalLexicographicOrder

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder
open InternalOrderGraphs InternalRankingConditions InternalBoundedRanking InternalFiniteUnions
open InternalSupportEquivalence

variable {M : Type u} [language.Structure M]

def LexBefore (p q : M) : Prop :=
  ∃ x y a b : M, IsOrderedPair p x y ∧ IsOrderedPair q a b ∧
    (member x a ∨ (x = a ∧ member y b))

def lexBeforeF {α : Type v} (p q : α) : language.Formula α :=
  exF (let p := some p; let q := some q; let x := none
    exF (let p := some p; let q := some q; let x := some x; let y := none
      exF (let p := some p; let q := some q; let x := some x; let y := some y; let a := none
        exF (pairF (some p) (some x) (some y) ⊓
          (pairF (some q) (some a) none ⊓
            (memF (some x) (some a) ⊔
              (eqF (some x) (some a) ⊓ memF (some y) none)))))))

@[simp]
theorem lexBeforeF_realize {α : Type v} (p q : α) (e : α → M) :
    (lexBeforeF p q).Realize e ↔ LexBefore (e p) (e q) := by
  simp [lexBeforeF,LexBefore,assign]

theorem lexBefore_pair_iff {p q x y a b : M}
    (hp : IsOrderedPair p x y) (hq : IsOrderedPair q a b) :
    LexBefore p q ↔ member x a ∨ (x = a ∧ member y b) := by
  constructor
  · rintro ⟨x',y',a',b',hp',hq',hlex⟩
    obtain ⟨rfl,rfl⟩ := orderedPair_injective hp' hp
    obtain ⟨rfl,rfl⟩ := orderedPair_injective hq' hq
    exact hlex
  · intro hl
    exact ⟨x,y,a,b,hp,hq,hl⟩

def LexRelation (r w : M) : Prop :=
  ∀ p q : M, PairMember p q r ↔ member p w ∧ member q w ∧ LexBefore p q

theorem lexRelation_exists (h : AxiomSemantics M) (w : M) :
    ∃ r : M, LexRelation r w := by
  let φ : language.Formula (Option (Option (Fin 0))) := lexBeforeF none (some none)
  obtain ⟨r,_,_,_,hr⟩ := relationSet_exists h φ ![] w w
  exact ⟨r,fun p q => by simpa [φ,assign] using hr p q⟩

theorem lexRelation_pair_iff {r w p q x y a b : M}
    (hr : LexRelation r w) (hpw : member p w) (hqw : member q w)
    (hp : IsOrderedPair p x y) (hq : IsOrderedPair q a b) :
    PairMember p q r ↔ member x a ∨ (x = a ∧ member y b) := by
  rw [hr p q]
  exact (and_iff_right hpw).trans ((and_iff_right hqw).trans (lexBefore_pair_iff hp hq))

/-- Nonempty internal subsets of the rectangle have a lexicographically least element.
Both coordinate projections used below are sets furnished by Separation. -/
theorem lexRelation_least (h : AxiomSemantics M) {a b w r : M}
    (hw : Product w a b) (hr : LexRelation r w)
    (s : M) (hsw : subset s w) (hs : ∃ p : M, member p s) :
    ∃ p : M, member p s ∧ ∀ q : M, member q s → ¬ PairMember q p r := by
  let φ : language.Formula (Option (Fin 2)) :=
    exF (let x := some none; let b := some (some 0); let s := some (some 1); let y := none
      memF y b ⊓ exF (memF none (some s) ⊓ pairF none (some x) (some y)))
  obtain ⟨firsts,hfirsts⟩ := h.separation 2 φ ![b,s] a
  have hfirsts' : ∀ x : M, member x firsts ↔ member x a ∧
      ∃ y : M, member y b ∧ ∃ p : M, member p s ∧ IsOrderedPair p x y := by
    intro x
    simpa [φ,assign] using hfirsts x
  have hfn : ∃ x : M, member x firsts := by
    obtain ⟨p,hps⟩ := hs
    obtain ⟨x,hxa,y,hyb,hp⟩ := (hw p).mp (hsw p hps)
    exact ⟨x,(hfirsts' x).mpr ⟨hxa,y,hyb,p,hps,hp⟩⟩
  obtain ⟨x,hxf,hxmin⟩ := h.foundation firsts hfn
  let ψ : language.Formula (Option (Fin 2)) :=
    exF (memF none (some (some 1)) ⊓ pairF none (some (some 0)) (some none))
  obtain ⟨seconds,hseconds⟩ := h.separation 2 ψ ![x,s] b
  have hseconds' : ∀ y : M, member y seconds ↔ member y b ∧
      ∃ p : M, member p s ∧ IsOrderedPair p x y := by
    intro y
    simpa [ψ,assign] using hseconds y
  have hsn : ∃ y : M, member y seconds := by
    obtain ⟨y,hyb,p,hps,hp⟩ := ((hfirsts' x).mp hxf).2
    exact ⟨y,(hseconds' y).mpr ⟨hyb,p,hps,hp⟩⟩
  obtain ⟨y,hys,hymin⟩ := h.foundation seconds hsn
  obtain ⟨_,p,hps,hp⟩ := (hseconds' y).mp hys
  refine ⟨p,hps,?_⟩
  intro q hqs hqp
  obtain ⟨u,hua,v,hvb,hq⟩ := (hw q).mp (hsw q hqs)
  rcases (lexRelation_pair_iff hr (hsw q hqs) (hsw p hps) hq hp).mp hqp with hux | ⟨rfl,hvy⟩
  · exact hxmin u ⟨(hfirsts' u).mpr ⟨hua,v,hvb,q,hqs,hq⟩,hux⟩
  · exact hymin v ⟨(hseconds' v).mpr ⟨hvb,q,hqs,hq⟩,hvy⟩

theorem lexRelation_wellOrder (h : AxiomSemantics M) {a b w r : M}
    (ha : OrdinalPredicate a) (hb : OrdinalPredicate b)
    (hw : Product w a b) (hr : LexRelation r w) : WellOrderOn w r := by
  refine ⟨?_,?_,?_,?_,lexRelation_least h hw hr⟩
  · intro p q hpq
    exact ⟨((hr p q).mp hpq).1,((hr p q).mp hpq).2.1⟩
  · intro p hpp
    have hpw := ((hr p p).mp hpp).1
    obtain ⟨x,_,y,_,hp⟩ := (hw p).mp hpw
    rcases (lexRelation_pair_iff hr hpw hpw hp hp).mp hpp with hxx | ⟨_,hyy⟩
    · exact InternalOrdinalOrder.member_irrefl h x hxx
    · exact InternalOrdinalOrder.member_irrefl h y hyy
  · intro p q t hpq hqt
    have hpw := ((hr p q).mp hpq).1
    have hqw := ((hr p q).mp hpq).2.1
    have htw := ((hr q t).mp hqt).2.1
    obtain ⟨x,_,y,_,hp⟩ := (hw p).mp hpw
    obtain ⟨x',_,y',_,hq⟩ := (hw q).mp hqw
    obtain ⟨x'',hx''a,y'',hy''b,ht⟩ := (hw t).mp htw
    apply (lexRelation_pair_iff hr hpw htw hp ht).mpr
    rcases (lexRelation_pair_iff hr hpw hqw hp hq).mp hpq with hxx' | ⟨rfl,hyy'⟩
    · rcases (lexRelation_pair_iff hr hqw htw hq ht).mp hqt with hx'x'' | ⟨rfl,_⟩
      · exact Or.inl ((ordinal_member ha hx''a).1 x' hx'x'' x hxx')
      · exact Or.inl hxx'
    · rcases (lexRelation_pair_iff hr hqw htw hq ht).mp hqt with hx'x'' | ⟨rfl,hy'y''⟩
      · exact Or.inl hx'x''
      · exact Or.inr ⟨rfl,(ordinal_member hb hy''b).1 y' hy'y'' y hyy'⟩
  · intro p q hpw hqw
    obtain ⟨x,hxa,y,hyb,hp⟩ := (hw p).mp hpw
    obtain ⟨a',ha'a,b',hb'b,hq⟩ := (hw q).mp hqw
    rcases ordinal_comparable h (ordinal_member ha hxa) (ordinal_member ha ha'a) with hxa' | rfl | ha'x
    · exact Or.inl ((lexRelation_pair_iff hr hpw hqw hp hq).mpr (Or.inl hxa'))
    · rcases ordinal_comparable h (ordinal_member hb hyb) (ordinal_member hb hb'b) with hyb' | rfl | hb'y
      · exact Or.inl ((lexRelation_pair_iff hr hpw hqw hp hq).mpr (Or.inr ⟨rfl,hyb'⟩))
      · exact Or.inr (Or.inl (orderedPair_unique h hp hq))
      · exact Or.inr (Or.inr ((lexRelation_pair_iff hr hqw hpw hq hp).mpr (Or.inr ⟨rfl,hb'y⟩)))
    · exact Or.inr (Or.inr ((lexRelation_pair_iff hr hqw hpw hq hp).mpr (Or.inl ha'x)))

/-- Predecessors split into an earlier rectangle and a single initial row slice. -/
theorem lexPredecessors_small (h : AxiomSemantics M) {k a b w r q x y p : M}
    (hk : Guard k) (hb : member b k) (hw : Product w a b) (hr : LexRelation r w)
    (hy : member y b) (hq : IsOrderedPair q x y) (hp : Predecessors p w r q)
    (hrect : ∀ t : M, Product t x b → Small k t) : Small k p := by
  obtain ⟨rect,hrectp⟩ := product_exists h x b
  obtain ⟨slice,hslice⟩ := productSlice_exists h x y
  obtain ⟨both,hboth⟩ := binary_union_exists h rect slice
  have hrs : Small k rect := hrect rect hrectp
  have hss : Small k slice := small_of_embeds h (productSlice_embeds h hslice)
    (member_small h (hk.1.1.1 b hb y hy))
  have hbs : Small k both := binary_union_small_of_guard h hk hrs hss hboth
  apply small_of_subset h ?_ hbs
  intro z hzp
  have hzw := ((hp z).mp hzp).1
  have hzq := ((hp z).mp hzp).2
  obtain ⟨u,_,v,hvb,hz⟩ := (hw z).mp hzw
  rcases (lexBefore_pair_iff hz hq).mp ((hr z q).mp hzq).2.2 with hux | ⟨rfl,hvy⟩
  · exact (hboth z).mpr (Or.inl ((hrectp z).mpr ⟨u,hux,v,hvb,hz⟩))
  · exact (hboth z).mpr (Or.inr ((hslice z).mpr ⟨v,hvy,hz⟩))

end Komorebi.InternalLexicographicOrder
