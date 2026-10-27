import Komorebi.Foundation.InternalSmallSupports

/-!
# Reduce internal small-union closure to internal small-product closure

The regularity argument is performed with internally selected ordinal bounds.
The only remaining cardinal-arithmetic hypothesis is SmallProductClosed.
-/

universe u v

namespace Komorebi.InternalUnionReduction

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport InternalConstraints InternalSmallSupports

variable {M : Type u} [language.Structure M]

/-- Select internal size bounds, form their internal small image in K, and apply
the predecessor's actual bounded-small-subset guard. -/
theorem uniform_bound_for_small_family (h : AxiomSemantics M) {k family : M}
    (hg : Guard k) (hfamily : Small k family)
    (hmembers : ∀ s : M, member s family → Small k s) :
    ∃ bound : M, member bound k ∧ ∀ s : M, member s family → Embeds s bound := by
  let φ : language.Formula (Option (Option (Fin 0))) := embedsF none (some none)
  obtain ⟨rel,_,_,_,hrel⟩ := relationSet_exists h φ ![] family k
  have hrel' : ∀ s a : M, PairMember s a rel ↔
      member s family ∧ member a k ∧ Embeds s a := by
    intro s a
    simpa [φ,assign] using hrel s a
  have htotal : ∀ s : M, member s family → ∃ a : M, member a k ∧ PairMember s a rel := by
    intro s hs
    obtain ⟨a,ha,hemb⟩ := hmembers s hs
    exact ⟨a,ha,(hrel' s a).mpr ⟨hs,ha,hemb⟩⟩
  obtain ⟨f,hf,hselect⟩ := internal_selection h family k rel htotal
  let ψ : language.Formula (Option (Option (Fin 1))) :=
    pairMemF none (some none) (some (some 0))
  have hfun : ∀ s : M, member s family → ∃! a : M,
      ψ.Realize (assign (assign ![f] a) s) := by
    intro s hs
    obtain ⟨a,hsa,hunique⟩ := hf.2 s hs
    refine ⟨a,?_,?_⟩
    · simpa [ψ,assign] using hsa
    · intro b hb
      apply hunique b
      simpa [ψ,assign] using hb
  obtain ⟨bounds,g,hgmap,hgraph,himage⟩ := definable_image_function h ψ ![f] family hfun
  have hgraph' : ∀ s a : M, PairMember s a g ↔ member s family ∧ PairMember s a f := by
    intro s a
    simpa [ψ,assign] using hgraph s a
  have himage' : ∀ a : M, member a bounds ↔ ∃ s : M, member s family ∧ PairMember s a f := by
    intro a
    simpa [ψ,assign] using himage a
  have hbsmall : Small k bounds := by
    apply small_of_surjection h hgmap hfamily
    intro a ha
    obtain ⟨s,hs,hsa⟩ := (himage' a).mp ha
    exact ⟨s,hs,(hgraph' s a).mpr ⟨hs,hsa⟩⟩
  have hbk : subset bounds k := by
    intro a ha
    obtain ⟨s,_,hsa⟩ := (himage' a).mp ha
    exact (functionGraph_pair_bounds hf hsa).2
  obtain ⟨bound,hboundk,hbound⟩ := hg.2.2 bounds hbk hbsmall
  refine ⟨bound,hboundk,?_⟩
  intro s hs
  obtain ⟨a,hsa,_⟩ := hf.2 s hs
  have haBounds : member a bounds := (himage' a).mpr ⟨s,hs,hsa⟩
  have haBound : member a bound := hbound a haBounds
  have haSub : subset a bound := hg.1.1.2 bound hboundk a haBound
  have hsEmb : Embeds s a := ((hrel' s a).mp (hselect s a hsa)).2.2
  exact embeds_trans h hsEmb (embeds_of_subset h haSub)

def AssignedPair (x q selection owner : M) : Prop :=
  ∃ s g value : M, PairMember x s owner ∧ PairMember s g selection ∧
    PairMember x value g ∧ IsOrderedPair q s value

def assignedPairF {α : Type v} (x q selection owner : α) : language.Formula α :=
  exF (let x := some x; let q := some q; let selection := some selection
    let owner := some owner; let s := none
    exF (let x := some x; let q := some q; let selection := some selection
      let owner := some owner; let s := some s; let g := none
      exF (pairMemF (some x) (some s) (some owner) ⊓
        (pairMemF (some s) (some g) (some selection) ⊓
          (pairMemF (some x) none (some g) ⊓ pairF (some q) (some s) none)))))

@[simp]
theorem assignedPairF_realize {α : Type v} (x q selection owner : α) (e : α → M) :
    (assignedPairF x q selection owner).Realize e ↔
      AssignedPair (e x) (e q) (e selection) (e owner) := by
  simp [assignedPairF,AssignedPair,assign]

/-- The internal union injects into family times a uniform bound. Both the
member selector and the injection selector are internally coded graphs. -/
theorem union_embeds_family_product (h : AxiomSemantics M) {family whole bound : M}
    (hwhole : IsUnion whole family)
    (hemb : ∀ s : M, member s family → Embeds s bound) :
    ∃ target : M, Product target family bound ∧ Embeds whole target := by
  obtain ⟨big,hbig⟩ := product_exists h whole bound
  obtain ⟨graphs,hgraphs⟩ := h.powerset big
  let φ : language.Formula (Option (Option (Fin 1))) :=
    funcF none (some (some 0)) (some none) ⊓ injectiveF none (some none)
  obtain ⟨rel,_,_,_,hrel⟩ := relationSet_exists h φ ![bound] family graphs
  have hrel' : ∀ s g : M, PairMember s g rel ↔ member s family ∧ member g graphs ∧
      FunctionGraph s bound g ∧ InjectiveGraph s g := by
    intro s g
    simpa [φ,assign] using hrel s g
  have htotal : ∀ s : M, member s family → ∃ g : M,
      member g graphs ∧ PairMember s g rel := by
    intro s hs
    obtain ⟨g,hg,hig⟩ := hemb s hs
    have hgbig : subset g big := by
      intro z hzg
      obtain ⟨p,hp,hgp⟩ := hg.1
      obtain ⟨a,ha,b,hb,hab⟩ := (hp z).mp (hgp z hzg)
      exact (hbig z).mpr ⟨a,(hwhole a).mpr ⟨s,hs,ha⟩,b,hb,hab⟩
    have hgGraphs : member g graphs := (hgraphs g).mpr hgbig
    exact ⟨g,hgGraphs,(hrel' s g).mpr ⟨hs,hgGraphs,hg,hig⟩⟩
  obtain ⟨selection,hselection,hselected⟩ := internal_selection h family graphs rel htotal
  have selected_injection : ∀ s g : M, PairMember s g selection →
      FunctionGraph s bound g ∧ InjectiveGraph s g := by
    intro s g hsg
    exact ((hrel' s g).mp (hselected s g hsg)).2.2
  let ψ : language.Formula (Option (Option (Fin 0))) := memF none (some none)
  obtain ⟨owns,_,_,_,howns⟩ := relationSet_exists h ψ ![] whole family
  have howns' : ∀ x s : M, PairMember x s owns ↔
      member x whole ∧ member s family ∧ member x s := by
    intro x s
    simpa [ψ,assign] using howns x s
  have hownerTotal : ∀ x : M, member x whole →
      ∃ s : M, member s family ∧ PairMember x s owns := by
    intro x hx
    obtain ⟨s,hs,hxs⟩ := (hwhole x).mp hx
    exact ⟨s,hs,(howns' x s).mpr ⟨hx,hs,hxs⟩⟩
  obtain ⟨owner,howner,howned⟩ := internal_selection h whole family owns hownerTotal
  obtain ⟨target,htarget⟩ := product_exists h family bound
  let χ : language.Formula (Option (Option (Fin 2))) :=
    assignedPairF none (some none) (some (some 0)) (some (some 1))
  obtain ⟨f,p,hp,hfp,hf⟩ := relationSet_exists h χ ![selection,owner] whole target
  have hf' : ∀ x q : M, PairMember x q f ↔ member x whole ∧ member q target ∧
      AssignedPair x q selection owner := by
    intro x q
    simpa [χ,assign] using hf x q
  refine ⟨target,htarget,f,⟨⟨p,hp,hfp⟩,?_⟩,?_⟩
  · intro x hx
    obtain ⟨s,hxs,_⟩ := howner.2 x hx
    have hsFamily : member s family := (functionGraph_pair_bounds howner hxs).2
    have hxS : member x s := ((howns' x s).mp (howned x s hxs)).2.2
    obtain ⟨g,hsg,_⟩ := hselection.2 s hsFamily
    obtain ⟨hg,hig⟩ := selected_injection s g hsg
    obtain ⟨value,hxvalue,_⟩ := hg.2 x hxS
    have hvalue : member value bound := (functionGraph_pair_bounds hg hxvalue).2
    obtain ⟨q,hq⟩ := orderedPair_exists h s value
    have hqTarget : member q target := (htarget q).mpr ⟨s,hsFamily,value,hvalue,hq⟩
    refine ⟨q,(hf' x q).mpr ⟨hx,hqTarget,s,g,value,hxs,hsg,hxvalue,hq⟩,?_⟩
    intro q' hxq'
    obtain ⟨s',g',value',hxs',hsg',hxvalue',hq'⟩ := ((hf' x q').mp hxq').2.2
    have hss : s' = s := functionGraph_value_unique howner hxs' hxs
    subst s'
    have hgg : g' = g := functionGraph_value_unique hselection hsg' hsg
    subst g'
    have hvv : value' = value := functionGraph_value_unique hg hxvalue' hxvalue
    subst value'
    exact orderedPair_unique h hq' hq
  · intro x _ y _ q hxq hyq
    obtain ⟨s,g,value,_,hsg,hxvalue,hq⟩ := ((hf' x q).mp hxq).2.2
    obtain ⟨s',g',value',_,hsg',hyvalue',hq'⟩ := ((hf' y q).mp hyq).2.2
    obtain ⟨hss,hvv⟩ := orderedPair_injective hq hq'
    subst s'; subst value'
    have hgg : g' = g := functionGraph_value_unique hselection hsg' hsg
    subst g'
    obtain ⟨hg,hig⟩ := selected_injection s g hsg
    exact hig x (functionGraph_pair_bounds hg hxvalue).1
      y (functionGraph_pair_bounds hg hyvalue').1 value hxvalue hyvalue'

/-- The full internal regular-union argument, reduced to the single explicitly
stated small-product property. Guard is the unchanged predecessor guard. -/
theorem unionClosed_of_guard_productClosed (h : AxiomSemantics M) {k : M}
    (hg : Guard k) (hprod : SmallProductClosed k) : SmallUnionClosed k := by
  intro family whole hfamily hmembers hwhole
  obtain ⟨bound,hbound,huniform⟩ := uniform_bound_for_small_family h hg hfamily hmembers
  obtain ⟨target,htarget,hemb⟩ := union_embeds_family_product h hwhole huniform
  exact small_of_embeds h hemb (hprod family bound target hfamily (member_small h hbound) htarget)

end Komorebi.InternalUnionReduction
