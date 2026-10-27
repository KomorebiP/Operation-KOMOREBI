import Komorebi.Foundation.InternalOrderGraphs

/-!
# Definable partial rankings bounded by an internally regular cardinal

The recurrence chooses the least ordinal bound of preceding values, above an
offset. Partial rankings are internal graph codes. They are not external maps.
-/

universe u v

namespace Komorebi.InternalRankingConditions

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder
open InternalOrderGraphs

variable {M : Type u} [language.Structure M]

def RankUpper (k r offset g x y : M) : Prop :=
  member y k ∧ subset offset y ∧
    ∀ a b : M, PairMember a x r → PairMember a b g → member b y

def LeastRank (k r offset g x y : M) : Prop :=
  RankUpper k r offset g x y ∧
    ∀ z : M, RankUpper k r offset g x z → subset y z

def rankUpperF {α : Type v} (k r offset g x y : α) : language.Formula α :=
  memF y k ⊓ (subsetF offset y ⊓
    allF (allF ((pairMemF (some none) (some (some x)) (some (some r))).imp
      ((pairMemF (some none) none (some (some g))).imp (memF none (some (some y)))))))

def leastRankF {α : Type v} (k r offset g x y : α) : language.Formula α :=
  rankUpperF k r offset g x y ⊓
    allF ((rankUpperF (some k) (some r) (some offset) (some g) (some x) none).imp
      (subsetF (some y) none))

@[simp]
theorem rankUpperF_realize {α : Type v} (k r offset g x y : α) (e : α → M) :
    (rankUpperF k r offset g x y).Realize e ↔
      RankUpper (e k) (e r) (e offset) (e g) (e x) (e y) := by
  simp [rankUpperF,RankUpper,assign]

@[simp]
theorem leastRankF_realize {α : Type v} (k r offset g x y : α) (e : α → M) :
    (leastRankF k r offset g x y).Realize e ↔
      LeastRank (e k) (e r) (e offset) (e g) (e x) (e y) := by
  simp [leastRankF,LeastRank,assign]

/-- No existence property or desired totality is included in this structure. -/
structure PartialRanking (k w r offset g : M) : Prop where
  bounded : ∃ p : M, Product p w k ∧ subset g p
  functional : ∀ x a b : M, PairMember x a g → PairMember x b g → a = b
  downward : ∀ x y a : M, PairMember y a g → PairMember x y r →
    ∃ b : M, PairMember x b g
  recurrence : ∀ x a : M, PairMember x a g → LeastRank k r offset g x a

def functionalGraphF {α : Type v} (g : α) : language.Formula α :=
  allF (let g := some g; let x := none
    allF (let g := some g; let x := some x; let a := none
      allF ((pairMemF (some x) (some a) (some g)).imp
        ((pairMemF (some x) none (some g)).imp (eqF (some a) none)))))

def downwardGraphF {α : Type v} (r g : α) : language.Formula α :=
  allF (let r := some r; let g := some g; let x := none
    allF (let r := some r; let g := some g; let x := some x; let y := none
      allF ((pairMemF (some y) none (some g)).imp
        ((pairMemF (some x) (some y) (some r)).imp
          (exF (pairMemF (some (some x)) none (some (some g))))))))

def rankRecurrenceF {α : Type v} (k r offset g : α) : language.Formula α :=
  allF (allF ((pairMemF (some none) none (some (some g))).imp
    (leastRankF (some (some k)) (some (some r)) (some (some offset))
      (some (some g)) (some none) none)))

def partialRankingF {α : Type v} (k w r offset g : α) : language.Formula α :=
  (exF (prodF none (some w) (some k) ⊓ subsetF (some g) none)) ⊓
    (functionalGraphF g ⊓ (downwardGraphF r g ⊓ rankRecurrenceF k r offset g))

@[simp]
theorem partialRankingF_realize {α : Type v} (k w r offset g : α) (e : α → M) :
    (partialRankingF k w r offset g).Realize e ↔
      PartialRanking (e k) (e w) (e r) (e offset) (e g) := by
  simp only [partialRankingF, functionalGraphF, downwardGraphF, rankRecurrenceF, Formula.realize_inf, exF_realize, prodF_internal,
    subsetF_realize, allF_realize, Formula.realize_imp, pairMemF_realize,
    eqF_realize, leastRankF_realize, assign]
  constructor
  · rintro ⟨hb,hf,hd,hr⟩
    exact ⟨hb,hf,hd,hr⟩
  · intro h
    exact ⟨h.bounded,h.functional,h.downward,h.recurrence⟩

theorem partial_pair_bounds {k w r offset g x a : M}
    (hg : PartialRanking k w r offset g) (hxa : PairMember x a g) :
    member x w ∧ member a k := by
  obtain ⟨p,hp,hgp⟩ := hg.bounded
  obtain ⟨q,hq,hqg⟩ := hxa
  obtain ⟨x',hx',a',ha',hq'⟩ := (hp q).mp (hgp q hqg)
  obtain ⟨rfl,rfl⟩ := orderedPair_injective hq hq'
  exact ⟨hx',ha'⟩

theorem rankUpper_congr {k r offset g f x y : M}
    (he : ∀ a b : M, PairMember a x r → (PairMember a b g ↔ PairMember a b f)) :
    RankUpper k r offset g x y ↔ RankUpper k r offset f x y := by
  constructor
  · rintro ⟨hy,ho,hb⟩
    exact ⟨hy,ho,fun a b hax hab => hb a b hax ((he a b hax).mpr hab)⟩
  · rintro ⟨hy,ho,hb⟩
    exact ⟨hy,ho,fun a b hax hab => hb a b hax ((he a b hax).mp hab)⟩

theorem leastRank_congr {k r offset g f x y : M}
    (he : ∀ a b : M, PairMember a x r → (PairMember a b g ↔ PairMember a b f)) :
    LeastRank k r offset g x y ↔ LeastRank k r offset f x y := by
  constructor
  · rintro ⟨hy,hmin⟩
    exact ⟨rankUpper_congr he |>.mp hy,
      fun z hz => hmin z (rankUpper_congr he |>.mpr hz)⟩
  · rintro ⟨hy,hmin⟩
    exact ⟨rankUpper_congr he |>.mpr hy,
      fun z hz => hmin z (rankUpper_congr he |>.mp hz)⟩

theorem leastRank_unique (h : AxiomSemantics M) {k r offset g x y z : M}
    (hy : LeastRank k r offset g x y) (hz : LeastRank k r offset g x z) : y = z :=
  h.extensionality y z (fun a => ⟨hy.2 z hz.1 a,hz.2 y hy.1 a⟩)

/-- A small predecessor graph has a least ordinal upper bound inside K.
Regularity is used only on the internal image of that small predecessor set. -/
theorem leastRank_exists (h : AxiomSemantics M) {k w r offset g x p : M}
    (hk : Guard k) (ho : member offset k) (hr : WellOrderOn w r)
    (hg : PartialRanking k w r offset g) (hp : Predecessors p w r x)
    (hs : Small k p) (ht : ∀ a : M, member a p → ∃ b : M, PairMember a b g) :
    ∃ y : M, LeastRank k r offset g x y := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    pairMemF none (some none) (some (some 0))
  obtain ⟨f,b,hb,hfb,hf⟩ := relationSet_exists h φ ![g] p k
  have hf' : ∀ a v : M, PairMember a v f ↔ member a p ∧ member v k ∧ PairMember a v g := by
    intro a v
    simpa [φ,assign] using hf a v
  have hfunc : FunctionGraph p k f := by
    refine ⟨⟨b,hb,hfb⟩,?_⟩
    intro a ha
    obtain ⟨v,hav⟩ := ht a ha
    refine ⟨v,(hf' a v).mpr ⟨ha,(partial_pair_bounds hg hav).2,hav⟩,?_⟩
    intro v' hav'
    exact hg.functional a v' v ((hf' a v').mp hav').2.2 hav
  obtain ⟨im,himk,hsmall,him⟩ := function_range_small h hfunc hs
  obtain ⟨bound,hbound,himb⟩ := hk.2.2 im himk hsmall
  have he : ∃ y : M, RankUpper k r offset g x y := by
    have hchoose : ∃ y : M, member y k ∧ subset offset y ∧ subset bound y := by
      rcases ordinal_subset_total h (ordinal_member hk.1.1 ho)
        (ordinal_member hk.1.1 hbound) with hab | hba
      · exact ⟨bound,hbound,hab,fun _ hb => hb⟩
      · exact ⟨offset,ho,fun _ ho => ho,hba⟩
    obtain ⟨y,hyk,hoy,hby⟩ := hchoose
    refine ⟨y,hyk,hoy,?_⟩
    intro a v hax hav
    have hap : member a p := (hp a).mpr ⟨(hr.bounds a x hax).1,hax⟩
    have havf : PairMember a v f := (hf' a v).mpr ⟨hap,(partial_pair_bounds hg hav).2,hav⟩
    exact hby v (himb v ((him v).mpr ⟨a,hap,havf⟩))
  let ψ : language.Formula (Option (Fin 5)) :=
    rankUpperF (some 0) (some 1) (some 2) (some 3) (some 4) none
  obtain ⟨bounds,hbounds⟩ := h.separation 5 ψ ![k,r,offset,g,x] k
  have hbounds' : ∀ y : M, member y bounds ↔ RankUpper k r offset g x y := by
    intro y
    have heq : member y bounds ↔ member y k ∧ RankUpper k r offset g x y := by
      simpa [ψ,assign] using hbounds y
    exact heq.trans ⟨fun hy => hy.2,fun hy => ⟨hy.1,hy⟩⟩
  obtain ⟨y,hy,hmin⟩ := ordinal_set_has_least h
    (fun y hy => ordinal_member hk.1.1 ((hbounds' y).mp hy).1)
    (by obtain ⟨y,hy⟩ := he; exact ⟨y,(hbounds' y).mpr hy⟩)
  refine ⟨y,(hbounds' y).mp hy,?_⟩
  intro z hz
  exact (ordinal_subset_iff h (ordinal_member hk.1.1 ((hbounds' y).mp hy).1)
    (ordinal_member hk.1.1 hz.1)).mpr (hmin z ((hbounds' z).mpr hz))

/-- Two partial rankings agree wherever both are defined. The least
disagreement is selected from an internally represented subset of W. -/
theorem partial_rankings_agree (h : AxiomSemantics M) {k w r offset g f x a b : M}
    (hr : WellOrderOn w r) (hg : PartialRanking k w r offset g)
    (hf : PartialRanking k w r offset f)
    (hxa : PairMember x a g) (hxb : PairMember x b f) : a = b := by
  classical
  by_contra hne
  let φ : language.Formula (Option (Fin 2)) :=
    exF (exF (pairMemF (some (some none)) (some none) (some (some (some 0))) ⊓
      (pairMemF (some (some none)) none (some (some (some 1))) ⊓
        (eqF (some none) none).not)))
  obtain ⟨s,hs⟩ := h.separation 2 φ ![g,f] w
  have hs' : ∀ z : M, member z s ↔ member z w ∧
      ∃ a b : M, PairMember z a g ∧ PairMember z b f ∧ a ≠ b := by
    intro z
    simpa [φ,assign] using hs z
  obtain ⟨z,hzs,hmin⟩ := hr.least s (fun z hz => ((hs' z).mp hz).1)
    ⟨x,(hs' x).mpr ⟨(partial_pair_bounds hg hxa).1,a,b,hxa,hxb,hne⟩⟩
  obtain ⟨_,a',b',hza,hzb,hne'⟩ := (hs' z).mp hzs
  have he : ∀ y v : M, PairMember y z r → (PairMember y v g ↔ PairMember y v f) := by
    intro y v hyz
    obtain ⟨vg,hyg⟩ := hg.downward y z a' hza hyz
    obtain ⟨vf,hyf⟩ := hf.downward y z b' hzb hyz
    have hv : vg = vf := by
      by_contra hnv
      exact hmin y ((hs' y).mpr ⟨(hr.bounds y z hyz).1,vg,vf,hyg,hyf,hnv⟩) hyz
    subst vf
    constructor
    · intro hyv
      have hev := hg.functional y v vg hyv hyg
      exact hev.symm ▸ hyf
    · intro hyv
      have hev := hf.functional y v vg hyv hyf
      exact hev.symm ▸ hyg
  exact hne' (leastRank_unique h (hg.recurrence z a' hza)
    ((leastRank_congr he).mpr (hf.recurrence z b' hzb)))

end Komorebi.InternalRankingConditions
