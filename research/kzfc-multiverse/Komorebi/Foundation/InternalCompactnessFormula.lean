import Komorebi.Foundation.InternalFineCompactness

/-!
# Membership-language syntax for the internal compactness implication

All abbreviations expand in the same one-relation first-order language.
The final sentence is proved true in every model of the encoded ZFC theory.
This is a semantic consequence theorem, not extraction into a separate proof calculus.
-/

universe u v

namespace Komorebi.InternalCompactnessFormula

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces InternalConstraints
open InternalFineCompactness

variable {M : Type u} [language.Structure M]

def globalSatF {α : Type v} (i v a c : α) : language.Formula α :=
  exF (funcF (some v) (some a) none ⊓ satisfiesF (some c) (some i) none)

@[simp]
theorem globalSatF_realize {α : Type v} (i v a c : α) (e : α → M) :
    (globalSatF i v a c).Realize e ↔ GlobalSat (e i) (e v) (e a) (e c) := by
  simp [globalSatF,GlobalSat,assign]

def localSatF {α : Type v} (k i v a c : α) : language.Formula α :=
  allF ((subsetF none (some i)).imp ((smallF (some k) none).imp
    (globalSatF none (some v) (some a) (some c))))

@[simp]
theorem localSatF_realize {α : Type v} (k i v a c : α) (e : α → M) :
    (localSatF k i v a c).Realize e ↔ LocalSat (e k) (e i) (e v) (e a) (e c) := by
  simp [localSatF,LocalSat,assign]

def constraintRelationF {α : Type v} (i v a c : α) : language.Formula α :=
  exF (let i := some i; let v := some v; let a := some a; let c := some c; let e := none
    exF (functionSpaceF (some e) (some v) (some a) ⊓
      (prodF none (some i) (some e) ⊓ subsetF (some c) none)))

@[simp]
theorem constraintRelationF_realize {α : Type v} (i v a c : α) (e : α → M) :
    (constraintRelationF i v a c).Realize e ↔ ConstraintRelation (e i) (e v) (e a) (e c) := by
  simp [constraintRelationF,ConstraintRelation,assign]

def scopeAssignmentF {α : Type v} (i v scopes : α) : language.Formula α :=
  exF (powerF none (some v) ⊓ funcF (some i) none (some scopes))

@[simp]
theorem scopeAssignmentF_realize {α : Type v} (i v scopes : α) (e : α → M) :
    (scopeAssignmentF i v scopes).Realize e ↔ ScopeAssignment (e i) (e v) (e scopes) := by
  simp [scopeAssignmentF,ScopeAssignment,assign]

def smallScopesF {α : Type v} (k scopes : α) : language.Formula α :=
  allF (allF ((pairMemF (some none) none (some (some scopes))).imp
    (smallF (some (some k)) none)))

@[simp]
theorem smallScopesF_realize {α : Type v} (k scopes : α) (e : α → M) :
    (smallScopesF k scopes).Realize e ↔
      ∀ j s : M, PairMember j s (e scopes) → Small (e k) s := by
  simp [smallScopesF,assign]

def localityF {α : Type v} (v a c scopes : α) : language.Formula α :=
  allF (let v := some v; let a := some a; let c := some c; let scopes := some scopes; let j := none
    allF (let v := some v; let a := some a; let c := some c; let scopes := some scopes
      let j := some j; let s := none
      allF (let v := some v; let a := some a; let c := some c; let scopes := some scopes
        let j := some j; let s := some s; let g := none
        allF ((pairMemF (some j) (some s) (some scopes)).imp
          ((funcF (some v) (some a) (some g)).imp ((funcF (some v) (some a) none).imp
            ((agreeOnF (some s) (some g) none).imp
              ((pairMemF (some j) (some g) (some c)).iff (pairMemF (some j) none (some c))))))))))

@[simp]
theorem localityF_realize {α : Type v} (v a c scopes : α) (e : α → M) :
    (localityF v a c scopes).Realize e ↔
      ∀ j s g h : M, PairMember j s (e scopes) → FunctionGraph (e v) (e a) g →
        FunctionGraph (e v) (e a) h → AgreeOn s g h →
          (PairMember j g (e c) ↔ PairMember j h (e c)) := by
  simp [localityF,assign]

def admissibleF {α : Type v} (k i v a c scopes : α) : language.Formula α :=
  smallF k a ⊓ (constraintRelationF i v a c ⊓ (scopeAssignmentF i v scopes ⊓
    (smallScopesF k scopes ⊓ localityF v a c scopes)))

@[simp]
theorem admissibleF_realize {α : Type v} (k i v a c scopes : α) (e : α → M) :
    (admissibleF k i v a c scopes).Realize e ↔ Admissible (e k) (e i) (e v) (e a) (e c) (e scopes) := by
  simp [admissibleF,Admissible]

def constraintCompactnessF {α : Type v} (k : α) : language.Formula α :=
  allF (let k := some k; let i := none
    allF (let k := some k; let i := some i; let v := none
      allF (let k := some k; let i := some i; let v := some v; let a := none
        allF (let k := some k; let i := some i; let v := some v; let a := some a; let c := none
          allF ((admissibleF (some k) (some i) (some v) (some a) (some c) none).imp
            ((localSatF (some k) (some i) (some v) (some a) (some c)).imp
              (globalSatF (some i) (some v) (some a) (some c))))))))

@[simp]
theorem constraintCompactnessF_realize {α : Type v} (k : α) (e : α → M) :
    (constraintCompactnessF k).Realize e ↔ ConstraintCompactness (e k) := by
  simp [constraintCompactnessF,ConstraintCompactness,assign]

def smallPiecesSetF {α : Type v} (p k i : α) : language.Formula α :=
  allF ((memF none (some p)).iff (subsetF none (some i) ⊓ smallF (some k) none))

@[simp]
theorem smallPiecesSetF_realize {α : Type v} (p k i : α) (e : α → M) :
    (smallPiecesSetF p k i).Realize e ↔ SmallPiecesSet (e p) (e k) (e i) := by
  simp [smallPiecesSetF,SmallPiecesSet,assign]

def fineOnF {α : Type v} (p i u : α) : language.Formula α :=
  allF (let p := some p; let i := some i; let u := some u; let c := none
    (memF c i).imp (exF (let p := some p; let u := some u; let c := some c; let cone := none
      memF cone u ⊓ allF ((memF none (some cone)).iff
        (memF none (some p) ⊓ memF (some c) none)))))

@[simp]
theorem fineOnF_realize {α : Type v} (p i u : α) (e : α → M) :
    (fineOnF p i u).Realize e ↔ FineOn (e p) (e i) (e u) := by
  simp [fineOnF,FineOn,assign]

def hasFineCompleteF {α : Type v} (k i : α) : language.Formula α :=
  exF (let k := some k; let i := some i; let p := none
    exF (smallPiecesSetF (some p) (some k) (some i) ⊓
      (ultraF (some p) none ⊓ (completeF (some k) (some p) none ⊓ fineOnF (some p) (some i) none))))

@[simp]
theorem hasFineCompleteF_realize {α : Type v} (k i : α) (e : α → M) :
    (hasFineCompleteF k i).Realize e ↔ HasFineComplete (e k) (e i) := by
  simp [hasFineCompleteF,HasFineComplete,assign]

def internalFineF {α : Type v} (k : α) : language.Formula α :=
  allF (hasFineCompleteF (some k) none)

@[simp]
theorem internalFineF_realize {α : Type v} (k : α) (e : α → M) :
    (internalFineF k).Realize e ↔ InternalFinePrinciple (e k) := by
  simp [internalFineF,InternalFinePrinciple,assign]

/-- One closed sentence in the original membership-only language. -/
def fineCompactnessSentence : language.Sentence :=
  allF ((internalFineF none).imp (constraintCompactnessF none))

@[simp]
theorem fineCompactnessSentence_realize :
    M ⊨ fineCompactnessSentence ↔ ∀ k : M, InternalFinePrinciple k → ConstraintCompactness k := by
  simp [Sentence.Realize,fineCompactnessSentence,assign]

/-- A semantic consequence of the explicit ZFC theory, valid in every model.
This does not assert that any witness to the antecedent exists. -/
theorem model_zfc_fineCompactnessSentence (hM : M ⊨ zfcTheory) :
    M ⊨ fineCompactnessSentence := by
  rw [fineCompactnessSentence_realize]
  exact model_zfc_internal_compactness hM

end Komorebi.InternalCompactnessFormula
