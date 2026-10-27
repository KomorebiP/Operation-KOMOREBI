import Komorebi.Foundation.InternalSmallSupports

/-!
# The internal cone filter

This file constructs the filter and proves every filter and completeness law.
SmallUnionClosed is an explicit sufficient hypothesis. It is not silently
identified with the predecessor's ordinal-boundedness guard.
-/

universe u v

namespace Komorebi.InternalConeFilter

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport InternalConstraints InternalUltrafilterSelection InternalFineCompactness
open InternalSmallSupports

variable {M : Type u} [language.Structure M]

def ConeAbove (c p b : M) : Prop :=
  ∀ j : M, member j c ↔ member j p ∧ subset b j

def ContainsCone (s p b : M) : Prop :=
  ∀ j : M, member j p → subset b j → member j s

def IsConeFilter (f p : M) : Prop :=
  ∀ s : M, member s f ↔ subset s p ∧ ∃ b : M, member b p ∧ ContainsCone s p b

def coneAboveF {α : Type v} (c p b : α) : language.Formula α :=
  allF ((memF none (some c)).iff (memF none (some p) ⊓ subsetF (some b) none))

def containsConeF {α : Type v} (s p b : α) : language.Formula α :=
  allF ((memF none (some p)).imp ((subsetF (some b) none).imp (memF none (some s))))

@[simp]
theorem coneAboveF_realize {α : Type v} (c p b : α) (e : α → M) :
    (coneAboveF c p b).Realize e ↔ ConeAbove (e c) (e p) (e b) := by
  simp [coneAboveF,ConeAbove,assign]

@[simp]
theorem containsConeF_realize {α : Type v} (s p b : α) (e : α → M) :
    (containsConeF s p b).Realize e ↔ ContainsCone (e s) (e p) (e b) := by
  simp [containsConeF,ContainsCone,assign]

theorem coneAbove_exists (h : AxiomSemantics M) (p b : M) :
    ∃ c : M, ConeAbove c p b := by
  let φ : language.Formula (Option (Fin 1)) := subsetF (some 0) none
  obtain ⟨c,hc⟩ := h.separation 1 φ ![b] p
  exact ⟨c,fun j => by simpa [φ,assign] using hc j⟩

theorem coneAbove_unique (h : AxiomSemantics M) {c d p b : M}
    (hc : ConeAbove c p b) (hd : ConeAbove d p b) : c = d :=
  h.extensionality c d (fun j => (hc j).trans (hd j).symm)

theorem coneFilter_exists (h : AxiomSemantics M) (p : M) : ∃ f : M, IsConeFilter f p := by
  obtain ⟨pp,hpp⟩ := h.powerset p
  let φ : language.Formula (Option (Fin 1)) :=
    exF (memF none (some (some 0)) ⊓ containsConeF (some none) (some (some 0)) none)
  obtain ⟨f,hf⟩ := h.separation 1 φ ![p] pp
  refine ⟨f,?_⟩
  intro s
  have hf' : member s f ↔ member s pp ∧ ∃ b : M, member b p ∧ ContainsCone s p b := by
    simpa [φ,assign] using hf s
  exact hf'.trans (and_congr (hpp s) Iff.rfl)

theorem cone_mem (hf : IsConeFilter (M := M) f p) {b c : M}
    (hb : member b p) (hc : ConeAbove c p b) : member c f := by
  exact (hf c).mpr ⟨fun j hj => ((hc j).mp hj).1,b,hb,
    fun j hj hbj => (hc j).mpr ⟨hj,hbj⟩⟩

theorem relativeIntersection_exists (h : AxiomSemantics M) (p family : M) :
    ∃ r : M, RelInter r p family := by
  let φ : language.Formula (Option (Fin 1)) :=
    allF ((memF none (some (some 0))).imp (memF (some none) none))
  obtain ⟨r,hr⟩ := h.separation 1 φ ![family] p
  exact ⟨r,fun j => by simpa [φ,assign] using hr j⟩

/-- The cone filter is proper under the explicit small-union hypothesis.
Its generators are actual small supports, so every generating cone is nonempty. -/
theorem coneFilter_proper (h : AxiomSemantics M) {k i p f : M}
    (hind : HasInductiveMember k) (hun : SmallUnionClosed k)
    (hp : SmallPiecesSet p k i) (hf : IsConeFilter f p) : ProperFilterOn p f := by
  obtain ⟨e,he⟩ := h.empty
  have hep : member e p := (hp e).mpr
    ⟨fun z hz => False.elim (he z hz),empty_small h hind he⟩
  refine ⟨⟨?_,?_,?_,?_⟩,?_⟩
  · exact fun s hs => ((hf s).mp hs).1
  · exact (hf p).mpr ⟨fun j hj => hj,e,hep,fun j hj _ => hj⟩
  · intro s t hs hst htp
    obtain ⟨_,b,hb,hbs⟩ := (hf s).mp hs
    exact (hf t).mpr ⟨htp,b,hb,fun j hj hbj => hst j (hbs j hj hbj)⟩
  · intro s t hs ht
    obtain ⟨hsp,b,hb,hbs⟩ := (hf s).mp hs
    obtain ⟨htp,c,hc,hct⟩ := (hf t).mp ht
    obtain ⟨d,hdsmall,hd⟩ := binary_union_small h hind hun ((hp b).mp hb).2 ((hp c).mp hc).2
    have hdi : subset d i := by
      intro z hz
      rcases (hd z).mp hz with hz | hz
      · exact ((hp b).mp hb).1 z hz
      · exact ((hp c).mp hc).1 z hz
    have hdp : member d p := (hp d).mpr ⟨hdi,hdsmall⟩
    let φ : language.Formula (Option (Fin 1)) := memF none (some 0)
    obtain ⟨r,hr⟩ := h.separation 1 φ ![t] s
    have hr' : Inter r s t := by
      intro j
      simpa [φ,assign] using hr j
    refine ⟨r,hr',(hf r).mpr ⟨fun j hj => hsp j ((hr' j).mp hj).1,d,hdp,?_⟩⟩
    intro j hj hdj
    refine (hr' j).mpr ⟨hbs j hj ?_,hct j hj ?_⟩
    · exact fun z hz => hdj z ((hd z).mpr (Or.inl hz))
    · exact fun z hz => hdj z ((hd z).mpr (Or.inr hz))
  · intro z hz hzf
    obtain ⟨_,b,hb,hbz⟩ := (hf z).mp hzf
    exact hz b (hbz b hb (fun _ h => h))

/-- Choose cone generators with an internal graph, collect its image internally,
then take the small union of those supports. No external indexed family enters
completeness or Selection. -/
theorem coneFilter_complete (h : AxiomSemantics M) {k i p f : M}
    (hun : SmallUnionClosed k) (hp : SmallPiecesSet p k i)
    (hf : IsConeFilter f p) : CompleteOn k p f := by
  intro family hfamily hsmall
  let φ : language.Formula (Option (Option (Fin 1))) :=
    containsConeF none (some (some 0)) (some none)
  obtain ⟨rel,_,_,_,hrel⟩ := relationSet_exists h φ ![p] family p
  have hrel' : ∀ s b : M, PairMember s b rel ↔
      member s family ∧ member b p ∧ ContainsCone s p b := by
    intro s b
    simpa [φ,assign] using hrel s b
  have htotal : ∀ s : M, member s family → ∃ b : M,
      member b p ∧ PairMember s b rel := by
    intro s hs
    obtain ⟨_,b,hb,hbs⟩ := (hf s).mp (hfamily s hs)
    exact ⟨b,hb,(hrel' s b).mpr ⟨hs,hb,hbs⟩⟩
  obtain ⟨choice,hchoice,hchosen⟩ := internal_selection h family p rel htotal
  let ψ : language.Formula (Option (Option (Fin 1))) :=
    pairMemF none (some none) (some (some 0))
  have hfun : ∀ s : M, member s family →
      ∃! b : M, ψ.Realize (assign (assign ![choice] b) s) := by
    intro s hs
    obtain ⟨b,hsb,hunique⟩ := hchoice.2 s hs
    refine ⟨b,?_,?_⟩
    · simpa [ψ,assign] using hsb
    · intro c hc
      apply hunique c
      simpa [ψ,assign] using hc
  obtain ⟨supports,g,hg,hgraph,himage⟩ := definable_image_function h ψ ![choice] family hfun
  have himage' : ∀ b : M, member b supports ↔
      ∃ s : M, member s family ∧ PairMember s b choice := by
    intro b
    simpa [ψ,assign] using himage b
  have hgraph' : ∀ s b : M, PairMember s b g ↔
      member s family ∧ PairMember s b choice := by
    intro s b
    simpa [ψ,assign] using hgraph s b
  have hsupportSmall : Small k supports := by
    apply small_of_surjection h hg hsmall
    intro b hb
    obtain ⟨s,hs,hsb⟩ := (himage' b).mp hb
    exact ⟨s,hs,(hgraph' s b).mpr ⟨hs,hsb⟩⟩
  have hsupportP : subset supports p := by
    intro b hb
    obtain ⟨s,_,hsb⟩ := (himage' b).mp hb
    exact (functionGraph_pair_bounds hchoice hsb).2
  obtain ⟨support,hsupport⟩ := h.union supports
  have hsupportK : Small k support :=
    hun supports support hsupportSmall (fun b hb => ((hp b).mp (hsupportP b hb)).2) hsupport
  have hsupportI : subset support i := by
    intro z hz
    obtain ⟨b,hb,hzb⟩ := (hsupport z).mp hz
    exact ((hp b).mp (hsupportP b hb)).1 z hzb
  obtain ⟨r,hr⟩ := relativeIntersection_exists h p family
  refine ⟨r,hr,(hf r).mpr ⟨fun j hj => ((hr j).mp hj).1,
    support,(hp support).mpr ⟨hsupportI,hsupportK⟩,?_⟩⟩
  intro j hj hsupportj
  apply (hr j).mpr
  refine ⟨hj,?_⟩
  intro s hs
  obtain ⟨b,hsb,_⟩ := hchoice.2 s hs
  have hb : member b supports := (himage' b).mpr ⟨s,hs,hsb⟩
  have hcone : ContainsCone s p b := ((hrel' s b).mp (hchosen s b hsb)).2.2
  exact hcone j hj (fun z hz => hsupportj z ((hsupport z).mpr ⟨b,hb,hz⟩))

theorem coneFilter_fine (h : AxiomSemantics M) {k i p f : M}
    (hind : HasInductiveMember k) (hp : SmallPiecesSet p k i)
    (hf : IsConeFilter f p) : FineOn p i f := by
  intro point hpoint
  obtain ⟨b,hb⟩ := singleton_exists h point
  have hbi : subset b i := by
    intro z hz
    exact (hb z).mp hz ▸ hpoint
  have hbp : member b p := (hp b).mpr ⟨hbi,singleton_small h hind hb⟩
  obtain ⟨cone,hcone⟩ := coneAbove_exists h p b
  refine ⟨cone,cone_mem hf hbp hcone,?_⟩
  intro j
  refine (hcone j).trans (and_congr Iff.rfl ?_)
  constructor
  · intro hbj
    exact hbj point ((hb point).mpr rfl)
  · intro hpj z hz
    exact (hb z).mp hz ▸ hpj

/-- The extension-to-fine argument with its exact support-closure obligation.
This does not claim that Guard alone has yet discharged SmallUnionClosed. -/
theorem fine_of_extension_unionClosed (h : AxiomSemantics M) {k : M}
    (hind : HasInductiveMember k) (hun : SmallUnionClosed k) (hext : Extension k) :
    InternalFinePrinciple k := by
  intro i
  obtain ⟨p,hp⟩ := smallPiecesSet_exists h k i
  obtain ⟨f,hf⟩ := coneFilter_exists h p
  obtain ⟨u,hu,hfu,hcomplete⟩ := hext p f (coneFilter_proper h hind hun hp hf)
    (coneFilter_complete h hun hp hf)
  refine ⟨p,u,hp,hu,hcomplete,?_⟩
  intro point hpoint
  obtain ⟨c,hcf,hc⟩ := coneFilter_fine h hind hp hf point hpoint
  exact ⟨c,hfu c hcf,hc⟩

theorem compactness_of_extension_unionClosed (h : AxiomSemantics M) {k : M}
    (hg : Guard k) (hun : SmallUnionClosed k) (hext : Extension k) :
    ConstraintCompactness k :=
  internal_fine_implies_compactness h k (fine_of_extension_unionClosed h hg.2.1 hun hext)

theorem model_zfc_extension_unionClosed_compactness (hM : M ⊨ zfcTheory) {k : M}
    (hg : Guard k) (hun : SmallUnionClosed k) (hext : Extension k) :
    ConstraintCompactness k :=
  compactness_of_extension_unionClosed (model_zfc_iff_axiomSemantics.mp hM) hg hun hext

end Komorebi.InternalConeFilter
