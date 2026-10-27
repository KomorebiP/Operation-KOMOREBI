import Komorebi.Foundation.GeneralMembershipSemantics

/-!
# An explicit first-order ZFC theory in the existing membership language

Eight fixed sentences and the full Separation and Replacement schemas, with
arbitrarily many finite parameters. The image in Replacement is exact.
No schema quantifies over arbitrary semantic predicates in an arbitrary model.
-/

universe u v w

namespace Komorebi.ZFCAxiomSyntax

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics

variable {M : Type u} [language.Structure M]

/-- Replace a formula's distinguished variable and its parameters without capture. -/
def applyOne {α : Type v} {β : Type w} (φ : language.Formula (Option α))
    (x : β) (p : α → β) : language.Formula β :=
  φ.relabel (fun | none => x | some a => p a)

/-- Distinguished variables are x = none, y = some none. -/
def applyTwo {α : Type v} {β : Type w} (φ : language.Formula (Option (Option α)))
    (x y : β) (p : α → β) : language.Formula β :=
  φ.relabel (fun | none => x | some none => y | some (some a) => p a)

@[simp]
theorem applyOne_realize {α : Type v} {β : Type w} (φ : language.Formula (Option α))
    (x : β) (p : α → β) (e : β → M) :
    (applyOne φ x p).Realize e ↔ φ.Realize (assign (e ∘ p) (e x)) := by
  rw [applyOne, Formula.realize_relabel]
  apply Iff.of_eq
  congr 1
  funext a
  cases a <;> rfl

@[simp]
theorem applyTwo_realize {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (x y : β) (p : α → β) (e : β → M) :
    (applyTwo φ x y p).Realize e ↔ φ.Realize (assign (assign (e ∘ p) (e y)) (e x)) := by
  rw [applyTwo, Formula.realize_relabel]
  apply Iff.of_eq
  congr 1
  funext a
  cases a with
  | none => rfl
  | some a => cases a <;> rfl

/-- Universal closure of every explicitly indexed parameter, not just a sample. -/
def closeAll {n : ℕ} (φ : language.Formula (Fin n)) : language.Sentence :=
  (BoundedFormula.relabel (Sum.inr : Fin n → Empty ⊕ Fin n) φ).alls

@[simp]
theorem closeAll_realize {n : ℕ} (φ : language.Formula (Fin n)) :
    M ⊨ closeAll φ ↔ ∀ e : Fin n → M, φ.Realize e := by
  simp only [closeAll, Sentence.Realize, BoundedFormula.realize_alls]
  exact forall_congr' (fun _ => Formula.realize_relabel_sumInr φ)

def unionF {α : Type v} (r x : α) : language.Formula α :=
  allF ((memF none (some r)).iff
    (exF (memF none (some (some x)) ⊓ memF (some none) none)))

def powerF {α : Type v} (p x : α) : language.Formula α :=
  allF ((memF none (some p)).iff (subsetF none (some x)))

@[simp]
theorem unionF_realize {α : Type v} (r x : α) (e : α → M) :
    (unionF r x).Realize e ↔ IsUnion (e r) (e x) := by
  simp [unionF, IsUnion, assign]

@[simp]
theorem powerF_realize {α : Type v} (p x : α) (e : α → M) :
    (powerF p x).Realize e ↔ IsPower (e p) (e x) := by
  simp [powerF, IsPower, assign]

def IsSingleton (s x : M) : Prop := ∀ z, member z s ↔ z = x

def IsOrderedPair (p x y : M) : Prop :=
  ∃ a b, IsSingleton a x ∧ IsPair b x y ∧ IsPair p a b

def PairMember (x y g : M) : Prop := ∃ p, IsOrderedPair p x y ∧ member p g

@[simp]
theorem singletonF_realize {α : Type v} (s x : α) (e : α → M) :
    (singletonF s x).Realize e ↔ IsSingleton (e s) (e x) := by
  simp [singletonF, IsSingleton, assign]

@[simp]
theorem pairF_realize {α : Type v} (p x y : α) (e : α → M) :
    (pairF p x y).Realize e ↔ IsOrderedPair (e p) (e x) (e y) := by
  simp [pairF, IsOrderedPair, assign]

@[simp]
theorem pairMemF_realize {α : Type v} (x y g : α) (e : α → M) :
    (pairMemF x y g).Realize e ↔ PairMember (e x) (e y) (e g) := by
  simp [pairMemF, PairMember, assign]

/-- A genuine choice graph, including the absence of extra graph entries. -/
def IsChoiceGraph (x g : M) : Prop :=
  (∀ p, member p g → ∃ a, member a x ∧ ∃ b, member b a ∧ IsOrderedPair p a b) ∧
    ∀ a, member a x → ∃ b, member b a ∧ PairMember a b g ∧
      ∀ c, PairMember a c g → c = b

def choiceGraphF {α : Type v} (x g : α) : language.Formula α :=
  (allF ((memF none (some g)).imp
    (exF (memF none (some (some x)) ⊓
      exF (memF none (some none) ⊓ pairF (some (some none)) (some none) none))))) ⊓
  allF ((memF none (some x)).imp
    (exF (memF none (some none) ⊓
      (pairMemF (some none) none (some (some g)) ⊓
        allF ((pairMemF (some (some none)) none (some (some (some g)))).imp
          (eqF none (some none)))))))

@[simp]
theorem choiceGraphF_realize {α : Type v} (x g : α) (e : α → M) :
    (choiceGraphF x g).Realize e ↔ IsChoiceGraph (e x) (e g) := by
  simp [choiceGraphF, IsChoiceGraph, assign]

def extensionalitySentence : language.Sentence :=
  allF (allF ((allF ((memF none (some (some none))).iff
    (memF none (some none)))).imp (eqF (some none) none)))

def emptySentence : language.Sentence := exF (emptyF none)

def pairingSentence : language.Sentence :=
  allF (allF (exF (unorderedPairF none (some (some none)) (some none))))

def unionSentence : language.Sentence := allF (exF (unionF none (some none)))

def powersetSentence : language.Sentence := allF (exF (powerF none (some none)))

def infinitySentence : language.Sentence := exF (inductiveF none)

def foundationSentence : language.Sentence :=
  allF ((exF (memF none (some none))).imp
    (exF (memF none (some none) ⊓
      allF ((memF none (some (some none)) ⊓ memF none (some none)).not))))

def choiceSentence : language.Sentence :=
  allF ((allF ((memF none (some none)).imp (exF (memF none (some none))))).imp
    (exF (choiceGraphF (some none) none)))

def uniqueOutputF {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (x : β) (p : α → β) : language.Formula β :=
  exF (applyTwo φ (some x) none (some ∘ p) ⊓
    allF ((applyTwo φ (some (some x)) none (some ∘ some ∘ p)).imp (eqF none (some none))))

def functionalOnF {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (a : β) (p : α → β) : language.Formula β :=
  allF ((memF none (some a)).imp (uniqueOutputF φ none (some ∘ p)))

def imageF {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (a b : β) (p : α → β) : language.Formula β :=
  allF ((memF none (some b)).iff
    (exF (memF none (some (some a)) ⊓
      applyTwo φ none (some none) (some ∘ some ∘ p))))

def separationBody {n : ℕ} (φ : language.Formula (Option (Fin n))) :
    language.Formula (Fin n) :=
  allF (exF (allF ((memF none (some none)).iff
    (memF none (some (some none)) ⊓
      applyOne φ none (fun a => some (some (some a)))))))

def replacementBody {n : ℕ} (φ : language.Formula (Option (Option (Fin n)))) :
    language.Formula (Fin n) :=
  allF ((functionalOnF φ none some).imp
    (exF (imageF φ (some none) none (some ∘ some))))

def separationSentence {n : ℕ} (φ : language.Formula (Option (Fin n))) :
    language.Sentence := closeAll (separationBody φ)

def replacementSentence {n : ℕ}
    (φ : language.Formula (Option (Option (Fin n)))) : language.Sentence :=
  closeAll (replacementBody φ)

/-- Exact semantic form of a Separation instance, with internal witnesses. -/
def SeparationInstance {n : ℕ} (φ : language.Formula (Option (Fin n)))
    (e : Fin n → M) : Prop :=
  ∀ a : M, ∃ b : M, ∀ x : M,
    member x b ↔ member x a ∧ φ.Realize (assign e x)

/-- Exact functional Replacement, restricted to a given internal set a. -/
def ReplacementInstance {n : ℕ} (φ : language.Formula (Option (Option (Fin n))))
    (e : Fin n → M) : Prop :=
  ∀ a : M, (∀ x : M, member x a → ∃! y : M, φ.Realize (assign (assign e y) x)) →
    ∃ b : M, ∀ y : M, member y b ↔
      ∃ x : M, member x a ∧ φ.Realize (assign (assign e y) x)

@[simp]
theorem uniqueOutputF_realize {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (x : β) (p : α → β) (e : β → M) :
    (uniqueOutputF φ x p).Realize e ↔
      ∃! y : M, φ.Realize (assign (assign (e ∘ p) y) (e x)) := by
  simp [uniqueOutputF, assign, Function.comp_def, ExistsUnique]

@[simp]
theorem functionalOnF_realize {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (a : β) (p : α → β) (e : β → M) :
    (functionalOnF φ a p).Realize e ↔
      ∀ x : M, member x (e a) → ∃! y : M,
        φ.Realize (assign (assign (e ∘ p) y) x) := by
  simp [functionalOnF, assign, Function.comp_def]

@[simp]
theorem imageF_realize {α : Type v} {β : Type w}
    (φ : language.Formula (Option (Option α))) (a b : β) (p : α → β) (e : β → M) :
    (imageF φ a b p).Realize e ↔
      ∀ y : M, member y (e b) ↔ ∃ x : M,
        member x (e a) ∧ φ.Realize (assign (assign (e ∘ p) y) x) := by
  simp [imageF, assign, Function.comp_def]

@[simp]
theorem separationBody_realize {n : ℕ} (φ : language.Formula (Option (Fin n)))
    (e : Fin n → M) :
    (separationBody φ).Realize e ↔ SeparationInstance φ e := by
  simp [separationBody, SeparationInstance, assign, Function.comp_def]

@[simp]
theorem replacementBody_realize {n : ℕ}
    (φ : language.Formula (Option (Option (Fin n)))) (e : Fin n → M) :
    (replacementBody φ).Realize e ↔ ReplacementInstance φ e := by
  simp [replacementBody, ReplacementInstance, assign, Function.comp_def]

@[simp]
theorem separationSentence_realize {n : ℕ} (φ : language.Formula (Option (Fin n))) :
    M ⊨ separationSentence φ ↔ ∀ e : Fin n → M, SeparationInstance φ e := by
  simp [separationSentence]

@[simp]
theorem replacementSentence_realize {n : ℕ}
    (φ : language.Formula (Option (Option (Fin n)))) :
    M ⊨ replacementSentence φ ↔ ∀ e : Fin n → M, ReplacementInstance φ e := by
  simp [replacementSentence]

/-- All schema indices are syntactic formulas with finitely many parameters. -/
inductive AxiomCode
  | extensionality | empty | pairing | union | powerset | infinity | foundation | choice
  | separation (n : ℕ) (φ : language.Formula (Option (Fin n)))
  | replacement (n : ℕ) (φ : language.Formula (Option (Option (Fin n))))

def axiomSentence : AxiomCode → language.Sentence
  | .extensionality => extensionalitySentence
  | .empty => emptySentence
  | .pairing => pairingSentence
  | .union => unionSentence
  | .powerset => powersetSentence
  | .infinity => infinitySentence
  | .foundation => foundationSentence
  | .choice => choiceSentence
  | .separation _ φ => separationSentence φ
  | .replacement _ φ => replacementSentence φ

/-- The explicit axiom theory, not the complete theory of any chosen structure. -/
def zfcTheory : language.Theory := Set.range axiomSentence

theorem axiomSentence_mem (c : AxiomCode) : axiomSentence c ∈ zfcTheory :=
  ⟨c, rfl⟩

theorem model_zfc_iff_sentences :
    M ⊨ zfcTheory ↔ ∀ c : AxiomCode, M ⊨ axiomSentence c := by
  simp [Theory.model_iff, zfcTheory]

end Komorebi.ZFCAxiomSyntax
