import Komorebi.Foundation.InternalUnionReduction
import Komorebi.Foundation.InternalFineSupportClosure

/-! # Exact equivalences between the internal support obligations -/

universe u v

namespace Komorebi.InternalSupportEquivalence

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport InternalConstraints InternalUltrafilterSelection InternalFineCompactness
open InternalSmallSupports InternalConeFilter InternalFineSupportClosure InternalUnionReduction

variable {M : Type u} [language.Structure M]

def ProductSlice (s a y : M) : Prop :=
  ∀ q : M, member q s ↔ ∃ b : M, member b y ∧ IsOrderedPair q a b

def productSliceF {α : Type v} (s a y : α) : language.Formula α :=
  allF ((memF none (some s)).iff
    (exF (memF none (some (some y)) ⊓ pairF (some none) (some (some a)) none)))

@[simp]
theorem productSliceF_realize {α : Type v} (s a y : α) (e : α → M) :
    (productSliceF s a y).Realize e ↔ ProductSlice (e s) (e a) (e y) := by
  simp [productSliceF,ProductSlice,assign]

theorem productSlice_exists (h : AxiomSemantics M) (a y : M) :
    ∃ s : M, ProductSlice s a y := by
  obtain ⟨one,hone⟩ := singleton_exists h a
  obtain ⟨s,hs⟩ := product_exists h one y
  refine ⟨s,?_⟩
  intro q
  refine (hs q).trans ?_
  constructor
  · rintro ⟨a',ha',b,hb,hq⟩
    have he : a' = a := (hone a').mp ha'
    subst a'
    exact ⟨b,hb,hq⟩
  · rintro ⟨b,hb,hq⟩
    exact ⟨a,(hone a).mpr rfl,b,hb,hq⟩

theorem productSlice_embeds (h : AxiomSemantics M) {s a y : M}
    (hs : ProductSlice s a y) : Embeds s y := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    pairF none (some (some 0)) (some none)
  obtain ⟨f,p,hp,hfp,hf⟩ := relationSet_exists h φ ![a] s y
  have hf' : ∀ q b : M, PairMember q b f ↔
      member q s ∧ member b y ∧ IsOrderedPair q a b := by
    intro q b
    simpa [φ,assign] using hf q b
  refine ⟨f,⟨⟨p,hp,hfp⟩,?_⟩,?_⟩
  · intro q hq
    obtain ⟨b,hb,hqb⟩ := (hs q).mp hq
    refine ⟨b,(hf' q b).mpr ⟨hq,hb,hqb⟩,?_⟩
    intro c hc
    exact (orderedPair_injective ((hf' q c).mp hc).2.2 hqb).2
  · intro q _ r _ b hqb hrb
    exact orderedPair_unique h ((hf' q b).mp hqb).2.2 ((hf' r b).mp hrb).2.2

/-- Union closure implies product closure using the internal image of the slice
map a |-> {a} times Y. No ordinal comparison is needed in this direction. -/
theorem productClosed_of_unionClosed (h : AxiomSemantics M) {k : M}
    (hun : SmallUnionClosed k) : SmallProductClosed k := by
  intro x y p hx hy hp
  let φ : language.Formula (Option (Option (Fin 1))) :=
    productSliceF (some none) none (some (some 0))
  have hfun : ∀ a : M, member a x → ∃! s : M,
      φ.Realize (assign (assign ![y] s) a) := by
    intro a _
    obtain ⟨s,hs⟩ := productSlice_exists h a y
    refine ⟨s,?_,?_⟩
    · simpa [φ,assign] using hs
    · intro t ht
      have ht' : ProductSlice t a y := by simpa [φ,assign] using ht
      exact h.extensionality t s (fun q => (ht' q).trans (hs q).symm)
  obtain ⟨family,f,hf,hgraph,himage⟩ := definable_image_function h φ ![y] x hfun
  have hgraph' : ∀ a s : M, PairMember a s f ↔ member a x ∧ ProductSlice s a y := by
    intro a s
    simpa [φ,assign] using hgraph a s
  have himage' : ∀ s : M, member s family ↔ ∃ a : M, member a x ∧ ProductSlice s a y := by
    intro s
    simpa [φ,assign] using himage s
  have hsmall : Small k family := by
    apply small_of_surjection h hf hx
    intro s hs
    obtain ⟨a,ha,has⟩ := (himage' s).mp hs
    exact ⟨a,ha,(hgraph' a s).mpr ⟨ha,has⟩⟩
  have hmember : ∀ s : M, member s family → Small k s := by
    intro s hs
    obtain ⟨a,_,has⟩ := (himage' s).mp hs
    exact small_of_embeds h (productSlice_embeds h has) hy
  apply hun family p hsmall hmember
  intro q
  constructor
  · intro hq
    obtain ⟨a,ha,b,hb,hqab⟩ := (hp q).mp hq
    obtain ⟨s,hs⟩ := productSlice_exists h a y
    exact ⟨s,(himage' s).mpr ⟨a,ha,hs⟩,(hs q).mpr ⟨b,hb,hqab⟩⟩
  · rintro ⟨s,hs,hqs⟩
    obtain ⟨a,ha,has⟩ := (himage' s).mp hs
    obtain ⟨b,hb,hqab⟩ := (has q).mp hqs
    exact (hp q).mpr ⟨a,ha,b,hb,hqab⟩

theorem unionClosed_iff_productClosed (h : AxiomSemantics M) {k : M}
    (hg : Guard k) : SmallUnionClosed k ↔ SmallProductClosed k :=
  ⟨productClosed_of_unionClosed h,unionClosed_of_guard_productClosed h hg⟩

/-- Under the original guard and extension premise, the exact remaining
condition for the fine principle is internal small-product arithmetic. -/
theorem fine_iff_productClosed_of_extension (h : AxiomSemantics M) {k : M}
    (hg : Guard k) (hext : Extension k) :
    InternalFinePrinciple k ↔ SmallProductClosed k :=
  (fine_iff_unionClosed_of_extension h hg.2.1 hext).trans (unionClosed_iff_productClosed h hg)

theorem compactness_of_extension_productClosed (h : AxiomSemantics M) {k : M}
    (hg : Guard k) (hprod : SmallProductClosed k) (hext : Extension k) :
    ConstraintCompactness k :=
  compactness_of_extension_unionClosed h hg (unionClosed_of_guard_productClosed h hg hprod) hext

theorem model_zfc_extension_productClosed_compactness (hM : M ⊨ zfcTheory) {k : M}
    (hg : Guard k) (hprod : SmallProductClosed k) (hext : Extension k) :
    ConstraintCompactness k :=
  compactness_of_extension_productClosed (model_zfc_iff_axiomSemantics.mp hM) hg hprod hext

end Komorebi.InternalSupportEquivalence
