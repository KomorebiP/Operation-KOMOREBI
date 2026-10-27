import Komorebi.Foundation.FilterExtensionFormula
import Komorebi.Foundation.SetCardinalGuard

/-!
# The guarded closed membership-language existence sentence

The guard is a syntax tree over membership and equality, not a new relation
symbol. Its semantic classification recovers regular uncountable initial
cardinals. The final sentence is interpreted, not asserted to hold.
-/

universe u v

namespace Komorebi.MembershipFormula

open FirstOrder FirstOrder.Language
open SetFilterCoding CompactnessClassification

def transitiveF {α : Type v} (k : α) : language.Formula α :=
  allF ((memF none (some k)).imp (subsetF none (some k)))

def ordinalF {α : Type v} (k : α) : language.Formula α :=
  transitiveF k ⊓ allF ((memF none (some k)).imp (transitiveF none))

def initialF {α : Type v} (k : α) : language.Formula α :=
  ordinalF k ⊓ allF ((memF none (some k)).imp (embedsF (some k) none).not)

def successorF {α : Type v} (r x : α) : language.Formula α :=
  allF ((memF none (some r)).iff (eqF none (some x) ⊔ memF none (some x)))

def inductiveF {α : Type v} (w : α) : language.Formula α :=
  (exF (emptyF none ⊓ memF none (some w))) ⊓
    allF ((memF none (some w)).imp
      (exF (successorF none (some none) ⊓ memF none (some (some w)))))

def hasInductiveMemberF {α : Type v} (k : α) : language.Formula α :=
  exF (memF none (some k) ⊓ inductiveF none)

def smallSubsetsBoundedF {α : Type v} (k : α) : language.Formula α :=
  allF ((subsetF none (some k)).imp ((smallF (some k) none).imp
    (exF (memF none (some (some k)) ⊓ subsetF (some none) none))))

def guardF {α : Type v} (k : α) : language.Formula α :=
  initialF k ⊓ (hasInductiveMemberF k ⊓ smallSubsetsBoundedF k)

@[simp]
theorem realize_transitiveF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (transitiveF k).Realize e ↔ (e k).IsTransitive := by
  simp [transitiveF, extend, ZFSet.IsTransitive]

@[simp]
theorem realize_ordinalF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (ordinalF k).Realize e ↔ (e k).IsOrdinal := by
  simp [ordinalF, extend, ZFSet.isOrdinal_iff_forall_mem_isTransitive]

@[simp]
theorem realize_initialF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (initialF k).Realize e ↔ IsInitial (e k) := by
  simp [initialF, extend, IsInitial]

@[simp]
theorem realize_successorF {α : Type v} (r x : α) (e : α → ZFSet.{u}) :
    (successorF r x).Realize e ↔ e r = insert (e x) (e x) := by
  simp [successorF, extend, ZFSet.ext_iff]

@[simp]
theorem realize_inductiveF {α : Type v} (w : α) (e : α → ZFSet.{u}) :
    (inductiveF w).Realize e ↔ IsInductive (e w) := by
  simp [inductiveF, extend, IsInductive]

@[simp]
theorem realize_hasInductiveMemberF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (hasInductiveMemberF k).Realize e ↔ HasInductiveMember (e k) := by
  simp [hasInductiveMemberF, extend, HasInductiveMember]

@[simp]
theorem realize_smallSubsetsBoundedF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (smallSubsetsBoundedF k).Realize e ↔ SmallSubsetsBounded (e k) := by
  simp [smallSubsetsBoundedF, extend, SmallSubsetsBounded]

@[simp]
theorem realize_guardF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (guardF k).Realize e ↔ RegularUncountableGuard (e k) := by
  simp [guardF, RegularUncountableGuard]

/-- A closed sentence: no free variables, constants, or extra relation symbols. -/
def guardedExtensionSentence : language.Sentence :=
  exF (guardF none ⊓ extensionF none)

/-- Deliberately retained as a regression: this is not the intended axiom. -/
def unguardedExtensionSentence : language.Sentence := exF (extensionF none)

theorem realize_guardF_initial (κ : Cardinal.{u}) :
    (guardF ()).Realize (fun _ : Unit => κ.ord.toZFSet) ↔
      κ.IsRegular ∧ Cardinal.aleph0 < κ :=
  (realize_guardF () _).trans (guard_initial_iff κ)

/-- Exact characterization of all possible set witnesses, not just chosen codes. -/
theorem realize_guardF_iff_cardinal {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (guardF k).Realize e ↔
      ∃ κ : Cardinal.{u}, e k = κ.ord.toZFSet ∧ κ.IsRegular ∧ Cardinal.aleph0 < κ :=
  (realize_guardF k e).trans (guard_iff_exists_cardinal (e k))

theorem guardedSentence_iff_internal :
    ZFSet.{u} ⊨ guardedExtensionSentence ↔
      ∃ K : ZFSet.{u}, RegularUncountableGuard K ∧ InternalExtension K := by
  simp [Sentence.Realize, guardedExtensionSentence, extend]

/-- The closed syntax has exactly the earlier independently specified meaning.
This is semantic adequacy in ZFSet, not existence or ZFC derivability. -/
theorem guardedSentence_iff_filterExtensionExistence :
    ZFSet.{u} ⊨ guardedExtensionSentence ↔ FilterExtensionExistence.{u} := by
  rw [guardedSentence_iff_internal]
  constructor
  · rintro ⟨K, hguard, hext⟩
    obtain ⟨κ, rfl, hr, hu⟩ := (guard_iff_exists_cardinal K).mp hguard
    exact ⟨κ, hr, hu, (internalExtension_iff_extension κ).mp hext⟩
  · rintro ⟨κ, hr, hu, hext⟩
    exact ⟨κ.ord.toZFSet, (guard_initial_iff κ).mpr ⟨hr, hu⟩,
      (internalExtension_iff_extension κ).mpr hext⟩

theorem guardedSentence_iff_residualExistence :
    ZFSet.{u} ⊨ guardedExtensionSentence ↔ ResidualExistence.{u} :=
  guardedSentence_iff_filterExtensionExistence.trans
    residualExistence_iff_filterExtensionExistence.symm

/-- Omitting the guard yields a sentence already true at the ordinary baseline. -/
theorem unguardedSentence_true : ZFSet.{u} ⊨ unguardedExtensionSentence := by
  simp only [Sentence.Realize, unguardedExtensionSentence, realize_exF, realize_extensionF]
  exact ⟨Cardinal.aleph0.ord.toZFSet,
    (internalExtension_iff_extension _).mpr extension_aleph0⟩

/-- The aleph0 theorem cannot witness the guarded sentence. -/
theorem aleph0_not_guarded_witness :
    ¬ (guardF () ⊓ extensionF ()).Realize
      (fun _ : Unit => Cardinal.aleph0.{u}.ord.toZFSet) := by
  simp only [Formula.realize_inf, realize_guardF]
  exact fun h => not_guard_aleph0 h.1

/-- Successor failure remains a failure after adding the guard. -/
theorem successor_not_guarded_witness (μ : Cardinal.{u}) (hμ : Cardinal.aleph0 ≤ μ) :
    ¬ (guardF () ⊓ extensionF ()).Realize
      (fun _ : Unit => (Order.succ μ).ord.toZFSet) := by
  intro h
  have h := Formula.realize_inf.mp h
  exact not_extension_successor μ hμ
    ((internalExtension_iff_extension _).mp ((realize_extensionF () _).mp h.2))

/-- A cardinal failing regularity cannot pass the guard, independently of extension. -/
theorem nonregular_not_guarded_witness (κ : Cardinal.{u}) (hκ : ¬ κ.IsRegular) :
    ¬ (guardF () ⊓ extensionF ()).Realize (fun _ : Unit => κ.ord.toZFSet) := by
  intro h
  have h := Formula.realize_inf.mp h
  exact hκ (((realize_guardF_initial κ).mp h.1).1)

end Komorebi.MembershipFormula
