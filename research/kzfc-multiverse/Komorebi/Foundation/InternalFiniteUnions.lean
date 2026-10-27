import Komorebi.Foundation.InternalBoundedRanking

/-!
# Internal finite unions from regular boundedness

Ordinal copies can be placed above a prescribed offset by the bounded-ranking
construction. This gives small binary unions without invoking cardinal arithmetic.
-/

universe u v

namespace Komorebi.InternalFiniteUnions

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder
open InternalOrderGraphs InternalRankingConditions InternalBoundedRanking

variable {M : Type u} [language.Structure M]

theorem common_ordinal_bound (h : AxiomSemantics M) {k a b : M}
    (hk : OrdinalPredicate k) (ha : member a k) (hb : member b k) :
    ∃ c : M, member c k ∧ subset a c ∧ subset b c := by
  rcases ordinal_subset_total h (ordinal_member hk ha) (ordinal_member hk hb) with hab | hba
  · exact ⟨b,hb,hab,fun _ hb => hb⟩
  · exact ⟨a,ha,fun _ ha => ha,hba⟩

/-- An internal copy of an ordinal B below K, with all values at or above OFFSET. -/
theorem shifted_ordinal_embedding (h : AxiomSemantics M) {k offset b : M}
    (hk : Guard k) (hoff : member offset k) (hb : member b k) :
    ∃ c g : M, member c k ∧ FunctionGraph b c g ∧ InjectiveGraph b g ∧
      ∀ x y : M, PairMember x y g → subset offset y := by
  obtain ⟨r,hr,hrel⟩ := ordinal_wellOrder h (ordinal_member hk.1.1 hb)
  have hsmall : ∀ x p : M, member x b → Predecessors p b r x → Small k p := by
    intro x p hx hp
    have hpx : subset p x := by
      intro z hz
      exact ((hrel z x).mp ((hp z).mp hz).2).2.2
    exact small_of_subset h hpx (member_small h (hk.1.1.1 b hb x hx))
  obtain ⟨g,hg,hig,hpart⟩ := bounded_ranking_exists h hk hoff hr hsmall
  obtain ⟨im,himk,hims,him⟩ := function_range_small h hg (member_small h hb)
  obtain ⟨c,hck,himc⟩ := hk.2.2 im himk hims
  have hc : FunctionGraph b c g := graph_retype h hg
    (fun x y hxy => ⟨(functionGraph_pair_bounds hg hxy).1,
      himc y ((him y).mpr ⟨x,(functionGraph_pair_bounds hg hxy).1,hxy⟩)⟩)
    (fun x hx => by obtain ⟨y,hxy,_⟩ := hg.2 x hx; exact ⟨y,hxy⟩)
  exact ⟨c,g,hck,hc,hig,fun x y hxy => (hpart.recurrence x y hxy).1.2.1⟩

def BinaryUnion (z x y : M) : Prop :=
  ∀ a : M, member a z ↔ member a x ∨ member a y

theorem binary_union_exists (h : AxiomSemantics M) (x y : M) :
    ∃ z : M, BinaryUnion z x y := by
  obtain ⟨p,hp⟩ := h.pairing x y
  obtain ⟨z,hz⟩ := h.union p
  refine ⟨z,?_⟩
  intro a
  constructor
  · intro ha
    obtain ⟨b,hb,hab⟩ := (hz a).mp ha
    rcases (hp b).mp hb with rfl | rfl
    · exact Or.inl hab
    · exact Or.inr hab
  · rintro (ha | ha)
    · exact (hz a).mpr ⟨x,(hp x).mpr (Or.inl rfl),ha⟩
    · exact (hz a).mpr ⟨y,(hp y).mpr (Or.inr rfl),ha⟩

/-- Smallness of a binary union is now proved from the unchanged guard,
not assumed as a fragment of the desired product or union theorem. -/
theorem binary_union_small_of_guard (h : AxiomSemantics M) {k x y z : M}
    (hk : Guard k) (hx : Small k x) (hy : Small k y) (hz : BinaryUnion z x y) :
    Small k z := by
  classical
  obtain ⟨a,hak,fx,hfx,hix⟩ := hx
  obtain ⟨b,hbk,fy,hfy,hiy⟩ := hy
  obtain ⟨c,shift,hck,hshift,hishift,habove⟩ := shifted_ordinal_embedding h hk hak hbk
  obtain ⟨gy,hgy,hcomp⟩ := composition_exists h hfy hshift
  have higy : InjectiveGraph y gy := by
    intro u hu v hv q huq hvq
    obtain ⟨u',huu',hu'q⟩ := (hcomp u q).mp huq
    obtain ⟨v',hvv',hv'q⟩ := (hcomp v q).mp hvq
    have he : u' = v' := hishift u' (functionGraph_pair_bounds hfy huu').2
      v' (functionGraph_pair_bounds hfy hvv').2 q hu'q hv'q
    subst v'
    exact hiy u hu v hv u' huu' hvv'
  have hgyAbove : ∀ u q : M, PairMember u q gy → subset a q := by
    intro u q huq
    obtain ⟨v,_,hvq⟩ := (hcomp u q).mp huq
    exact habove v q hvq
  obtain ⟨t,ht,hat,hct⟩ := common_ordinal_bound h hk.1.1 hak hck
  let φ : language.Formula (Option (Option (Fin 3))) :=
    (memF none (some (some 0)) ⊓ pairMemF none (some none) (some (some 1))) ⊔
      ((memF none (some (some 0))).not ⊓ pairMemF none (some none) (some (some 2)))
  obtain ⟨f,p,hp,hfp,hf⟩ := relationSet_exists h φ ![x,fx,gy] z t
  have hf' : ∀ u q : M, PairMember u q f ↔ member u z ∧ member q t ∧
      ((member u x ∧ PairMember u q fx) ∨ (¬ member u x ∧ PairMember u q gy)) := by
    intro u q
    simpa [φ,assign] using hf u q
  have hfun : FunctionGraph z t f := by
    refine ⟨⟨p,hp,hfp⟩,?_⟩
    intro u hu
    by_cases hux : member u x
    · obtain ⟨q,huq,_⟩ := hfx.2 u hux
      refine ⟨q,(hf' u q).mpr ⟨hu,hat q (functionGraph_pair_bounds hfx huq).2,
        Or.inl ⟨hux,huq⟩⟩,?_⟩
      intro v huv
      rcases ((hf' u v).mp huv).2.2 with huv | huv
      · exact functionGraph_value_unique hfx huv.2 huq
      · exact False.elim (huv.1 hux)
    · have huy : member u y := ((hz u).mp hu).resolve_left hux
      obtain ⟨q,huq,_⟩ := hgy.2 u huy
      refine ⟨q,(hf' u q).mpr ⟨hu,hct q (functionGraph_pair_bounds hgy huq).2,
        Or.inr ⟨hux,huq⟩⟩,?_⟩
      intro v huv
      rcases ((hf' u v).mp huv).2.2 with huv | huv
      · exact False.elim (hux huv.1)
      · exact functionGraph_value_unique hgy huv.2 huq
  refine ⟨t,ht,f,hfun,?_⟩
  intro u _ v _ q huq hvq
  rcases ((hf' u q).mp huq).2.2 with huq | huq
  · rcases ((hf' v q).mp hvq).2.2 with hvq | hvq
    · exact hix u huq.1 v hvq.1 q huq.2 hvq.2
    · exact False.elim (InternalOrdinalOrder.member_irrefl h q
        (hgyAbove v q hvq.2 q (functionGraph_pair_bounds hfx huq.2).2))
  · rcases ((hf' v q).mp hvq).2.2 with hvq | hvq
    · exact False.elim (InternalOrdinalOrder.member_irrefl h q
        (hgyAbove u q huq.2 q (functionGraph_pair_bounds hfx hvq.2).2))
    · exact higy u (functionGraph_pair_bounds hgy huq.2).1
        v (functionGraph_pair_bounds hgy hvq.2).1 q huq.2 hvq.2

end Komorebi.InternalFiniteUnions
