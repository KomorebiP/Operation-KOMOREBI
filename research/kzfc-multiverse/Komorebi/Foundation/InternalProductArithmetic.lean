import Komorebi.Foundation.InternalRectangleBounds
import Komorebi.Foundation.InternalConeFormula

/-!
# Internal small-product arithmetic from the original ZFC axioms and guard

Definable induction ranks each ordinal rectangle. Each predecessor is a smaller
rectangle plus one slice. A two-stage internal image bound makes the full rank
image strictly small. No external cardinal arithmetic or external well-foundedness
of the model is invoked.
-/

universe u v

namespace Komorebi.InternalProductArithmetic

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder
open InternalOrderGraphs InternalRankingConditions InternalBoundedRanking InternalFiniteUnions
open InternalLexicographicOrder InternalRectangleBounds InternalConstraints InternalFineCompactness
open InternalSupportEquivalence InternalConeFormula

variable {M : Type u} [language.Structure M]

def OrdinalRectangleSmall (k a : M) : Prop :=
  ∀ b w : M, member b k → Product w a b → Small k w

def ordinalRectangleSmallF {α : Type v} (k a : α) : language.Formula α :=
  allF (let k := some k; let a := some a; let b := none
    allF ((memF (some b) (some k)).imp
      ((prodF none (some a) (some b)).imp (smallF (some k) none))))

@[simp]
theorem ordinalRectangleSmallF_realize {α : Type v} (k a : α) (e : α → M) :
    (ordinalRectangleSmallF k a).Realize e ↔ OrdinalRectangleSmall (e k) (e a) := by
  simp [ordinalRectangleSmallF,OrdinalRectangleSmall,assign]

/-- This induction applies only to a specifically supplied first-order formula.
The resulting ranks and injection witnesses are elements of the same model. -/
theorem ordinal_rectangles_small (h : AxiomSemantics M) {k : M} (hk : Guard k) :
    ∀ a : M, member a k → OrdinalRectangleSmall k a := by
  obtain ⟨o,hok,_⟩ := hk.2.1
  let φ : language.Formula (Option (Fin 1)) := ordinalRectangleSmallF (some 0) none
  have step : ∀ a : M, member a k →
      (∀ x : M, member x a → φ.Realize (assign ![k] x)) →
      φ.Realize (assign ![k] a) := by
    intro a hak ih
    have ih' : ∀ x : M, member x a → OrdinalRectangleSmall k x := by
      intro x hx
      simpa [φ,assign] using ih x hx
    suffices OrdinalRectangleSmall k a by simpa [φ,assign] using this
    intro b w hbk hw
    obtain ⟨r,hr⟩ := lexRelation_exists h w
    have hwo := lexRelation_wellOrder h (ordinal_member hk.1.1 hak)
      (ordinal_member hk.1.1 hbk) hw hr
    have hpred : ∀ q p : M, member q w → Predecessors p w r q → Small k p := by
      intro q p hqw hp
      obtain ⟨x,hxa,y,hyb,hq⟩ := (hw q).mp hqw
      exact lexPredecessors_small h hk hbk hw hr hyb hq hp
        (fun t ht => ih' x hxa b t hbk ht)
    obtain ⟨g,hg,hig,_⟩ := bounded_ranking_exists h hk hok hwo hpred
    exact rectangle_small_of_injection h hk (member_small h hak) (member_small h hbk) hw hg hig
  intro a ha
  simpa [φ,assign] using bounded_definable_induction h φ ![k] k hk.1.1.1 step a ha

def ProductMap (p q f g : M) : Prop :=
  ∃ x y a b : M, IsOrderedPair p x y ∧ IsOrderedPair q a b ∧
    PairMember x a f ∧ PairMember y b g

def productMapF {α : Type v} (p q f g : α) : language.Formula α :=
  exF (let p := some p; let q := some q; let f := some f; let g := some g; let x := none
    exF (let p := some p; let q := some q; let f := some f; let g := some g; let x := some x; let y := none
      exF (let p := some p; let q := some q; let f := some f; let g := some g
        let x := some x; let y := some y; let a := none
        exF (pairF (some p) (some x) (some y) ⊓
          (pairF (some q) (some a) none ⊓
            (pairMemF (some x) (some a) (some f) ⊓ pairMemF (some y) none (some g)))))))

@[simp]
theorem productMapF_realize {α : Type v} (p q f g : α) (e : α → M) :
    (productMapF p q f g).Realize e ↔ ProductMap (e p) (e q) (e f) (e g) := by
  simp [productMapF,ProductMap,assign]

/-- An actual internal product injection is constructed from two internal injections. -/
theorem product_embeds_product (h : AxiomSemantics M) {x y a b w t : M}
    (hx : Embeds x a) (hy : Embeds y b) (hw : Product w x y) (ht : Product t a b) :
    Embeds w t := by
  obtain ⟨f,hf,hif⟩ := hx
  obtain ⟨g,hg,hig⟩ := hy
  let φ : language.Formula (Option (Option (Fin 2))) :=
    productMapF none (some none) (some (some 0)) (some (some 1))
  obtain ⟨m,p,hp,hmp,hm⟩ := relationSet_exists h φ ![f,g] w t
  have hm' : ∀ s q : M, PairMember s q m ↔
      member s w ∧ member q t ∧ ProductMap s q f g := by
    intro s q
    simpa [φ,assign] using hm s q
  refine ⟨m,⟨⟨p,hp,hmp⟩,?_⟩,?_⟩
  · intro s hs
    obtain ⟨u,hux,v,hvy,hsp⟩ := (hw s).mp hs
    obtain ⟨u',huu',_⟩ := hf.2 u hux
    obtain ⟨v',hvv',_⟩ := hg.2 v hvy
    obtain ⟨q,hq⟩ := orderedPair_exists h u' v'
    have hqt : member q t := (ht q).mpr
      ⟨u',(functionGraph_pair_bounds hf huu').2,v',(functionGraph_pair_bounds hg hvv').2,hq⟩
    refine ⟨q,(hm' s q).mpr ⟨hs,hqt,u,v,u',v',hsp,hq,huu',hvv'⟩,?_⟩
    intro q' hsq'
    obtain ⟨z,z',c,d,hs',hq',hzc,hz'd⟩ := ((hm' s q').mp hsq').2.2
    obtain ⟨rfl,rfl⟩ := orderedPair_injective hs' hsp
    have hc : c = u' := functionGraph_value_unique hf hzc huu'
    have hd : d = v' := functionGraph_value_unique hg hz'd hvv'
    subst c; subst d
    exact orderedPair_unique h hq' hq
  · intro s _ t' _ q hsq htq
    obtain ⟨u,v,c,d,hs,hq,huc,hvd⟩ := ((hm' s q).mp hsq).2.2
    obtain ⟨u',v',c',d',ht',hq',hu'c',hv'd'⟩ := ((hm' t' q).mp htq).2.2
    obtain ⟨rfl,rfl⟩ := orderedPair_injective hq' hq
    have hu : u = u' := hif u (functionGraph_pair_bounds hf huc).1
      u' (functionGraph_pair_bounds hf hu'c').1 _ huc hu'c'
    have hv : v = v' := hig v (functionGraph_pair_bounds hg hvd).1
      v' (functionGraph_pair_bounds hg hv'd').1 _ hvd hv'd'
    subst u'; subst v'
    exact orderedPair_unique h hs ht'

/-- The formerly explicit arithmetic premise is discharged without strengthening
ZFC, the regular-uncountable guard, or the definition of internal smallness. -/
theorem smallProductClosed_of_guard (h : AxiomSemantics M) {k : M}
    (hk : Guard k) : SmallProductClosed k := by
  intro x y p hx hy hp
  obtain ⟨a,hak,hxa⟩ := hx
  obtain ⟨b,hbk,hyb⟩ := hy
  obtain ⟨t,ht⟩ := product_exists h a b
  have hts : Small k t := ordinal_rectangles_small h hk a hak b t hbk ht
  exact small_of_embeds h (product_embeds_product h hxa hyb hp ht) hts

theorem model_zfc_productArithmeticSentence (hM : M ⊨ zfcTheory) :
    M ⊨ productArithmeticSentence := by
  rw [productArithmeticSentence_realize]
  exact fun _ hk => smallProductClosed_of_guard (model_zfc_iff_axiomSemantics.mp hM) hk

theorem internal_extension_implies_fine (h : AxiomSemantics M) {k : M}
    (hk : Guard k) (hext : Extension k) : InternalFinePrinciple k :=
  (fine_iff_productClosed_of_extension h hk hext).mpr (smallProductClosed_of_guard h hk)

theorem internal_extension_implies_compactness (h : AxiomSemantics M) {k : M}
    (hk : Guard k) (hext : Extension k) : ConstraintCompactness k :=
  internal_fine_implies_compactness h k (internal_extension_implies_fine h hk hext)

theorem internal_extension_implies_reflection (h : AxiomSemantics M) {k : M}
    (hk : Guard k) (hext : Extension k) : ConstraintReflection k :=
  internal_fine_implies_reflection h k (internal_extension_implies_fine h hk hext)

theorem model_zfc_extensionCompactnessSentence (hM : M ⊨ zfcTheory) :
    M ⊨ guardedExtensionCompactnessSentence :=
  model_zfc_extensionCompactness_of_arithmetic hM (model_zfc_productArithmeticSentence hM)

theorem model_kzfc_compactness_witness (hM : M ⊨ KZFCTheory.kzfcTheory) :
    ∃ k : M, Guard k ∧ ConstraintCompactness k := by
  have hbase : M ⊨ zfcTheory :=
    ((MembershipFormula.model_extension_iff zfcTheory M).mp hM).1
  exact model_kzfc_compactness_witness_of_arithmetic hM (model_zfc_productArithmeticSentence hbase)

end Komorebi.InternalProductArithmetic
