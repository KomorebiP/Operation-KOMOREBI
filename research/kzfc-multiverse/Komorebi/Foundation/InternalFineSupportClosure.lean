import Komorebi.Foundation.InternalConeFilter

/-!
# Fine complete ultrafilters force internal small-union closure

This proves that the support-closure hypothesis of the cone construction is
necessary for the fine-ultrafilter conclusion. Every image family and every
intersection is internally represented.
-/

universe u v

namespace Komorebi.InternalFineSupportClosure

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport InternalConstraints InternalUltrafilterSelection InternalFineCompactness
open InternalSmallSupports InternalConeFilter

variable {M : Type u} [language.Structure M]

/-- Intersect a definably indexed small family of large sets. The image family
and its cardinal witness are constructed before completeness is invoked. -/
theorem small_definable_intersection (h : AxiomSemantics M) {n : ℕ} {k p u x : M}
    (hc : CompleteOn k p u) (hx : Small k x)
    (φ : language.Formula (Option (Option (Fin n)))) (e : Fin n → M)
    (hfun : ∀ a : M, member a x → ∃! s : M, φ.Realize (assign (assign e s) a))
    (hlarge : ∀ a s : M, member a x → φ.Realize (assign (assign e s) a) → member s u) :
    ∃ r : M, member r u ∧ ∀ j : M, member j r ↔ member j p ∧
      ∀ a : M, member a x → ∀ s : M, φ.Realize (assign (assign e s) a) → member j s := by
  obtain ⟨family,f,hf,hgraph,himage⟩ := definable_image_function h φ e x hfun
  have hsmall : Small k family := by
    apply small_of_surjection h hf hx
    intro s hs
    obtain ⟨a,ha,has⟩ := (himage s).mp hs
    exact ⟨a,ha,(hgraph a s).mpr ⟨ha,has⟩⟩
  have hsub : subset family u := by
    intro s hs
    obtain ⟨a,ha,has⟩ := (himage s).mp hs
    exact hlarge a s ha has
  obtain ⟨r,hr,hru⟩ := hc family hsub hsmall
  refine ⟨r,hru,?_⟩
  intro j
  refine (hr j).trans (and_congr Iff.rfl ?_)
  constructor
  · intro hall a ha s has
    exact hall s ((himage s).mpr ⟨a,ha,has⟩)
  · intro hall s hs
    obtain ⟨a,ha,has⟩ := (himage s).mp hs
    exact hall a ha s has

def PointCone (c p point : M) : Prop :=
  ∀ j : M, member j c ↔ member j p ∧ member point j

def pointConeF {α : Type v} (c p point : α) : language.Formula α :=
  allF ((memF none (some c)).iff (memF none (some p) ⊓ memF (some point) none))

@[simp]
theorem pointConeF_realize {α : Type v} (c p point : α) (e : α → M) :
    (pointConeF c p point).Realize e ↔ PointCone (e c) (e p) (e point) := by
  simp [pointConeF,PointCone,assign]

/-- Fineness for points upgrades to largeness of the cone above every small
support. This upgrade uses completeness and an internally constructed cone family. -/
theorem large_cone_of_small_support (h : AxiomSemantics M) {k i p u b : M}
    (hfine : FineOn p i u) (hc : CompleteOn k p u)
    (hbi : subset b i) (hb : Small k b) :
    ∃ c : M, member c u ∧ ConeAbove c p b := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    pointConeF (some none) (some (some 0)) none
  have hfun : ∀ a : M, member a b → ∃! s : M,
      φ.Realize (assign (assign ![p] s) a) := by
    intro a ha
    obtain ⟨s,_,hs⟩ := hfine a (hbi a ha)
    refine ⟨s,?_,?_⟩
    · simpa [φ,assign,PointCone] using hs
    · intro t ht
      have ht' : PointCone t p a := by simpa [φ,assign] using ht
      exact h.extensionality t s (fun j => (ht' j).trans (hs j).symm)
  have hlarge : ∀ a s : M, member a b →
      φ.Realize (assign (assign ![p] s) a) → member s u := by
    intro a s ha hs
    have hs' : PointCone s p a := by simpa [φ,assign] using hs
    obtain ⟨t,htu,ht⟩ := hfine a (hbi a ha)
    have hst : s = t := h.extensionality s t (fun j => (hs' j).trans (ht j).symm)
    exact hst.symm ▸ htu
  obtain ⟨r,hru,hr⟩ := small_definable_intersection h hc hb φ ![p] hfun hlarge
  refine ⟨r,hru,?_⟩
  intro j
  refine (hr j).trans ?_
  constructor
  · rintro ⟨hjp,hall⟩
    refine ⟨hjp,?_⟩
    intro a ha
    obtain ⟨s,_,hs⟩ := hfine a (hbi a ha)
    have hsφ : φ.Realize (assign (assign ![p] s) a) := by
      simpa [φ,assign,PointCone] using hs
    exact ((hs j).mp (hall a ha s hsφ)).2
  · rintro ⟨hjp,hbj⟩
    refine ⟨hjp,?_⟩
    intro a ha s hs
    have hs' : PointCone s p a := by simpa [φ,assign] using hs
    exact (hs' j).mpr ⟨hjp,hbj a ha⟩

/-- The all-index-set fine principle implies closure under internally small
unions. This needs no guard and assumes no external cardinality correctness. -/
theorem unionClosed_of_internalFine (h : AxiomSemantics M) {k : M}
    (hfine : InternalFinePrinciple k) : SmallUnionClosed k := by
  intro b i hb hmembers hi
  obtain ⟨p,u,hp,hu,hc,hf⟩ := hfine i
  have hsi : ∀ s : M, member s b → subset s i := by
    intro s hs z hz
    exact (hi z).mpr ⟨s,hs,hz⟩
  let φ : language.Formula (Option (Option (Fin 1))) :=
    coneAboveF (some none) (some (some 0)) none
  have hfun : ∀ s : M, member s b → ∃! c : M,
      φ.Realize (assign (assign ![p] c) s) := by
    intro s hs
    obtain ⟨c,_,hcone⟩ := large_cone_of_small_support h hf hc (hsi s hs) (hmembers s hs)
    refine ⟨c,?_,?_⟩
    · simpa [φ,assign] using hcone
    · intro d hd
      apply coneAbove_unique h (p := p) (b := s) _ hcone
      simpa [φ,assign] using hd
  have hlarge : ∀ s c : M, member s b →
      φ.Realize (assign (assign ![p] c) s) → member c u := by
    intro s c hs hcφ
    have hcone : ConeAbove c p s := by simpa [φ,assign] using hcφ
    obtain ⟨d,hdu,hd⟩ := large_cone_of_small_support h hf hc (hsi s hs) (hmembers s hs)
    exact (coneAbove_unique h hcone hd).symm ▸ hdu
  obtain ⟨r,hru,hr⟩ := small_definable_intersection h hc hb φ ![p] hfun hlarge
  have hnonempty : ∃ j : M, member j r := by
    by_contra hn
    exact (ultrafilter_proper h hu).2 r (fun j hj => hn ⟨j,hj⟩) hru
  obtain ⟨j,hjr⟩ := hnonempty
  obtain ⟨hjp,hall⟩ := (hr j).mp hjr
  have hij : subset i j := by
    intro z hz
    obtain ⟨s,hs,hzs⟩ := (hi z).mp hz
    obtain ⟨c,_,hcone⟩ := large_cone_of_small_support h hf hc (hsi s hs) (hmembers s hs)
    have hcφ : φ.Realize (assign (assign ![p] c) s) := by simpa [φ,assign] using hcone
    exact ((hcone j).mp (hall s hs c hcφ)).2 z hzs
  exact small_of_subset h hij ((hp j).mp hjp).2

/-- With filter extension given, small-union closure is both necessary and
sufficient for the fine principle, under the weak inductive-member condition. -/
theorem fine_iff_unionClosed_of_extension (h : AxiomSemantics M) {k : M}
    (hind : HasInductiveMember k) (hext : Extension k) :
    InternalFinePrinciple k ↔ SmallUnionClosed k :=
  ⟨unionClosed_of_internalFine h,fun hun => fine_of_extension_unionClosed h hind hun hext⟩

theorem model_zfc_fine_iff_unionClosed_of_extension (hM : M ⊨ zfcTheory) {k : M}
    (hg : Guard k) (hext : Extension k) :
    InternalFinePrinciple k ↔ SmallUnionClosed k :=
  fine_iff_unionClosed_of_extension (model_zfc_iff_axiomSemantics.mp hM) hg.2.1 hext

end Komorebi.InternalFineSupportClosure
