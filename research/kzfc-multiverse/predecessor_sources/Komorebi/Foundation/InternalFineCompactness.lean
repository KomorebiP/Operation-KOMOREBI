import Komorebi.Foundation.InternalConstraints
import Komorebi.Foundation.InternalUltrafilterSelection

/-!
# Compactness from an internal fine complete ultrafilter

The proof is carried out in an arbitrary membership structure satisfying the
explicit ZFC theory. Every assignment selector, coordinate graph, fiber family,
intersection and final assignment is an internal set. Ultrafilter existence
remains an explicit hypothesis and is not derived by an external choice shortcut.
-/

universe u v

namespace Komorebi.InternalFineCompactness

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection
open InternalGraphTransport InternalConstraints InternalUltrafilterSelection

variable {M : Type u} [language.Structure M]

def Eval (l j v a : M) : Prop := ∃ g : M, PairMember j g l ∧ PairMember v a g

def evalF {α : Type v} (l j v a : α) : language.Formula α :=
  exF (pairMemF (some j) none (some l) ⊓ pairMemF (some v) (some a) none)

@[simp]
theorem evalF_realize {α : Type v} (l j v a : α) (e : α → M) :
    (evalF l j v a).Realize e ↔ Eval (e l) (e j) (e v) (e a) := by
  simp [evalF,Eval,assign]

def EvalFiber (s p l v a : M) : Prop :=
  ∀ j : M, member j s ↔ member j p ∧ Eval l j v a

def evalFiberF {α : Type v} (s p l v a : α) : language.Formula α :=
  allF ((memF none (some s)).iff
    (memF none (some p) ⊓ evalF (some l) none (some v) (some a)))

@[simp]
theorem evalFiberF_realize {α : Type v} (s p l v a : α) (e : α → M) :
    (evalFiberF s p l v a).Realize e ↔ EvalFiber (e s) (e p) (e l) (e v) (e a) := by
  simp [evalFiberF,EvalFiber,assign]

def Concentrates (p l u v a : M) : Prop := ∃ s : M, member s u ∧ EvalFiber s p l v a

def concentratesF {α : Type v} (p l u v a : α) : language.Formula α :=
  exF (memF none (some u) ⊓ evalFiberF none (some p) (some l) (some v) (some a))

@[simp]
theorem concentratesF_realize {α : Type v} (p l u v a : α) (e : α → M) :
    (concentratesF p l u v a).Realize e ↔ Concentrates (e p) (e l) (e u) (e v) (e a) := by
  simp [concentratesF,Concentrates,assign]

theorem coordinate_function (h : AxiomSemantics M) {p e v a l point : M}
    (he : FunctionSpace e v a) (hl : FunctionGraph p e l) (hpoint : member point v) :
    ∃ f : M, FunctionGraph p a f ∧ ∀ j value : M, PairMember j value f ↔ Eval l j point value := by
  let φ : language.Formula (Option (Option (Fin 2))) :=
    evalF (some (some 0)) none (some (some 1)) (some none)
  obtain ⟨f,b,hb,hfb,hf⟩ := relationSet_exists h φ ![l,point] p a
  have hf' : ∀ j value : M, PairMember j value f ↔ Eval l j point value := by
    intro j value
    have hf'' : PairMember j value f ↔ member j p ∧ member value a ∧ Eval l j point value := by
      simpa [φ,assign] using hf j value
    refine hf''.trans ?_
    constructor
    · exact fun h => h.2.2
    · rintro ⟨g,hjg,hpg⟩
      have hg : FunctionGraph v a g := (he g).mp (functionGraph_pair_bounds hl hjg).2
      exact ⟨(functionGraph_pair_bounds hl hjg).1,(functionGraph_pair_bounds hg hpg).2,g,hjg,hpg⟩
  refine ⟨f,⟨⟨b,hb,hfb⟩,?_⟩,hf'⟩
  intro j hj
  obtain ⟨g,hjg,_⟩ := hl.2 j hj
  have hg : FunctionGraph v a g := (he g).mp (functionGraph_pair_bounds hl hjg).2
  obtain ⟨value,hgv,_⟩ := hg.2 point hpoint
  refine ⟨value,(hf' j value).mpr ⟨g,hjg,hgv⟩,?_⟩
  intro value' hjv'
  obtain ⟨g',hjg',hgv'⟩ := (hf' j value').mp hjv'
  have hgg' : g' = g := functionGraph_value_unique hl hjg' hjg
  subst g'
  exact functionGraph_value_unique hg hgv' hgv

theorem concentration_exists (h : AxiomSemantics M) {k p e v a l u point : M}
    (he : FunctionSpace e v a) (hl : FunctionGraph p e l) (hpoint : member point v)
    (hu : UltrafilterOn p u) (hc : CompleteOn k p u) (ha : Small k a) :
    ∃ value : M, member value a ∧ Concentrates p l u point value := by
  obtain ⟨f,hf,hcoord⟩ := coordinate_function h he hl hpoint
  obtain ⟨value,hva,s,hsu,hs⟩ := small_fiber_selection h hu hc ha hf
  exact ⟨value,hva,s,hsu,fun j => (hs j).trans (and_congr Iff.rfl (hcoord j value))⟩

theorem concentration_unique (h : AxiomSemantics M) {p e v a l u point b c : M}
    (he : FunctionSpace e v a) (hl : FunctionGraph p e l) (hpoint : member point v)
    (hu : UltrafilterOn p u) (hb : Concentrates p l u point b)
    (hc : Concentrates p l u point c) : b = c := by
  obtain ⟨f,hf,hcoord⟩ := coordinate_function h he hl hpoint
  obtain ⟨s,hsu,hs⟩ := hb
  obtain ⟨t,htu,ht⟩ := hc
  exact selected_fiber_value_unique h hu hf hsu htu
    (fun j => (hs j).trans (and_congr Iff.rfl (hcoord j b).symm))
    (fun j => (ht j).trans (and_congr Iff.rfl (hcoord j c).symm))

/-- All selected values are assembled into a single internally existing graph
by a first-order Separation instance on the internal product V times A. -/
theorem concentrated_assignment (h : AxiomSemantics M) {k p e v a l u : M}
    (he : FunctionSpace e v a) (hl : FunctionGraph p e l)
    (hu : UltrafilterOn p u) (hc : CompleteOn k p u) (ha : Small k a) :
    ∃ g : M, FunctionGraph v a g ∧
      ∀ point value : M, PairMember point value g → Concentrates p l u point value := by
  let φ : language.Formula (Option (Option (Fin 3))) :=
    concentratesF (some (some 0)) (some (some 1)) (some (some 2)) none (some none)
  obtain ⟨g,b,hb,hgb,hg⟩ := relationSet_exists h φ ![p,l,u] v a
  have hg' : ∀ point value : M, PairMember point value g ↔
      member point v ∧ member value a ∧ Concentrates p l u point value := by
    intro point value
    simpa [φ,assign] using hg point value
  refine ⟨g,⟨⟨b,hb,hgb⟩,?_⟩,fun point value hv => ((hg' point value).mp hv).2.2⟩
  intro point hpoint
  obtain ⟨value,hva,hconc⟩ := concentration_exists h he hl hpoint hu hc ha
  refine ⟨value,(hg' point value).mpr ⟨hpoint,hva,hconc⟩,?_⟩
  intro value' hv'
  exact concentration_unique h he hl hpoint hu ((hg' point value').mp hv').2.2 hconc


def ChosenFiber (s p l g point : M) : Prop :=
  ∃ value : M, PairMember point value g ∧ EvalFiber s p l point value

def chosenFiberF {α : Type v} (s p l g point : α) : language.Formula α :=
  exF (pairMemF (some point) none (some g) ⊓
    evalFiberF (some s) (some p) (some l) (some point) none)

@[simp]
theorem chosenFiberF_realize {α : Type v} (s p l g point : α) (e : α → M) :
    (chosenFiberF s p l g point).Realize e ↔ ChosenFiber (e s) (e p) (e l) (e g) (e point) := by
  simp [chosenFiberF,ChosenFiber,assign]

/-- Agreement on an entire internally small scope is large in the ultrafilter.
The family of coordinate agreement sets is a Replacement image of the scope,
proved internally small before invoking completeness. -/
theorem agreement_set (h : AxiomSemantics M) {k p e v a l u g scope : M}
    (he : FunctionSpace e v a) (hl : FunctionGraph p e l) (hg : FunctionGraph v a g)
    (hconc : ∀ point value : M, PairMember point value g → Concentrates p l u point value)
    (hc : CompleteOn k p u) (hscope : subset scope v) (hsmall : Small k scope) :
    ∃ r : M, member r u ∧ subset r p ∧
      ∀ j b : M, member j r → PairMember j b l → AgreeOn scope b g := by
  have hchosen : ∀ point : M, member point scope → ∃! s : M, ChosenFiber s p l g point := by
    intro point hps
    obtain ⟨value,hgv,_⟩ := hg.2 point (hscope point hps)
    obtain ⟨s,_,hs⟩ := hconc point value hgv
    refine ⟨s,⟨value,hgv,hs⟩,?_⟩
    rintro t ⟨value',hgv',ht⟩
    have hval : value' = value := functionGraph_value_unique hg hgv' hgv
    subst value'
    exact h.extensionality t s (fun j => (ht j).trans (hs j).symm)
  let φ : language.Formula (Option (Option (Fin 3))) :=
    chosenFiberF (some none) (some (some 0)) (some (some 1)) (some (some 2)) none
  have hfun : ∀ point : M, member point scope →
      ∃! s : M, φ.Realize (assign (assign ![p,l,g] s) point) := by
    intro point hp
    simpa [φ,assign] using hchosen point hp
  obtain ⟨family,f,hf,hgraph,hfamily⟩ := definable_image_function h φ ![p,l,g] scope hfun
  have hgraph' : ∀ point s : M, PairMember point s f ↔
      member point scope ∧ ChosenFiber s p l g point := by
    intro point s
    simpa [φ,assign] using hgraph point s
  have hfamily' : ∀ s : M, member s family ↔
      ∃ point : M, member point scope ∧ ChosenFiber s p l g point := by
    intro s
    simpa [φ,assign] using hfamily s
  have hsurj : ∀ s : M, member s family →
      ∃ point : M, member point scope ∧ PairMember point s f := by
    intro s hs
    obtain ⟨point,hps,hchosen⟩ := (hfamily' s).mp hs
    exact ⟨point,hps,(hgraph' point s).mpr ⟨hps,hchosen⟩⟩
  have hfsmall : Small k family := small_of_surjection h hf hsmall hsurj
  have hfu : subset family u := by
    intro s hs
    obtain ⟨point,_,value,hgv,hfiber⟩ := (hfamily' s).mp hs
    obtain ⟨t,htu,ht⟩ := hconc point value hgv
    have hst : s = t := h.extensionality s t (fun j => (hfiber j).trans (ht j).symm)
    exact hst.symm ▸ htu
  obtain ⟨r,hr,hru⟩ := hc family hfu hfsmall
  refine ⟨r,hru,fun j hj => ((hr j).mp hj).1,?_⟩
  intro j b hjr hjb point hpoint value'
  have hb : FunctionGraph v a b := (he b).mp (functionGraph_pair_bounds hl hjb).2
  obtain ⟨value,hgv,_⟩ := hg.2 point (hscope point hpoint)
  obtain ⟨s,_,hs⟩ := hconc point value hgv
  have hsfamily : member s family := (hfamily' s).mpr ⟨point,hpoint,value,hgv,hs⟩
  have hjs : member j s := ((hr j).mp hjr).2 s hsfamily
  obtain ⟨b',hjb',hb'v⟩ := ((hs j).mp hjs).2
  have hbb : b' = b := functionGraph_value_unique hl hjb' hjb
  subst b'
  constructor
  · intro hbv'
    have hvalue : value' = value := functionGraph_value_unique hb hbv' hb'v
    subst value'
    exact hgv
  · intro hgv'
    have hvalue : value' = value := functionGraph_value_unique hg hgv' hgv
    subst value'
    exact hb'v

/-- Each cone is an actual internal large set, with the exact incidence condition. -/
def FineOn (p i u : M) : Prop :=
  ∀ constraint : M, member constraint i → ∃ cone : M, member cone u ∧
    ∀ j : M, member j cone ↔ member j p ∧ member constraint j

def HasFineComplete (k i : M) : Prop :=
  ∃ p u : M, SmallPiecesSet p k i ∧ UltrafilterOn p u ∧ CompleteOn k p u ∧ FineOn p i u

def InternalFinePrinciple (k : M) : Prop := ∀ i : M, HasFineComplete k i

/-- The full fixed-domain compactness argument, now internal to an arbitrary model.
No external family is passed to internal completeness, and the final graph belongs to M. -/
theorem compactness_of_internal_fine (h : AxiomSemantics M) {k i v a c scopes : M}
    (hadm : Admissible k i v a c scopes) (hfine : HasFineComplete k i)
    (hlocal : LocalSat k i v a c) : GlobalSat i v a c := by
  classical
  obtain ⟨ha,_,⟨pv,hpv,hscopes⟩,hsmallscope,hlocality⟩ := hadm
  obtain ⟨p,u,hp,hu,hc,hfine⟩ := hfine
  obtain ⟨p',e,l,hp',he,hl,hsolutions⟩ := localAssignmentSelector h hlocal
  have hpp : p' = p := smallPiecesSet_unique h hp' hp
  subst p'
  obtain ⟨g,hg,hconc⟩ := concentrated_assignment h he hl hu hc ha
  refine ⟨g,hg,?_⟩
  intro constraint hci
  obtain ⟨scope,hcs,_⟩ := hscopes.2 constraint hci
  have hsv : subset scope v := (hpv scope).mp (functionGraph_pair_bounds hscopes hcs).2
  have hssmall : Small k scope := hsmallscope constraint scope hcs
  obtain ⟨r,hru,hrp,hagree⟩ := agreement_set h he hl hg hconc hc hsv hssmall
  obtain ⟨cone,hconeu,hcone⟩ := hfine constraint hci
  obtain ⟨both,hboth,hbothu⟩ := hu.1.2.2.2 r cone hru hconeu
  have hnonempty : ∃ j : M, member j both := by
    by_contra hn
    have he : IsEmpty both := fun j hj => hn ⟨j,hj⟩
    exact (ultrafilter_proper h hu).2 both he hbothu
  obtain ⟨j,hj⟩ := hnonempty
  have hjr : member j r := ((hboth j).mp hj).1
  have hconstraint : member constraint j := ((hcone j).mp ((hboth j).mp hj).2).2
  obtain ⟨b,hjb,_⟩ := hl.2 j (hrp j hjr)
  obtain ⟨hb,hbsat⟩ := hsolutions j b hjb
  exact (hlocality constraint scope b g hcs hb hg (hagree j b hjr hjb)).mp
    (hbsat constraint hconstraint)

theorem internal_fine_implies_compactness (h : AxiomSemantics M) (k : M)
    (hfine : InternalFinePrinciple k) : ConstraintCompactness k := by
  intro i v a c scopes hadm hlocal
  exact compactness_of_internal_fine h hadm (hfine i) hlocal

theorem internal_fine_implies_reflection (h : AxiomSemantics M) (k : M)
    (hfine : InternalFinePrinciple k) : ConstraintReflection k :=
  (compactness_iff_reflection k).mp (internal_fine_implies_compactness h k hfine)

/-- The principal arbitrary-model theorem takes the encoded ZFC theory, not an
augmented axiom package containing compactness, as its base hypothesis. -/
theorem model_zfc_internal_compactness (hM : M ⊨ zfcTheory) (k : M)
    (hfine : InternalFinePrinciple k) : ConstraintCompactness k :=
  internal_fine_implies_compactness (model_zfc_iff_axiomSemantics.mp hM) k hfine

theorem model_zfc_internal_reflection (hM : M ⊨ zfcTheory) (k : M)
    (hfine : InternalFinePrinciple k) : ConstraintReflection k :=
  internal_fine_implies_reflection (model_zfc_iff_axiomSemantics.mp hM) k hfine

end Komorebi.InternalFineCompactness
