import Komorebi.Foundation.MembershipFormula
import Komorebi.Foundation.SuccessorObstruction

/-!
# A membership-only first-order formula for complete-filter extension

Every abbreviation expands into equality, membership, implication, falsity and
first-order quantification. No semantic predicate is added as an atomic symbol.
-/

universe u v

namespace Komorebi.MembershipFormula

open FirstOrder FirstOrder.Language
open SetFilterCoding

def unorderedPairF {α : Type v} (p x y : α) : language.Formula α :=
  allF ((memF none (some p)).iff (eqF none (some x) ⊔ eqF none (some y)))

def singletonF {α : Type v} (p x : α) : language.Formula α :=
  allF ((memF none (some p)).iff (eqF none (some x)))

def pairF {α : Type v} (p x y : α) : language.Formula α :=
  exF (let p := some p; let x := some x; let y := some y; let a := none
    exF (singletonF (some a) (some x) ⊓
      (unorderedPairF none (some x) (some y) ⊓ unorderedPairF (some p) (some a) none)))

def pairMemF {α : Type v} (x y g : α) : language.Formula α :=
  exF (pairF none (some x) (some y) ⊓ memF none (some g))

def prodF {α : Type v} (r x y : α) : language.Formula α :=
  allF ((memF none (some r)).iff
    (let x := some x; let y := some y; let z := none
    exF (memF none (some x) ⊓
      (let y := some y; let z := some z; let a := none
      exF (memF none (some y) ⊓ pairF (some z) (some a) none)))))

@[simp]
theorem realize_unorderedPairF {α : Type v} (p x y : α) (e : α → ZFSet.{u}) :
    (unorderedPairF p x y).Realize e ↔ e p = {e x, e y} := by
  simp [unorderedPairF, extend, ZFSet.ext_iff]

@[simp]
theorem realize_singletonF {α : Type v} (p x : α) (e : α → ZFSet.{u}) :
    (singletonF p x).Realize e ↔ e p = {e x} := by
  simp [singletonF, extend, ZFSet.ext_iff]

@[simp]
theorem realize_pairF {α : Type v} (p x y : α) (e : α → ZFSet.{u}) :
    (pairF p x y).Realize e ↔ e p = ZFSet.pair (e x) (e y) := by
  simp [pairF, extend, ZFSet.pair]

@[simp]
theorem realize_pairMemF {α : Type v} (x y g : α) (e : α → ZFSet.{u}) :
    (pairMemF x y g).Realize e ↔ ZFSet.pair (e x) (e y) ∈ e g := by
  simp [pairMemF, extend]

@[simp]
theorem realize_prodF {α : Type v} (r x y : α) (e : α → ZFSet.{u}) :
    (prodF r x y).Realize e ↔ e r = ZFSet.prod (e x) (e y) := by
  simp [prodF, extend, ZFSet.ext_iff, ZFSet.mem_prod]

def funcF {α : Type v} (x y g : α) : language.Formula α :=
  (exF (prodF none (some x) (some y) ⊓ subsetF (some g) none)) ⊓
  allF (let x := some x; let g := some g; let a := none
    (memF a x).imp
      (exF (let g := some g; let a := some a; let b := none
        pairMemF a b g ⊓
          allF ((pairMemF (some a) none (some g)).imp (eqF none (some b))))))

def injectiveF {α : Type v} (x g : α) : language.Formula α :=
  allF (let x := some x; let g := some g; let a := none
    (memF a x).imp
      (allF (let x := some x; let g := some g; let a := some a; let b := none
        (memF b x).imp
          (allF ((pairMemF (some a) none (some g)).imp
            ((pairMemF (some b) none (some g)).imp (eqF (some a) (some b))))))))

def embedsF {α : Type v} (x y : α) : language.Formula α :=
  exF (funcF (some x) (some y) none ⊓ injectiveF (some x) none)

def smallF {α : Type v} (k s : α) : language.Formula α :=
  exF (memF none (some k) ⊓ embedsF (some s) none)

@[simp]
theorem realize_funcF {α : Type v} (x y g : α) (e : α → ZFSet.{u}) :
    (funcF x y g).Realize e ↔ ZFSet.IsFunc (e x) (e y) (e g) := by
  simp [funcF, extend, ZFSet.IsFunc, ExistsUnique]

@[simp]
theorem realize_injectiveF {α : Type v} (x g : α) (e : α → ZFSet.{u}) :
    (injectiveF x g).Realize e ↔
      ∀ a ∈ e x, ∀ b ∈ e x, ∀ c : ZFSet.{u},
        ZFSet.pair a c ∈ e g → ZFSet.pair b c ∈ e g → a = b := by
  simp [injectiveF, extend]

@[simp]
theorem realize_embedsF {α : Type v} (x y : α) (e : α → ZFSet.{u}) :
    (embedsF x y).Realize e ↔ SetEmbeds (e x) (e y) := by
  simp [embedsF, extend, SetEmbeds]

@[simp]
theorem realize_smallF {α : Type v} (k s : α) (e : α → ZFSet.{u}) :
    (smallF k s).Realize e ↔ SetSmall (e k) (e s) := by
  simp [smallF, extend, SetSmall]


def boundedFamilyF {α : Type v} (x f : α) : language.Formula α :=
  allF ((memF none (some f)).imp (subsetF none (some x)))

def upwardF {α : Type v} (x f : α) : language.Formula α :=
  allF (let x := some x; let f := some f; let s := none
    allF ((memF (some s) (some f)).imp
      ((subsetF (some s) none).imp
        ((subsetF none (some x)).imp (memF none (some f))))))

def meetClosedF {α : Type v} (f : α) : language.Formula α :=
  allF (let f := some f; let s := none
    allF (let f := some f; let s := some s; let t := none
      (memF s f).imp ((memF t f).imp
        (exF (interF none (some s) (some t) ⊓ memF none (some f))))))

def filterF {α : Type v} (x f : α) : language.Formula α :=
  boundedFamilyF x f ⊓ (memF x f ⊓ (upwardF x f ⊓ meetClosedF f))

def properF {α : Type v} (x f : α) : language.Formula α :=
  filterF x f ⊓ allF ((emptyF none).imp (memF none (some f)).not)

def ultraF {α : Type v} (x f : α) : language.Formula α :=
  filterF x f ⊓
    allF (let x := some x; let f := some f; let s := none
      (subsetF s x).imp
        (exF (diffF none (some x) (some s) ⊓
          (memF (some s) (some f)).iff (memF none (some f)).not)))

def completeF {α : Type v} (k x f : α) : language.Formula α :=
  allF (let k := some k; let x := some x; let f := some f; let s := none
    (subsetF s f).imp ((smallF k s).imp
      (exF (relInterF none (some x) (some s) ⊓ memF none (some f)))))

def extensionF {α : Type v} (k : α) : language.Formula α :=
  allF (let k := some k; let x := none
    allF (let k := some k; let x := some x; let f := none
      (properF x f).imp ((completeF k x f).imp
        (exF (ultraF (some x) none ⊓
          (subsetF (some f) none ⊓ completeF (some k) (some x) none))))))

@[simp]
theorem realize_boundedFamilyF {α : Type v} (x f : α) (e : α → ZFSet.{u}) :
    (boundedFamilyF x f).Realize e ↔ e f ⊆ (e x).powerset := by
  simp [boundedFamilyF, extend, ZFSet.subset_def, ZFSet.mem_powerset]

@[simp]
theorem realize_upwardF {α : Type v} (x f : α) (e : α → ZFSet.{u}) :
    (upwardF x f).Realize e ↔
      ∀ S T : ZFSet.{u}, S ∈ e f → S ⊆ T → T ⊆ e x → T ∈ e f := by
  simp [upwardF, extend]

@[simp]
theorem realize_meetClosedF {α : Type v} (f : α) (e : α → ZFSet.{u}) :
    (meetClosedF f).Realize e ↔
      ∀ S T : ZFSet.{u}, S ∈ e f → T ∈ e f → S ∩ T ∈ e f := by
  simp [meetClosedF, extend]

@[simp]
theorem realize_filterF {α : Type v} (x f : α) (e : α → ZFSet.{u}) :
    (filterF x f).Realize e ↔ IsSetFilter (e x) (e f) := by
  simp only [filterF, Formula.realize_inf, realize_boundedFamilyF, realize_memF,
    realize_upwardF, realize_meetClosedF]
  constructor
  · rintro ⟨hb, ht, hu, hm⟩
    exact ⟨hb, ht, hu, hm⟩
  · intro h
    exact ⟨h.bounded, h.top, h.upward, h.meet⟩

@[simp]
theorem realize_properF {α : Type v} (x f : α) (e : α → ZFSet.{u}) :
    (properF x f).Realize e ↔ IsProperSetFilter (e x) (e f) := by
  simp [properF, extend, IsProperSetFilter]

@[simp]
theorem realize_ultraF {α : Type v} (x f : α) (e : α → ZFSet.{u}) :
    (ultraF x f).Realize e ↔ IsSetUltrafilter (e x) (e f) := by
  simp [ultraF, extend, IsSetUltrafilter]

@[simp]
theorem realize_completeF {α : Type v} (k x f : α) (e : α → ZFSet.{u}) :
    (completeF k x f).Realize e ↔ InternalComplete (e k) (e x) (e f) := by
  simp [completeF, extend, InternalComplete]

/-- Interpretation of the actual syntax tree into the entirely set-quantified predicate. -/
@[simp]
theorem realize_extensionF {α : Type v} (k : α) (e : α → ZFSet.{u}) :
    (extensionF k).Realize e ↔ InternalExtension (e k) := by
  simp [extensionF, extend, InternalExtension]

/-- The requested one-free-variable formula uses exactly the membership language. -/
def extensionFormula : language.Formula Unit := extensionF ()

/-- A semantic adequacy theorem in the concrete ZFSet universe. This is not yet
an object-language proof from the first-order axioms of ZFC. -/
theorem extensionFormula_iff_filterExtension (κ : Cardinal.{u}) :
    extensionFormula.Realize (fun _ => κ.ord.toZFSet) ↔
      CompactnessClassification.CompleteFilterExtension κ :=
  (realize_extensionF () (fun _ => κ.ord.toZFSet)).trans
    (internalExtension_iff_extension κ)

theorem extensionFormula_iff_residual (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    extensionFormula.Realize (fun _ => κ.ord.toZFSet) ↔
      CompactnessClassification.FixedDomainKRR κ :=
  (extensionFormula_iff_filterExtension κ).trans
    (CompactnessClassification.krr_iff_extension κ hκ).symm

theorem extensionFormula_aleph0 :
    extensionFormula.Realize (fun _ => Cardinal.aleph0.{u}.ord.toZFSet) :=
  (extensionFormula_iff_filterExtension _).mpr CompactnessClassification.extension_aleph0


/-- The predecessor's counterexample transfers all the way to actual syntax. -/
theorem not_extensionFormula_successor (μ : Cardinal.{u}) (hμ : Cardinal.aleph0 ≤ μ) :
    ¬ extensionFormula.Realize (fun _ => (Order.succ μ).ord.toZFSet) := by
  intro h
  exact CompactnessClassification.not_extension_successor μ hμ
    ((extensionFormula_iff_filterExtension _).mp h)

end Komorebi.MembershipFormula
