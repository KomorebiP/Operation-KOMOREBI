import Komorebi.Foundation.InternalSelection

/-!
# Internally coded constraint systems and local assignment selectors

Constraints are an internal relation table, not an arbitrary external predicate.
Assignments, scopes, small subfamilies, solution sets and selectors are all set
codes in M. The complete compactness/filter comparison is not assumed here.
-/

universe u v

namespace Komorebi.InternalConstraints

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalSelection

variable {M : Type u} [language.Structure M]

/-- Satisfaction is membership of a pair in a set-coded constraint table. -/
def Satisfies (c j g : M) : Prop := ∀ i : M, member i j → PairMember i g c

/-- Agreement is pointwise agreement of the two internal function graphs. -/
def AgreeOn (s g h : M) : Prop :=
  ∀ x : M, member x s → ∀ y : M, PairMember x y g ↔ PairMember x y h

def SmallPiecesSet (p k i : M) : Prop :=
  ∀ j : M, member j p ↔ subset j i ∧ Small k j

def SolutionSet (s v a c j : M) : Prop :=
  ∀ g : M, member g s ↔ FunctionGraph v a g ∧ Satisfies c j g

def GlobalSat (i v a c : M) : Prop := ∃ g : M, FunctionGraph v a g ∧ Satisfies c i g

def LocalSat (k i v a c : M) : Prop :=
  ∀ j : M, subset j i → Small k j → GlobalSat j v a c

/-- Every constraint-table entry consists of a constraint and a valid assignment. -/
def ConstraintRelation (i v a c : M) : Prop :=
  ∃ e p : M, FunctionSpace e v a ∧ Product p i e ∧ subset c p

/-- A total internal function assigns each constraint its subset of variables. -/
def ScopeAssignment (i v scopes : M) : Prop :=
  ∃ pv : M, IsPower pv v ∧ FunctionGraph i pv scopes

/-- The specified class fixes all representation, domain and scope requirements.
It contains no compactness or global-selection conclusion. -/
def Admissible (k i v a c scopes : M) : Prop :=
  Small k a ∧ ConstraintRelation i v a c ∧ ScopeAssignment i v scopes ∧
  (∀ j s : M, PairMember j s scopes → Small k s) ∧
  ∀ j s g h : M, PairMember j s scopes → FunctionGraph v a g → FunctionGraph v a h →
    AgreeOn s g h → (PairMember j g c ↔ PairMember j h c)

/-- A proposed internal principle, defined only. It is not an assumption of the
set-construction or selector theorems in this file. -/
def ConstraintCompactness (k : M) : Prop :=
  ∀ i v a c scopes : M, Admissible k i v a c scopes →
    LocalSat k i v a c → GlobalSat i v a c

def ConstraintReflection (k : M) : Prop :=
  ∀ i v a c scopes : M, Admissible k i v a c scopes →
    ¬ GlobalSat i v a c → ∃ j : M, subset j i ∧ Small k j ∧ ¬ GlobalSat j v a c

def satisfiesF {α : Type v} (c j g : α) : language.Formula α :=
  allF ((memF none (some j)).imp (pairMemF none (some g) (some c)))

@[simp]
theorem satisfiesF_realize {α : Type v} (c j g : α) (e : α → M) :
    (satisfiesF c j g).Realize e ↔ Satisfies (e c) (e j) (e g) := by
  simp [satisfiesF,Satisfies,assign]

def functionSpaceF {α : Type v} (e v a : α) : language.Formula α :=
  allF ((memF none (some e)).iff (funcF (some v) (some a) none))

@[simp]
theorem functionSpaceF_realize {α : Type v} (e v a : α) (b : α → M) :
    (functionSpaceF e v a).Realize b ↔ FunctionSpace (b e) (b v) (b a) := by
  simp [functionSpaceF,FunctionSpace,assign]

def agreeOnF {α : Type v} (s g h : α) : language.Formula α :=
  allF ((memF none (some s)).imp
    (allF ((pairMemF (some none) none (some (some g))).iff
      (pairMemF (some none) none (some (some h))))))

@[simp]
theorem agreeOnF_realize {α : Type v} (s g h : α) (e : α → M) :
    (agreeOnF s g h).Realize e ↔ AgreeOn (e s) (e g) (e h) := by
  simp [agreeOnF,AgreeOn,assign]

theorem smallPiecesSet_exists (h : AxiomSemantics M) (k i : M) :
    ∃ p : M, SmallPiecesSet p k i := by
  obtain ⟨pi,hpi⟩ := h.powerset i
  let φ : language.Formula (Option (Fin 1)) := smallF (some 0) none
  obtain ⟨p,hp⟩ := h.separation 1 φ ![k] pi
  refine ⟨p,?_⟩
  intro j
  have hp' : member j p ↔ member j pi ∧ Small k j := by
    simpa [φ,assign] using hp j
  exact hp'.trans (and_congr (hpi j) Iff.rfl)

theorem smallPiecesSet_unique (h : AxiomSemantics M) {p q k i : M}
    (hp : SmallPiecesSet p k i) (hq : SmallPiecesSet q k i) : p = q :=
  h.extensionality p q (fun j => (hp j).trans (hq j).symm)

theorem solutionSet_exists (h : AxiomSemantics M) (v a c j : M) :
    ∃ s : M, SolutionSet s v a c j := by
  obtain ⟨e,he⟩ := functionSpace_exists h v a
  let φ : language.Formula (Option (Fin 2)) := satisfiesF (some 0) (some 1) none
  obtain ⟨s,hs⟩ := h.separation 2 φ ![c,j] e
  refine ⟨s,?_⟩
  intro g
  have hs' : member g s ↔ member g e ∧ Satisfies c j g := by
    simpa [φ,assign] using hs g
  exact hs'.trans (and_congr (he g) Iff.rfl)

theorem solutionSet_unique (h : AxiomSemantics M) {s t v a c j : M}
    (hs : SolutionSet s v a c j) (ht : SolutionSet t v a c j) : s = t :=
  h.extensionality s t (fun g => (hs g).trans (ht g).symm)

theorem solutionSet_empty_iff {s v a c j : M} (hs : SolutionSet s v a c j) :
    IsEmpty s ↔ ¬ GlobalSat j v a c := by
  constructor
  · intro he hg
    obtain ⟨g,hg⟩ := hg
    exact he g ((hs g).mpr hg)
  · intro he g hg
    exact he ⟨g,(hs g).mp hg⟩

theorem solutionRelation_exists (h : AxiomSemantics M) (p e c : M) :
    ∃ r b : M, Product b p e ∧ subset r b ∧
      ∀ j g : M, PairMember j g r ↔ member j p ∧ member g e ∧ Satisfies c j g := by
  let φ : language.Formula (Option (Option (Fin 1))) :=
    satisfiesF (some (some 0)) none (some none)
  obtain ⟨r,b,hb,hr,hrel⟩ := relationSet_exists h φ ![c] p e
  refine ⟨r,b,hb,hr,?_⟩
  intro j g
  simpa [φ,assign] using hrel j g

/-- This closes the local-assignment collection step in arbitrary ZFC models.
The selector g is internal. No compactness or large-cardinal input is used. -/
theorem localAssignmentSelector (h : AxiomSemantics M) {k i v a c : M}
    (hlocal : LocalSat k i v a c) :
    ∃ p e g : M, SmallPiecesSet p k i ∧ FunctionSpace e v a ∧ FunctionGraph p e g ∧
      ∀ j b : M, PairMember j b g → FunctionGraph v a b ∧ Satisfies c j b := by
  obtain ⟨p,hp⟩ := smallPiecesSet_exists h k i
  obtain ⟨e,he⟩ := functionSpace_exists h v a
  obtain ⟨r,_,_,_,hr⟩ := solutionRelation_exists h p e c
  have htotal : ∀ j : M, member j p → ∃ b : M, member b e ∧ PairMember j b r := by
    intro j hj
    obtain ⟨hjI,hjSmall⟩ := (hp j).mp hj
    obtain ⟨b,hb,hbs⟩ := hlocal j hjI hjSmall
    have hbe : member b e := (he b).mpr hb
    exact ⟨b,hbe,(hr j b).mpr ⟨hj,hbe,hbs⟩⟩
  obtain ⟨g,hg,hgr⟩ := internal_selection h p e r htotal
  refine ⟨p,e,g,hp,he,hg,?_⟩
  intro j b hjb
  have hrel := (hr j b).mp (hgr j b hjb)
  exact ⟨(he b).mp hrel.2.1,hrel.2.2⟩

theorem model_zfc_localAssignmentSelector (hM : M ⊨ zfcTheory) {k i v a c : M}
    (hlocal : LocalSat k i v a c) :
    ∃ p e g : M, SmallPiecesSet p k i ∧ FunctionSpace e v a ∧ FunctionGraph p e g ∧
      ∀ j b : M, PairMember j b g → FunctionGraph v a b ∧ Satisfies c j b :=
  localAssignmentSelector (model_zfc_iff_axiomSemantics.mp hM) hlocal

/-- Solution selection implies local satisfiability. This is not global compactness. -/
theorem localSat_iff_internalSelector (h : AxiomSemantics M) (k i v a c : M) :
    LocalSat k i v a c ↔
      ∃ p e g : M, SmallPiecesSet p k i ∧ FunctionSpace e v a ∧ FunctionGraph p e g ∧
        ∀ j b : M, PairMember j b g → FunctionGraph v a b ∧ Satisfies c j b := by
  constructor
  · exact localAssignmentSelector h
  · rintro ⟨p,e,g,hp,_,hg,hsol⟩ j hj hsmall
    obtain ⟨b,hjb,_⟩ := hg.2 j ((hp j).mpr ⟨hj,hsmall⟩)
    exact ⟨b,hsol j b hjb⟩

theorem satisfies_subset {c i j g : M} (hg : Satisfies c i g) (hj : subset j i) :
    Satisfies c j g := fun x hx => hg x (hj x hx)

/-- An unsatisfiable internally coded subsystem is a sound obstruction. -/
theorem obstruction_sound {i v a c j : M} (hj : subset j i)
    (hbad : ¬ GlobalSat j v a c) : ¬ GlobalSat i v a c := by
  rintro ⟨g,hg,hgs⟩
  exact hbad ⟨g,hg,satisfies_subset hgs hj⟩

/-- Contraposition for the fixed internal encoding; no filter comparison is asserted. -/
theorem compactness_iff_reflection (k : M) :
    ConstraintCompactness k ↔ ConstraintReflection k := by
  classical
  constructor
  · intro hc i v a c scopes ha hbad
    by_contra hn
    have hlocal : LocalSat k i v a c := by
      intro j hj hsmall
      by_contra hunsat
      exact hn ⟨j,hj,hsmall,hunsat⟩
    exact hbad (hc i v a c scopes ha hlocal)
  · intro hr i v a c scopes ha hlocal
    by_contra hbad
    obtain ⟨j,hj,hsmall,hunsat⟩ := hr i v a c scopes ha hbad
    exact hunsat (hlocal j hj hsmall)

end Komorebi.InternalConstraints
