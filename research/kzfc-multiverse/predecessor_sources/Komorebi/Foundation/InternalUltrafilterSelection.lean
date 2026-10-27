import Komorebi.Foundation.InternalGraphTransport

/-!
# Complete internal ultrafilters select members of small internal covers

All covering families, complement families and cardinal witnesses are elements
of the model. Completeness is never applied to an arbitrary external family.
-/

universe u v

namespace Komorebi.InternalUltrafilterSelection

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport

variable {M : Type u} [language.Structure M]

theorem diff_exists (h : AxiomSemantics M) (x s : M) : ∃ d : M, Diff d x s := by
  let φ : language.Formula (Option (Fin 1)) := (memF none (some 0)).not
  obtain ⟨d,hd⟩ := h.separation 1 φ ![s] x
  exact ⟨d,fun z => by simpa [φ,assign] using hd z⟩

theorem diff_unique (h : AxiomSemantics M) {d e x s : M}
    (hd : Diff d x s) (he : Diff e x s) : d = e :=
  h.extensionality d e (fun z => (hd z).trans (he z).symm)

theorem diff_injective (h : AxiomSemantics M) {d x s t : M}
    (hs : subset s x) (ht : subset t x) (hd : Diff d x s) (he : Diff d x t) : s = t := by
  classical
  apply h.extensionality s t
  intro z
  constructor
  · intro hzs
    by_contra hzt
    exact ((hd z).mp ((he z).mpr ⟨hs z hzs,hzt⟩)).2 hzs
  · intro hzt
    by_contra hzs
    exact ((he z).mp ((hd z).mpr ⟨ht z hzt,hzs⟩)).2 hzt

def complementFamilyF {α : Type v} (d x b : α) : language.Formula α :=
  exF (memF none (some b) ⊓ diffF (some d) (some x) none)

@[simp]
theorem complementFamilyF_realize {α : Type v} (d x b : α) (e : α → M) :
    (complementFamilyF d x b).Realize e ↔
      ∃ s : M, member s (e b) ∧ Diff (e d) (e x) s := by
  simp [complementFamilyF,assign]

theorem complementFamily_exists (h : AxiomSemantics M) (x b : M) :
    ∃ d : M, ∀ t : M, member t d ↔ ∃ s : M, member s b ∧ Diff t x s := by
  obtain ⟨px,hpx⟩ := h.powerset x
  let φ : language.Formula (Option (Fin 2)) := complementFamilyF none (some 0) (some 1)
  obtain ⟨d,hd⟩ := h.separation 2 φ ![x,b] px
  refine ⟨d,?_⟩
  intro t
  have hd' : member t d ↔ member t px ∧ ∃ s : M, member s b ∧ Diff t x s := by
    simpa [φ,assign] using hd t
  refine hd'.trans ?_
  constructor
  · exact fun ht => ht.2
  · rintro ⟨s,hs,ht⟩
    exact ⟨(hpx t).mpr (fun z hz => ((ht z).mp hz).1),s,hs,ht⟩

theorem complementFamily_small (h : AxiomSemantics M) {k x b d : M}
    (hb : ∀ s : M, member s b → subset s x) (hsmall : Small k b)
    (hd : ∀ t : M, member t d ↔ ∃ s : M, member s b ∧ Diff t x s) : Small k d := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    diffF none (some (some 0)) (some none)
  obtain ⟨f,p,hp,hfp,hf⟩ := relationSet_exists h φ ![x] d b
  have hf' : ∀ t s : M, PairMember t s f ↔ member t d ∧ member s b ∧ Diff t x s := by
    intro t s
    simpa [φ,assign] using hf t s
  have hfunc : FunctionGraph d b f := by
    refine ⟨⟨p,hp,hfp⟩,?_⟩
    intro t ht
    obtain ⟨s,hs,hts⟩ := (hd t).mp ht
    refine ⟨s,(hf' t s).mpr ⟨ht,hs,hts⟩,?_⟩
    intro s' hts'
    have hs' := (hf' t s').mp hts'
    exact diff_injective h (hb s' hs'.2.1) (hb s hs) hs'.2.2 hts
  have hinj : InjectiveGraph d f := by
    intro t _ t' _ s hts ht's
    exact diff_unique h ((hf' t s).mp hts).2.2 ((hf' t' s).mp ht's).2.2
  exact small_of_embeds h ⟨f,hfunc,hinj⟩ hsmall

/-- The coded complement law implies properness; no ambient ultrafilter is used. -/
theorem ultrafilter_proper (h : AxiomSemantics M) {x u : M}
    (hu : UltrafilterOn x u) : ProperFilterOn x u := by
  refine ⟨hu.1,?_⟩
  intro e he heu
  obtain ⟨d,hd,hdu⟩ := hu.2 x (fun _ hz => hz)
  have hde : d = e := h.extensionality d e (by
    intro z
    constructor
    · intro hz
      exact False.elim (((hd z).mp hz).2 ((hd z).mp hz).1)
    · intro hz
      exact False.elim (he z hz))
  have hdnot : ¬ member d u := hdu.mp hu.1.2.1
  exact hdnot (hde.symm ▸ heu)

/-- Every small internally coded cover contains a filter-large member. Disjointness
is not required. The complement family is constructed and proved internally small. -/
theorem small_cover_selection (h : AxiomSemantics M) {k x u b : M}
    (hu : UltrafilterOn x u) (hc : CompleteOn k x u)
    (hb : ∀ s : M, member s b → subset s x) (hs : Small k b)
    (hcover : ∀ z : M, member z x → ∃ s : M, member s b ∧ member z s) :
    ∃ s : M, member s b ∧ member s u := by
  classical
  by_contra hnone
  have hnot : ∀ s : M, member s b → ¬ member s u := by
    intro s hsb hsu
    exact hnone ⟨s,hsb,hsu⟩
  obtain ⟨d,hd⟩ := complementFamily_exists h x b
  have hsmall : Small k d := complementFamily_small h hb hs hd
  have hdU : subset d u := by
    intro t ht
    obtain ⟨s,hsb,hts⟩ := (hd t).mp ht
    obtain ⟨t',ht',htu⟩ := hu.2 s (hb s hsb)
    have ht'u : member t' u := by
      by_contra ht'not
      exact hnot s hsb (htu.mpr ht'not)
    have htt' : t = t' := diff_unique h hts ht'
    exact htt'.symm ▸ ht'u
  obtain ⟨r,hr,hru⟩ := hc d hdU hsmall
  have hre : IsEmpty r := by
    intro z hzr
    have hrz := (hr z).mp hzr
    obtain ⟨s,hsb,hzs⟩ := hcover z hrz.1
    obtain ⟨t,ht⟩ := diff_exists h x s
    have htd : member t d := (hd t).mpr ⟨s,hsb,ht⟩
    exact ((ht z).mp (hrz.2 t htd)).2 hzs
  exact (ultrafilter_proper h hu).2 r hre hru


/-- Internal concentration on one fiber of a function with small value set.
The fiber family and its size bound are derived inside M before completeness is used. -/
theorem small_fiber_selection (h : AxiomSemantics M) {k x a u f : M}
    (hu : UltrafilterOn x u) (hc : CompleteOn k x u)
    (ha : Small k a) (hf : FunctionGraph x a f) :
    ∃ value : M, member value a ∧ ∃ s : M, member s u ∧
      ∀ z : M, member z s ↔ member z x ∧ PairMember z value f := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    pairMemF (some none) none (some (some 0))
  obtain ⟨r,_,_,_,hr⟩ := relationSet_exists h φ ![f] a x
  have hr' : ∀ value z : M, PairMember value z r ↔
      member value a ∧ member z x ∧ PairMember z value f := by
    intro value z
    simpa [φ,assign] using hr value z
  obtain ⟨b,hb⟩ := fiberFamily_exists h a x r
  let ψ : language.Formula (Option (Option (Fin 2))) :=
    fiberF (some none) none (some (some 0)) (some (some 1))
  obtain ⟨g,p,hp,hgp,hg⟩ := relationSet_exists h ψ ![x,r] a b
  have hg' : ∀ value s : M, PairMember value s g ↔
      member value a ∧ member s b ∧ Fiber s value x r := by
    intro value s
    simpa [ψ,assign] using hg value s
  have hmap : FunctionGraph a b g := by
    refine ⟨⟨p,hp,hgp⟩,?_⟩
    intro value hva
    obtain ⟨s,hs⟩ := fiber_exists h value x r
    have hsb : member s b := (hb s).mpr ⟨value,hva,hs⟩
    refine ⟨s,(hg' value s).mpr ⟨hva,hsb,hs⟩,?_⟩
    intro t hvt
    exact fiber_unique h ((hg' value t).mp hvt).2.2 hs
  have hsurj : ∀ s : M, member s b → ∃ value : M,
      member value a ∧ PairMember value s g := by
    intro s hsb
    obtain ⟨value,hva,hs⟩ := (hb s).mp hsb
    exact ⟨value,hva,(hg' value s).mpr ⟨hva,hsb,hs⟩⟩
  have hbsmall : Small k b := small_of_surjection h hmap ha hsurj
  have hbounded : ∀ s : M, member s b → subset s x := by
    intro s hsb
    obtain ⟨value,_,hs⟩ := (hb s).mp hsb
    exact fiber_subset hs
  have hcover : ∀ z : M, member z x → ∃ s : M, member s b ∧ member z s := by
    intro z hzx
    obtain ⟨value,hzv,_⟩ := hf.2 z hzx
    have hva : member value a := (functionGraph_pair_bounds hf hzv).2
    obtain ⟨s,hs⟩ := fiber_exists h value x r
    exact ⟨s,(hb s).mpr ⟨value,hva,hs⟩,
      (hs z).mpr ⟨hzx,(hr' value z).mpr ⟨hva,hzx,hzv⟩⟩⟩
  obtain ⟨s,hsb,hsu⟩ := small_cover_selection h hu hc hbounded hbsmall hcover
  obtain ⟨value,hva,hs⟩ := (hb s).mp hsb
  refine ⟨value,hva,s,hsu,?_⟩
  intro z
  constructor
  · intro hzs
    have hz := (hs z).mp hzs
    exact ⟨hz.1,((hr' value z).mp hz.2).2.2⟩
  · rintro ⟨hzx,hzv⟩
    exact (hs z).mpr ⟨hzx,(hr' value z).mpr ⟨hva,hzx,hzv⟩⟩

/-- A filter cannot concentrate on distinct fibers of the same function. -/
theorem selected_fiber_value_unique (h : AxiomSemantics M) {x a u f s t v w : M}
    (hu : UltrafilterOn x u) (hf : FunctionGraph x a f)
    (hsu : member s u) (htu : member t u)
    (hs : ∀ z : M, member z s ↔ member z x ∧ PairMember z v f)
    (ht : ∀ z : M, member z t ↔ member z x ∧ PairMember z w f) : v = w := by
  classical
  by_contra hne
  obtain ⟨r,hr,hru⟩ := hu.1.2.2.2 s t hsu htu
  have hre : IsEmpty r := by
    intro z hzr
    have hz := (hr z).mp hzr
    exact hne (functionGraph_value_unique hf ((hs z).mp hz.1).2 ((ht z).mp hz.2).2)
  exact (ultrafilter_proper h hu).2 r hre hru

/-- Actual encoded ZFC modelhood suffices for the set-existence part of the theorem.
The ultrafilter and its internal completeness remain explicit hypotheses. -/
theorem model_zfc_small_fiber_selection (hM : M ⊨ zfcTheory) {k x a u f : M}
    (hu : UltrafilterOn x u) (hc : CompleteOn k x u)
    (ha : Small k a) (hf : FunctionGraph x a f) :
    ∃ value : M, member value a ∧ ∃ s : M, member s u ∧
      ∀ z : M, member z s ↔ member z x ∧ PairMember z value f :=
  small_fiber_selection (model_zfc_iff_axiomSemantics.mp hM) hu hc ha hf

end Komorebi.InternalUltrafilterSelection
