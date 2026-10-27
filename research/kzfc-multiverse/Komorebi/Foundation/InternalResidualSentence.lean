import Komorebi.Foundation.ZFCModelSemantics

/-!
# The internal reading of the residual sentence in any membership structure

Every object below, including product graphs, subset families and size
witnesses, belongs to M. There is no reference to external Cardinal, Filter,
powersets, cofinalities or functions-as-set witnesses.
-/

universe u v

namespace Komorebi.InternalResidualSentence

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax

variable {M : Type u} [language.Structure M]

def Inter (r s t : M) : Prop :=
  ∀ z : M, member z r ↔ member z s ∧ member z t

def Diff (r x s : M) : Prop :=
  ∀ z : M, member z r ↔ member z x ∧ ¬ member z s

def RelInter (r x s : M) : Prop :=
  ∀ z : M, member z r ↔ member z x ∧ ∀ t : M, member t s → member z t

def Product (r x y : M) : Prop :=
  ∀ z : M, member z r ↔ ∃ a : M, member a x ∧
    ∃ b : M, member b y ∧ IsOrderedPair z a b

/-- Product and graph witnesses are internal elements, not external collections. -/
def FunctionGraph (x y g : M) : Prop :=
  (∃ p : M, Product p x y ∧ subset g p) ∧
    ∀ a : M, member a x → ∃ b : M, PairMember a b g ∧
      ∀ c : M, PairMember a c g → c = b

def InjectiveGraph (x g : M) : Prop :=
  ∀ a : M, member a x → ∀ b : M, member b x → ∀ c : M,
    PairMember a c g → PairMember b c g → a = b

def Embeds (x y : M) : Prop := ∃ g : M, FunctionGraph x y g ∧ InjectiveGraph x g

def Small (k s : M) : Prop := ∃ a : M, member a k ∧ Embeds s a

def FilterOn (x f : M) : Prop :=
  (∀ s : M, member s f → subset s x) ∧ member x f ∧
    (∀ s t : M, member s f → subset s t → subset t x → member t f) ∧
    ∀ s t : M, member s f → member t f → ∃ r : M, Inter r s t ∧ member r f

def ProperFilterOn (x f : M) : Prop :=
  FilterOn x f ∧ ∀ e : M, IsEmpty e → ¬ member e f

def UltrafilterOn (x f : M) : Prop :=
  FilterOn x f ∧ ∀ s : M, subset s x →
    ∃ d : M, Diff d x s ∧ (member s f ↔ ¬ member d f)

def CompleteOn (k x f : M) : Prop :=
  ∀ s : M, subset s f → Small k s → ∃ r : M, RelInter r x s ∧ member r f

def Extension (k : M) : Prop :=
  ∀ x f : M, ProperFilterOn x f → CompleteOn k x f →
    ∃ g : M, UltrafilterOn x g ∧ subset f g ∧ CompleteOn k x g

def Transitive (k : M) : Prop := ∀ a : M, member a k → subset a k

def OrdinalPredicate (k : M) : Prop :=
  Transitive k ∧ ∀ a : M, member a k → Transitive a

def Initial (k : M) : Prop :=
  OrdinalPredicate k ∧ ∀ a : M, member a k → ¬ Embeds k a

def HasInductiveMember (k : M) : Prop :=
  ∃ w : M, member w k ∧ GeneralMembershipSemantics.IsInductive w

def SmallBounded (k : M) : Prop :=
  ∀ s : M, subset s k → Small k s → ∃ b : M, member b k ∧ subset s b

def Guard (k : M) : Prop := Initial k ∧ HasInductiveMember k ∧ SmallBounded k

def GuardedExtension (M : Type u) [language.Structure M] : Prop :=
  ∃ k : M, Guard k ∧ Extension k

@[simp]
theorem interF_internal {α : Type v} (r s t : α) (e : α → M) :
    (interF r s t).Realize e ↔ Inter (e r) (e s) (e t) := by
  simp [interF, Inter, assign]

@[simp]
theorem diffF_internal {α : Type v} (r x s : α) (e : α → M) :
    (diffF r x s).Realize e ↔ Diff (e r) (e x) (e s) := by
  simp [diffF, Diff, assign]

@[simp]
theorem relInterF_internal {α : Type v} (r x s : α) (e : α → M) :
    (relInterF r x s).Realize e ↔ RelInter (e r) (e x) (e s) := by
  simp [relInterF, RelInter, assign]

@[simp]
theorem prodF_internal {α : Type v} (r x y : α) (e : α → M) :
    (prodF r x y).Realize e ↔ Product (e r) (e x) (e y) := by
  simp [prodF, Product, assign]

@[simp]
theorem funcF_internal {α : Type v} (x y g : α) (e : α → M) :
    (funcF x y g).Realize e ↔ FunctionGraph (e x) (e y) (e g) := by
  simp [funcF, FunctionGraph, assign]

@[simp]
theorem injectiveF_internal {α : Type v} (x g : α) (e : α → M) :
    (injectiveF x g).Realize e ↔ InjectiveGraph (e x) (e g) := by
  simp [injectiveF, InjectiveGraph, assign]

@[simp]
theorem embedsF_internal {α : Type v} (x y : α) (e : α → M) :
    (embedsF x y).Realize e ↔ Embeds (e x) (e y) := by
  simp [embedsF, Embeds, assign]

@[simp]
theorem smallF_internal {α : Type v} (k s : α) (e : α → M) :
    (smallF k s).Realize e ↔ Small (e k) (e s) := by
  simp [smallF, Small, assign]

@[simp]
theorem filterF_internal {α : Type v} (x f : α) (e : α → M) :
    (filterF x f).Realize e ↔ FilterOn (e x) (e f) := by
  simp [filterF, boundedFamilyF, upwardF, meetClosedF, FilterOn, assign]

@[simp]
theorem properF_internal {α : Type v} (x f : α) (e : α → M) :
    (properF x f).Realize e ↔ ProperFilterOn (e x) (e f) := by
  simp [properF, ProperFilterOn, assign]

@[simp]
theorem ultraF_internal {α : Type v} (x f : α) (e : α → M) :
    (ultraF x f).Realize e ↔ UltrafilterOn (e x) (e f) := by
  simp [ultraF, UltrafilterOn, assign]

@[simp]
theorem completeF_internal {α : Type v} (k x f : α) (e : α → M) :
    (completeF k x f).Realize e ↔ CompleteOn (e k) (e x) (e f) := by
  simp [completeF, CompleteOn, assign]

@[simp]
theorem extensionF_internal {α : Type v} (k : α) (e : α → M) :
    (extensionF k).Realize e ↔ Extension (e k) := by
  simp [extensionF, Extension, assign]

@[simp]
theorem transitiveF_internal {α : Type v} (k : α) (e : α → M) :
    (transitiveF k).Realize e ↔ Transitive (e k) := by
  simp [transitiveF, Transitive, assign]

@[simp]
theorem ordinalF_internal {α : Type v} (k : α) (e : α → M) :
    (ordinalF k).Realize e ↔ OrdinalPredicate (e k) := by
  simp [ordinalF, OrdinalPredicate, assign]

@[simp]
theorem initialF_internal {α : Type v} (k : α) (e : α → M) :
    (initialF k).Realize e ↔ Initial (e k) := by
  simp [initialF, Initial, assign]

@[simp]
theorem hasInductiveMemberF_internal {α : Type v} (k : α) (e : α → M) :
    (hasInductiveMemberF k).Realize e ↔ HasInductiveMember (e k) := by
  simp [hasInductiveMemberF, HasInductiveMember, assign]

@[simp]
theorem smallSubsetsBoundedF_internal {α : Type v} (k : α) (e : α → M) :
    (smallSubsetsBoundedF k).Realize e ↔ SmallBounded (e k) := by
  simp [smallSubsetsBoundedF, SmallBounded, assign]

@[simp]
theorem guardF_internal {α : Type v} (k : α) (e : α → M) :
    (guardF k).Realize e ↔ Guard (e k) := by
  simp [guardF, Guard]

/-- Uniform internal interpretation for all structures, including models whose
internal cardinals or sets disagree with the surrounding universe. -/
theorem guardedSentence_iff_internal_model :
    M ⊨ guardedExtensionSentence ↔ GuardedExtension M := by
  simp [Sentence.Realize, guardedExtensionSentence, GuardedExtension, assign]

end Komorebi.InternalResidualSentence
