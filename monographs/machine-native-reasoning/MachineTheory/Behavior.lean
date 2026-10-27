import Mathlib.Data.Fintype.Card
import Mathlib.Data.Set.Image

/-!
# Evidence and initialized behavioral state

Reviewed Core v0.2, Proposition 1.1 and Theorem 1.2.
Words are executed left to right. Operations are total on the declared state type.
An invariant domain can be represented by a subtype carrying its restricted operations.
The factorization theorems use attained records, so impossible records need no decoder.
-/

namespace Komorebi.MachineTheory

universe u v w z

/-- Exactly the record values produced by at least one state. -/
def Attained {X : Type u} {H : Type v} (r : X → H) :=
  {h : H // ∃ x, r x = h}

def record {X : Type u} {H : Type v} (r : X → H) (x : X) : Attained r :=
  ⟨r x, x, rfl⟩

def FiberConstant {X : Type u} {H : Type v} {Y : Type w}
    (r : X → H) (t : X → Y) : Prop :=
  ∀ x y, r x = r y → t x = t y

/-- Core 1.1: exact factorization through the actual observation record. -/
theorem decoder_exists_iff {X : Type u} {H : Type v} {Y : Type w}
    (r : X → H) (t : X → Y) :
    (∃ d : Attained r → Y, ∀ x, d (record r x) = t x) ↔ FiberConstant r t := by
  constructor
  · rintro ⟨d, hd⟩ x y h
    have he : record r x = record r y := Subtype.ext h
    rw [← hd x, ← hd y, he]
  · intro h
    classical
    let d : Attained r → Y := fun a => t (Classical.choose a.property)
    refine ⟨d, ?_⟩
    intro x
    exact h _ _ (Classical.choose_spec (record r x).property)

/-- A concrete collision excludes every decoder, not just one algorithm. -/
theorem no_decoder_of_collision {X : Type u} {H : Type v} {Y : Type w}
    {r : X → H} {t : X → Y} (x y : X)
    (hr : r x = r y) (ht : t x ≠ t y) :
    ¬ ∃ d : Attained r → Y, ∀ x, d (record r x) = t x := by
  intro hd
  exact ht ((decoder_exists_iff r t).mp hd x y hr)

/-- First execute the head action, then the remaining word. -/
def run {X : Type u} {A : Type v} (F : A → X → X) : List A → X → X
  | [], x => x
  | a :: w, x => run F w (F a x)

@[simp] theorem run_nil {X : Type u} {A : Type v} (F : A → X → X) (x : X) :
    run F [] x = x := rfl

@[simp] theorem run_cons {X : Type u} {A : Type v} (F : A → X → X)
    (a : A) (w : List A) (x : X) : run F (a :: w) x = run F w (F a x) := rfl

theorem run_append {X : Type u} {A : Type v} (F : A → X → X)
    (s t : List A) (x : X) : run F (s ++ t) x = run F t (run F s x) := by
  induction s generalizing x with
  | nil => rfl
  | cons a s ih => exact ih (F a x)

def SameBehavior {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) (x y : X) : Prop :=
  ∀ word, q (run F word x) = q (run F word y)

def behaviorSetoid {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) : Setoid X where
  r := SameBehavior F q
  iseqv := ⟨fun _ _ => rfl, fun h w => (h w).symm,
    fun h₁ h₂ w => (h₁ w).trans (h₂ w)⟩

abbrev BehavioralState {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) := Quotient (behaviorSetoid F q)

def behaviorClass {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) (x : X) : BehavioralState F q :=
  Quotient.mk _ x

theorem sameBehavior_step {X : Type u} {A : Type v} {Y : Type w}
    {F : A → X → X} {q : X → Y} {x y : X} (h : SameBehavior F q x y) (a : A) :
    SameBehavior F q (F a x) (F a y) := by
  intro word
  exact h (a :: word)

def quotientStep {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) (a : A) : BehavioralState F q → BehavioralState F q :=
  Quotient.map (F a) (fun _ _ h => sameBehavior_step h a)

def quotientRead {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) : BehavioralState F q → Y :=
  Quotient.lift q (fun _ _ h => h [])

@[simp] theorem quotientStep_class {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) (a : A) (x : X) :
    quotientStep F q a (behaviorClass F q x) = behaviorClass F q (F a x) := rfl

@[simp] theorem quotientRead_class {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) (x : X) :
    quotientRead F q (behaviorClass F q x) = q x := rfl

theorem quotient_run {X : Type u} {A : Type v} {Y : Type w}
    (F : A → X → X) (q : X → Y) (word : List A) (x : X) :
    run (quotientStep F q) word (behaviorClass F q x) = behaviorClass F q (run F word x) := by
  induction word generalizing x with
  | nil => rfl
  | cons a word ih => exact ih (F a x)

/-- A predictor's guarantee covers all finite words, not sampled continuations. -/
structure Predictor {X : Type u} {A : Type v} {Y : Type w} {H : Type z}
    (F : A → X → X) (q : X → Y) (r : X → H) (Z : Type*) where
  initState : Attained r → Z
  step : A → Z → Z
  read : Z → Y
  correct : ∀ word x, read (run step word (initState (record r x))) = q (run F word x)

/-- Any exact predictor separates behaviorally inequivalent initial states. -/
theorem Predictor.equal_initial_states {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} {Z : Type*} {F : A → X → X} {q : X → Y} {r : X → H}
    (p : Predictor F q r Z) {x y : X}
    (h : p.initState (record r x) = p.initState (record r y)) : SameBehavior F q x y := by
  intro word
  rw [← p.correct word x, ← p.correct word y, h]

theorem Predictor.record_sufficient {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} {Z : Type*} {F : A → X → X} {q : X → Y} {r : X → H}
    (p : Predictor F q r Z) : ∀ x y, r x = r y → SameBehavior F q x y := by
  intro x y h
  apply p.equal_initial_states
  exact congrArg p.initState (Subtype.ext h)

/-- The actual quotient predictor is constructed, not assumed as a structure field. -/
noncomputable def canonicalPredictor {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} (F : A → X → X) (q : X → Y) (r : X → H)
    (h : ∀ x y, r x = r y → SameBehavior F q x y) :
    Predictor F q r (BehavioralState F q) := by
  have hf : FiberConstant r (behaviorClass F q) := fun x y he => Quotient.sound (h x y he)
  let d := Classical.choose ((decoder_exists_iff r (behaviorClass F q)).mpr hf)
  have hd : ∀ x, d (record r x) = behaviorClass F q x :=
    Classical.choose_spec ((decoder_exists_iff r (behaviorClass F q)).mpr hf)
  refine ⟨d, quotientStep F q, quotientRead F q, ?_⟩
  intro word x
  rw [hd x, quotient_run]
  rfl

/-- Core 1.2, existence part. State cardinality is handled separately below. -/
theorem evidence_initialized_predictor_iff {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} (F : A → X → X) (q : X → Y) (r : X → H) :
    Nonempty (Predictor F q r (BehavioralState F q)) ↔
      (∀ x y, r x = r y → SameBehavior F q x y) := by
  constructor
  · rintro ⟨p⟩
    exact p.record_sufficient
  · intro h
    exact ⟨canonicalPredictor F q r h⟩

/-- A surjection from initialized states to behavioral classes proves minimality. -/
theorem Predictor.initialized_state_surjection {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} {Z : Type*} {F : A → X → X} {q : X → Y} {r : X → H}
    (p : Predictor F q r Z) :
    ∃ d : Attained (fun x => p.initState (record r x)) → BehavioralState F q,
      Function.Surjective d := by
  let e := fun x => p.initState (record r x)
  have hf : FiberConstant e (behaviorClass F q) := by
    intro x y he
    exact Quotient.sound (p.equal_initial_states he)
  obtain ⟨d, hd⟩ := (decoder_exists_iff e (behaviorClass F q)).mpr hf
  refine ⟨d, ?_⟩
  intro z₀
  refine Quotient.inductionOn z₀ ?_
  intro x
  exact ⟨record e x, hd x⟩


noncomputable instance attainedFintype {X : Type u} {H : Type v} [Fintype X]
    (r : X → H) : Fintype (Attained r) := by
  classical
  apply Fintype.ofSurjective (record r)
  intro h
  obtain ⟨x, hx⟩ := h.property
  exact ⟨x, Subtype.ext hx⟩

noncomputable instance behavioralFintype {X : Type u} {A : Type v} {Y : Type w}
    [Fintype X] (F : A → X → X) (q : X → Y) : Fintype (BehavioralState F q) := by
  classical
  apply Fintype.ofSurjective (behaviorClass F q)
  intro z₀
  exact Quotient.inductionOn z₀ (fun x => ⟨x, rfl⟩)

/-- Core 1.2, minimality among the *initialized* states, including redundant predictors. -/
theorem Predictor.minimal_initialized_card {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} {Z : Type*} [Fintype X] {F : A → X → X} {q : X → Y} {r : X → H}
    (p : Predictor F q r Z) :
    Fintype.card (BehavioralState F q) ≤
      Fintype.card (Attained (fun x => p.initState (record r x))) := by
  obtain ⟨d, hd⟩ := p.initialized_state_surjection
  exact Fintype.card_le_of_surjective d hd

/-- Every behavioral class is initialized in the canonical realization. -/
theorem canonical_initialization_surjective {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} (F : A → X → X) (q : X → Y) (r : X → H)
    (h : ∀ x y, r x = r y → SameBehavior F q x y) :
    Function.Surjective (fun x => (canonicalPredictor F q r h).initState (record r x)) := by
  intro z₀
  refine Quotient.inductionOn z₀ ?_
  intro x
  refine ⟨x, ?_⟩
  exact Classical.choose_spec
    ((decoder_exists_iff r (behaviorClass F q)).mpr
      (fun x y he => Quotient.sound (h x y he))) x


/-- The canonical predictor attains the lower bound on initialized finite states. -/
theorem canonical_initialized_card {X : Type u} {A : Type v} {Y : Type w}
    {H : Type z} [Fintype X] (F : A → X → X) (q : X → Y) (r : X → H)
    (h : ∀ x y, r x = r y → SameBehavior F q x y) :
    Fintype.card (Attained (fun x => (canonicalPredictor F q r h).initState (record r x))) =
      Fintype.card (BehavioralState F q) := by
  apply le_antisymm
  · exact Fintype.card_le_of_injective Subtype.val Subtype.val_injective
  · exact (canonicalPredictor F q r h).minimal_initialized_card

end Komorebi.MachineTheory

