import Komorebi.Foundation.InternalRankingConditions

/-!
# Internal bounded ranking by the union of compatible partial graphs

This construction uses only internally represented subsets and a well-order's
internal least-element property. It does not use external well-founded recursion.
-/

universe u v

namespace Komorebi.InternalBoundedRanking

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder
open InternalOrderGraphs InternalRankingConditions

variable {M : Type u} [language.Structure M]

theorem partial_ranking_set (h : AxiomSemantics M) (k w r offset : M) :
    ∃ c : M, ∀ g : M, member g c ↔ PartialRanking k w r offset g := by
  obtain ⟨p,hp⟩ := product_exists h w k
  obtain ⟨pp,hpp⟩ := h.powerset p
  let φ : language.Formula (Option (Fin 4)) :=
    partialRankingF (some 0) (some 1) (some 2) (some 3) none
  obtain ⟨c,hc⟩ := h.separation 4 φ ![k,w,r,offset] pp
  refine ⟨c,?_⟩
  intro g
  have hc' : member g c ↔ member g pp ∧ PartialRanking k w r offset g := by
    simpa [φ,assign] using hc g
  refine hc'.trans ?_
  constructor
  · exact fun hg => hg.2
  · intro hg
    obtain ⟨q,hq,hgq⟩ := hg.bounded
    have hqp : q = p := product_unique h hq hp
    subst q
    exact ⟨(hpp g).mpr hgq,hg⟩

theorem union_pairMember {g c a b : M} (hg : IsUnion g c) :
    PairMember a b g ↔ ∃ f : M, member f c ∧ PairMember a b f := by
  constructor
  · rintro ⟨p,hp,hpg⟩
    obtain ⟨f,hf,hpf⟩ := (hg p).mp hpg
    exact ⟨f,hf,p,hp,hpf⟩
  · rintro ⟨f,hf,p,hp,hpf⟩
    exact ⟨p,hp,(hg p).mpr ⟨f,hf,hpf⟩⟩

theorem union_partial_ranking (h : AxiomSemantics M) {k w r offset c g : M}
    (hr : WellOrderOn w r)
    (hc : ∀ f : M, member f c ↔ PartialRanking k w r offset f)
    (hg : IsUnion g c) : PartialRanking k w r offset g := by
  have hgf : ∀ x a b : M, PairMember x a g → PairMember x b g → a = b := by
    intro x a b hxa hxb
    obtain ⟨f,hfc,hxf⟩ := (union_pairMember hg).mp hxa
    obtain ⟨f',hf'c,hxf'⟩ := (union_pairMember hg).mp hxb
    exact partial_rankings_agree h hr ((hc f).mp hfc) ((hc f').mp hf'c) hxf hxf'
  refine ⟨?_,hgf,?_,?_⟩
  · obtain ⟨p,hp⟩ := product_exists h w k
    refine ⟨p,hp,?_⟩
    intro q hqg
    obtain ⟨f,hfc,hqf⟩ := (hg q).mp hqg
    obtain ⟨p',hp',hfp'⟩ := ((hc f).mp hfc).bounded
    have he : p' = p := product_unique h hp' hp
    exact he ▸ hfp' q hqf
  · intro x y a hya hxy
    obtain ⟨f,hfc,hyf⟩ := (union_pairMember hg).mp hya
    obtain ⟨b,hxb⟩ := ((hc f).mp hfc).downward x y a hyf hxy
    exact ⟨b,(union_pairMember hg).mpr ⟨f,hfc,hxb⟩⟩
  · intro x a hxa
    obtain ⟨f,hfc,hxfa⟩ := (union_pairMember hg).mp hxa
    have hf := (hc f).mp hfc
    have he : ∀ y b : M, PairMember y x r → (PairMember y b f ↔ PairMember y b g) := by
      intro y b hyx
      constructor
      · intro hyb
        exact (union_pairMember hg).mpr ⟨f,hfc,hyb⟩
      · intro hyb
        obtain ⟨bf,hybf⟩ := hf.downward y x a hxfa hyx
        have hbf : PairMember y bf g := (union_pairMember hg).mpr ⟨f,hfc,hybf⟩
        have heq := hgf y b bf hyb hbf
        exact heq.symm ▸ hybf
    exact (leastRank_congr he).mp (hf.recurrence x a hxfa)

/-- Add the least missing point. Recurrences at existing points are unchanged,
since a missing point cannot precede a point already in the downward-closed domain. -/
theorem partial_ranking_extend (h : AxiomSemantics M) {k w r offset g x a : M}
    (hr : WellOrderOn w r) (hg : PartialRanking k w r offset g)
    (hx : member x w) (hmissing : ¬ ∃ b : M, PairMember x b g)
    (hprev : ∀ y : M, PairMember y x r → ∃ b : M, PairMember y b g)
    (ha : LeastRank k r offset g x a) :
    ∃ f : M, PartialRanking k w r offset f ∧ PairMember x a f := by
  obtain ⟨f,hgf,hentries,hf⟩ := graph_append h g x a
  have old_congr : ∀ z value : M, PairMember z value g →
      ∀ y b : M, PairMember y z r → (PairMember y b g ↔ PairMember y b f) := by
    intro z value hz y b hyz
    constructor
    · intro hyb
      exact (hf y b).mpr (Or.inl hyb)
    · intro hyb
      rcases (hf y b).mp hyb with hybg | ⟨rfl,rfl⟩
      · exact hybg
      · exact False.elim (hmissing (hg.downward _ z value hz hyz))
  have new_congr : ∀ y b : M, PairMember y x r → (PairMember y b g ↔ PairMember y b f) := by
    intro y b hyx
    constructor
    · intro hyb
      exact (hf y b).mpr (Or.inl hyb)
    · intro hyb
      rcases (hf y b).mp hyb with hybg | ⟨rfl,rfl⟩
      · exact hybg
      · exact False.elim (hr.irrefl _ hyx)
  refine ⟨f,⟨?_,?_,?_,?_⟩,(hf x a).mpr (Or.inr ⟨rfl,rfl⟩)⟩
  · obtain ⟨p,hp,hgp⟩ := hg.bounded
    refine ⟨p,hp,?_⟩
    intro q hq
    rcases (hentries q).mp hq with hqg | hqpair
    · exact hgp q hqg
    · exact (hp q).mpr ⟨x,hx,a,ha.1.1,hqpair⟩
  · intro z b c hzb hzc
    rcases (hf z b).mp hzb with hzb | ⟨rfl,rfl⟩
    · rcases (hf z c).mp hzc with hzc | ⟨rfl,rfl⟩
      · exact hg.functional z b c hzb hzc
      · exact False.elim (hmissing ⟨b,hzb⟩)
    · rcases (hf _ c).mp hzc with hxc | ⟨_,rfl⟩
      · exact False.elim (hmissing ⟨c,hxc⟩)
      · rfl
  · intro y z b hzb hyz
    rcases (hf z b).mp hzb with hzbg | ⟨rfl,rfl⟩
    · obtain ⟨c,hyc⟩ := hg.downward y z b hzbg hyz
      exact ⟨c,(hf y c).mpr (Or.inl hyc)⟩
    · obtain ⟨c,hyc⟩ := hprev y hyz
      exact ⟨c,(hf y c).mpr (Or.inl hyc)⟩
  · intro z b hzb
    rcases (hf z b).mp hzb with hzbg | ⟨rfl,rfl⟩
    · exact (leastRank_congr (old_congr z b hzbg)).mp (hg.recurrence z b hzbg)
    · exact (leastRank_congr new_congr).mp ha

/-- Total internal ranking into K when every strict predecessor set is small.
This proves existence of the graph inside M rather than choosing an external map. -/
theorem bounded_ranking_exists (h : AxiomSemantics M) {k w r offset : M}
    (hk : Guard k) (hoff : member offset k) (hr : WellOrderOn w r)
    (hsmall : ∀ x p : M, member x w → Predecessors p w r x → Small k p) :
    ∃ g : M, FunctionGraph w k g ∧ InjectiveGraph w g ∧ PartialRanking k w r offset g := by
  classical
  obtain ⟨c,hc⟩ := partial_ranking_set h k w r offset
  obtain ⟨g,hg⟩ := h.union c
  have hpart := union_partial_ranking h hr hc hg
  have htotal : ∀ x : M, member x w → ∃ a : M, PairMember x a g := by
    intro x hx
    by_contra hmissing
    let φ : language.Formula (Option (Fin 1)) :=
      (exF (pairMemF (some none) none (some (some 0)))).not
    obtain ⟨missing,hmiss⟩ := h.separation 1 φ ![g] w
    have hmiss' : ∀ y : M, member y missing ↔
        member y w ∧ ¬ ∃ a : M, PairMember y a g := by
      intro y
      simpa [φ,assign] using hmiss y
    obtain ⟨y,hy,hmin⟩ := hr.least missing (fun y hy => ((hmiss' y).mp hy).1)
      ⟨x,(hmiss' x).mpr ⟨hx,hmissing⟩⟩
    have hyw := ((hmiss' y).mp hy).1
    have hynone := ((hmiss' y).mp hy).2
    have hprev : ∀ z : M, PairMember z y r → ∃ a : M, PairMember z a g := by
      intro z hzy
      by_contra hnone
      exact hmin z ((hmiss' z).mpr ⟨(hr.bounds z y hzy).1,hnone⟩) hzy
    obtain ⟨p,hp⟩ := predecessors_exists h w r y
    obtain ⟨a,ha⟩ := leastRank_exists h hk hoff hr hpart hp (hsmall y p hyw hp)
      (fun z hz => hprev z ((hp z).mp hz).2)
    obtain ⟨f,hf,hyaf⟩ := partial_ranking_extend h hr hpart hyw hynone hprev ha
    exact hynone ⟨a,(union_pairMember hg).mpr ⟨f,(hc f).mpr hf,hyaf⟩⟩
  have hfunc : FunctionGraph w k g :=
    ⟨hpart.bounded,fun x hx => by
      obtain ⟨a,hxa⟩ := htotal x hx
      exact ⟨a,hxa,fun b hxb => hpart.functional x b a hxb hxa⟩⟩
  refine ⟨g,hfunc,?_,hpart⟩
  intro x hx y hy a hxa hya
  rcases hr.total x y hx hy with hxy | he | hyx
  · exact False.elim (InternalOrdinalOrder.member_irrefl h a
      ((hpart.recurrence y a hya).1.2.2 x a hxy hxa))
  · exact he
  · exact False.elim (InternalOrdinalOrder.member_irrefl h a
      ((hpart.recurrence x a hxa).1.2.2 y a hyx hya))

end Komorebi.InternalBoundedRanking
