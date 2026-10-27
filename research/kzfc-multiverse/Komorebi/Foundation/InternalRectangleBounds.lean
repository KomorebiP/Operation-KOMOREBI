import Komorebi.Foundation.InternalLexicographicOrder

/-!
# Rowwise boundedness without assuming product smallness

An internal map from a rectangle of two small sets into K has bounded range.
The two successive bounds use the existing regular-cardinal guard on internal images.
-/

universe u v

namespace Komorebi.InternalRectangleBounds

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports InternalOrdinalOrder
open InternalOrderGraphs InternalRankingConditions InternalBoundedRanking InternalFiniteUnions
open InternalLexicographicOrder

variable {M : Type u} [language.Structure M]

def RowEval (f x y z : M) : Prop :=
  ∃ p : M, IsOrderedPair p x y ∧ PairMember p z f

def rowEvalF {α : Type v} (f x y z : α) : language.Formula α :=
  exF (pairF none (some x) (some y) ⊓ pairMemF none (some z) (some f))

@[simp]
theorem rowEvalF_realize {α : Type v} (f x y z : α) (e : α → M) :
    (rowEvalF f x y z).Realize e ↔ RowEval (e f) (e x) (e y) (e z) := by
  simp [rowEvalF,RowEval,assign]

theorem row_function (h : AxiomSemantics M) {a b w k f x : M}
    (hw : Product w a b) (hf : FunctionGraph w k f) (hx : member x a) :
    ∃ g : M, FunctionGraph b k g ∧
      ∀ y z : M, PairMember y z g ↔ RowEval f x y z := by
  let φ : language.Formula (Option (Option (Fin 2))) :=
    rowEvalF (some (some 0)) (some (some 1)) none (some none)
  obtain ⟨g,p,hp,hgp,hg⟩ := relationSet_exists h φ ![f,x] b k
  have hg' : ∀ y z : M, PairMember y z g ↔ RowEval f x y z := by
    intro y z
    have he : PairMember y z g ↔ member y b ∧ member z k ∧ RowEval f x y z := by
      simpa [φ,assign] using hg y z
    refine he.trans ?_
    constructor
    · exact fun he => he.2.2
    · rintro ⟨q,hq,hqz⟩
      obtain ⟨x',_,y',hy',hq'⟩ := (hw q).mp (functionGraph_pair_bounds hf hqz).1
      obtain ⟨rfl,rfl⟩ := orderedPair_injective hq' hq
      exact ⟨hy',(functionGraph_pair_bounds hf hqz).2,q,hq,hqz⟩
  refine ⟨g,⟨⟨p,hp,hgp⟩,?_⟩,hg'⟩
  intro y hy
  obtain ⟨q,hq⟩ := orderedPair_exists h x y
  obtain ⟨z,hqz,_⟩ := hf.2 q ((hw q).mpr ⟨x,hx,y,hy,hq⟩)
  refine ⟨z,(hg' y z).mpr ⟨q,hq,hqz⟩,?_⟩
  intro z' hyz'
  obtain ⟨q',hq',hq'z'⟩ := (hg' y z').mp hyz'
  have hqq : q' = q := orderedPair_unique h hq' hq
  subst q'
  exact functionGraph_value_unique hf hq'z' hqz

def RowBound (c f x b : M) : Prop :=
  ∀ y z : M, member y b → RowEval f x y z → member z c

def rowBoundF {α : Type v} (c f x b : α) : language.Formula α :=
  allF (let c := some c; let f := some f; let x := some x; let b := some b; let y := none
    allF ((memF (some y) (some b)).imp
      ((rowEvalF (some f) (some x) (some y) none).imp (memF none (some c)))))

@[simp]
theorem rowBoundF_realize {α : Type v} (c f x b : α) (e : α → M) :
    (rowBoundF c f x b).Realize e ↔ RowBound (e c) (e f) (e x) (e b) := by
  simp [rowBoundF,RowBound,assign]

theorem row_bound_exists (h : AxiomSemantics M) {k a b w f x : M}
    (hk : Guard k) (hw : Product w a b) (hf : FunctionGraph w k f)
    (hb : Small k b) (hx : member x a) :
    ∃ c : M, member c k ∧ RowBound c f x b := by
  obtain ⟨g,hg,hrow⟩ := row_function h hw hf hx
  obtain ⟨im,himk,hims,him⟩ := function_range_small h hg hb
  obtain ⟨c,hck,himc⟩ := hk.2.2 im himk hims
  refine ⟨c,hck,?_⟩
  intro y z hy hyz
  exact himc z ((him z).mpr ⟨y,hy,(hrow y z).mpr hyz⟩)

/-- The rectangle itself is not assumed small. Each row image is small, and
the internally selected family of row bounds is a small image of the row index set. -/
theorem rectangle_range_bounded (h : AxiomSemantics M) {k a b w f : M}
    (hk : Guard k) (ha : Small k a) (hb : Small k b)
    (hw : Product w a b) (hf : FunctionGraph w k f) :
    ∃ d : M, member d k ∧ ∀ p z : M, PairMember p z f → member z d := by
  let φ : language.Formula (Option (Option (Fin 2))) :=
    rowBoundF (some none) (some (some 0)) none (some (some 1))
  obtain ⟨rel,_,_,_,hrel⟩ := relationSet_exists h φ ![f,b] a k
  have hrel' : ∀ x c : M, PairMember x c rel ↔
      member x a ∧ member c k ∧ RowBound c f x b := by
    intro x c
    simpa [φ,assign] using hrel x c
  have htotal : ∀ x : M, member x a → ∃ c : M, member c k ∧ PairMember x c rel := by
    intro x hx
    obtain ⟨c,hck,hc⟩ := row_bound_exists h hk hw hf hb hx
    exact ⟨c,hck,(hrel' x c).mpr ⟨hx,hck,hc⟩⟩
  obtain ⟨sel,hsel,hselected⟩ := internal_selection h a k rel htotal
  obtain ⟨bounds,hbk,hbs,hbounds⟩ := function_range_small h hsel ha
  obtain ⟨d,hdk,hbd⟩ := hk.2.2 bounds hbk hbs
  refine ⟨d,hdk,?_⟩
  intro p z hpz
  obtain ⟨x,hxa,y,hyb,hp⟩ := (hw p).mp (functionGraph_pair_bounds hf hpz).1
  obtain ⟨c,hxc,_⟩ := hsel.2 x hxa
  have hc : RowBound c f x b := ((hrel' x c).mp (hselected x c hxc)).2.2
  have hcd : member c d := hbd c ((hbounds c).mpr ⟨x,hxa,hxc⟩)
  exact (ordinal_member hk.1.1 hdk).1 c hcd z (hc y z hyb ⟨p,hp,hpz⟩)

/-- Boundedness converts an internal injection of the rectangle into K into
the strict size witness needed by Small K. -/
theorem rectangle_small_of_injection (h : AxiomSemantics M) {k a b w f : M}
    (hk : Guard k) (ha : Small k a) (hb : Small k b)
    (hw : Product w a b) (hf : FunctionGraph w k f) (hi : InjectiveGraph w f) :
    Small k w := by
  obtain ⟨d,hdk,hfd⟩ := rectangle_range_bounded h hk ha hb hw hf
  refine ⟨d,hdk,f,graph_retype h hf ?_ ?_,hi⟩
  · intro p z hpz
    exact ⟨(functionGraph_pair_bounds hf hpz).1,hfd p z hpz⟩
  · intro p hp
    obtain ⟨z,hpz,_⟩ := hf.2 p hp
    exact ⟨z,hpz⟩

end Komorebi.InternalRectangleBounds
