import Komorebi.Foundation.InternalFunctionSpaces

/-!
# Internal selection from a bounded total relation

The fiber family, its choice graph and the selected graph all belong to M.
The proof derives their existence from the already encoded ZFC axioms.
It does not identify internally represented maps with arbitrary external functions.
-/

universe u v

namespace Komorebi.InternalSelection

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces

variable {M : Type u} [language.Structure M]

def Fiber (s i a r : M) : Prop :=
  ∀ b : M, member b s ↔ member b a ∧ PairMember i b r

def fiberF {α : Type v} (s i a r : α) : language.Formula α :=
  allF ((memF none (some s)).iff
    (memF none (some a) ⊓ pairMemF (some i) none (some r)))

@[simp]
theorem fiberF_realize {α : Type v} (s i a r : α) (e : α → M) :
    (fiberF s i a r).Realize e ↔ Fiber (e s) (e i) (e a) (e r) := by
  simp [fiberF,Fiber,assign]

theorem fiber_subset {s i a r : M} (hs : Fiber s i a r) : subset s a :=
  fun b hb => ((hs b).mp hb).1

theorem fiber_unique (h : AxiomSemantics M) {s t i a r : M}
    (hs : Fiber s i a r) (ht : Fiber t i a r) : s = t :=
  h.extensionality s t (fun b => (hs b).trans (ht b).symm)

theorem fiber_exists (h : AxiomSemantics M) (i a r : M) : ∃ s : M, Fiber s i a r := by
  let φ : language.Formula (Option (Fin 2)) := pairMemF (some 0) none (some 1)
  obtain ⟨s,hs⟩ := h.separation 2 φ ![i,r] a
  refine ⟨s,?_⟩
  intro b
  simpa [φ,assign] using hs b

def fiberFamilyF {α : Type v} (f i a r : α) : language.Formula α :=
  exF (memF none (some i) ⊓ fiberF (some f) none (some a) (some r))

@[simp]
theorem fiberFamilyF_realize {α : Type v} (f i a r : α) (e : α → M) :
    (fiberFamilyF f i a r).Realize e ↔
      ∃ j : M, member j (e i) ∧ Fiber (e f) j (e a) (e r) := by
  simp [fiberFamilyF,assign]

/-- The set of all indexed fibers is obtained by separating the internal powerset. -/
theorem fiberFamily_exists (h : AxiomSemantics M) (i a r : M) :
    ∃ f : M, ∀ s : M, member s f ↔ ∃ j : M, member j i ∧ Fiber s j a r := by
  obtain ⟨pa,hpa⟩ := h.powerset a
  let φ : language.Formula (Option (Fin 3)) :=
    fiberFamilyF none (some 0) (some 1) (some 2)
  obtain ⟨f,hf⟩ := h.separation 3 φ ![i,a,r] pa
  refine ⟨f,?_⟩
  intro s
  have hf' : member s f ↔ member s pa ∧ ∃ j : M, member j i ∧ Fiber s j a r := by
    simpa [φ,assign] using hf s
  refine hf'.trans ?_
  constructor
  · exact fun hs => hs.2
  · rintro ⟨j,hj,hs⟩
    exact ⟨(hpa s).mpr (fiber_subset hs),j,hj,hs⟩

theorem choiceGraph_pair_bounds {f g s a : M} (hg : IsChoiceGraph f g)
    (hsa : PairMember s a g) : member s f ∧ member a s := by
  obtain ⟨p,hp,hpg⟩ := hsa
  obtain ⟨t,ht,b,hb,htb⟩ := hg.1 p hpg
  obtain ⟨rfl,rfl⟩ := orderedPair_injective hp htb
  exact ⟨ht,hb⟩

def selectedF {α : Type v} (i a domain relation choice : α) : language.Formula α :=
  exF (fiberF none (some i) (some domain) (some relation) ⊓
    pairMemF none (some a) (some choice))

@[simp]
theorem selectedF_realize {α : Type v} (i a domain relation choice : α) (e : α → M) :
    (selectedF i a domain relation choice).Realize e ↔
      ∃ s : M, Fiber s (e i) (e domain) (e relation) ∧ PairMember s (e a) (e choice) := by
  simp [selectedF,assign]

/-- Bounded internal uniformization. The selected function is itself a set in M.
All set-existence obligations are discharged from AxiomSemantics, not postulated. -/
theorem internal_selection (h : AxiomSemantics M) (i a r : M)
    (htotal : ∀ j : M, member j i → ∃ b : M, member b a ∧ PairMember j b r) :
    ∃ g : M, FunctionGraph i a g ∧
      ∀ j b : M, PairMember j b g → PairMember j b r := by
  obtain ⟨f,hf⟩ := fiberFamily_exists h i a r
  have hnonempty : ∀ s : M, member s f → ∃ b : M, member b s := by
    intro s hs
    obtain ⟨j,hj,hs⟩ := (hf s).mp hs
    obtain ⟨b,hb,hr⟩ := htotal j hj
    exact ⟨b,(hs b).mpr ⟨hb,hr⟩⟩
  obtain ⟨choice,hchoice⟩ := h.choice f hnonempty
  let φ : language.Formula (Option (Option (Fin 3))) :=
    selectedF none (some none) (some (some 0)) (some (some 1)) (some (some 2))
  obtain ⟨g,p,hp,hgp,hg⟩ := relationSet_exists h φ ![a,r,choice] i a
  have hg' : ∀ j b : M, PairMember j b g ↔ member j i ∧ member b a ∧
      ∃ s : M, Fiber s j a r ∧ PairMember s b choice := by
    intro j b
    simpa [φ,assign] using hg j b
  refine ⟨g,⟨⟨p,hp,hgp⟩,?_⟩,?_⟩
  · intro j hj
    obtain ⟨s,hs⟩ := fiber_exists h j a r
    have hsf : member s f := (hf s).mpr ⟨j,hj,hs⟩
    obtain ⟨b,hbs,hsb,hunique⟩ := hchoice.2 s hsf
    have hba : member b a := ((hs b).mp hbs).1
    refine ⟨b,(hg' j b).mpr ⟨hj,hba,s,hs,hsb⟩,?_⟩
    intro c hjc
    obtain ⟨_,_,t,ht,htc⟩ := (hg' j c).mp hjc
    have hts : t = s := fiber_unique h ht hs
    subst t
    exact hunique c htc
  · intro j b hjb
    obtain ⟨_,_,s,hs,hsb⟩ := (hg' j b).mp hjb
    exact ((hs b).mp (choiceGraph_pair_bounds hchoice hsb).2).2

/-- This theorem takes actual modelhood of the encoded ZFC theory as its premise. -/
theorem model_zfc_internal_selection (hM : M ⊨ zfcTheory) (i a r : M)
    (htotal : ∀ j : M, member j i → ∃ b : M, member b a ∧ PairMember j b r) :
    ∃ g : M, FunctionGraph i a g ∧
      ∀ j b : M, PairMember j b g → PairMember j b r :=
  internal_selection (model_zfc_iff_axiomSemantics.mp hM) i a r htotal

/-- Restricting an internally coded function yields an internally coded function. -/
theorem restriction_exists (h : AxiomSemantics M) {x y g : M}
    (hg : FunctionGraph x y g) (s : M) (hs : subset s x) :
    ∃ t : M, FunctionGraph s y t ∧
      ∀ a b : M, PairMember a b t ↔ member a s ∧ PairMember a b g := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    pairMemF none (some none) (some (some 0))
  obtain ⟨t,p,hp,htp,ht⟩ := relationSet_exists h φ ![g] s y
  have ht' : ∀ a b : M, PairMember a b t ↔ member a s ∧ PairMember a b g := by
    intro a b
    have ht'' : PairMember a b t ↔ member a s ∧ member b y ∧ PairMember a b g := by
      simpa [φ,assign] using ht a b
    refine ht''.trans ?_
    constructor
    · exact fun h => ⟨h.1,h.2.2⟩
    · exact fun h => ⟨h.1,(functionGraph_pair_bounds hg h.2).2,h.2⟩
  refine ⟨t,⟨⟨p,hp,htp⟩,?_⟩,ht'⟩
  intro a ha
  obtain ⟨b,hab,hunique⟩ := hg.2 a (hs a ha)
  exact ⟨b,(ht' a b).mpr ⟨ha,hab⟩,fun c hc => hunique c ((ht' a c).mp hc).2⟩

end Komorebi.InternalSelection
