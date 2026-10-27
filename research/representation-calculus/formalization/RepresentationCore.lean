module
public import Std

@[expose] public section

/- Task-relative observational semantics, independent of a coefficient ring.
   States and operations are not assumed finite or linear. -/
namespace Komorebi.Representation
universe u v w z

structure System (X : Type u) (A : Type v) (O : Type w) (V : Type z) where
  step : A → X → X
  observe : O → X → V

variable {X Y Z : Type u} {A : Type v} {O : Type w} {V : Type z}

def run (S : System X A O V) : List A → X → X
  | [], x => x
  | a :: w, x => run S w (S.step a x)

def behavior (S : System X A O V) (x : X) (w : List A) (j : O) : V :=
  S.observe j (run S w x)

theorem run_append (S : System X A O V) (w v : List A) (x : X) :
    run S (w ++ v) x = run S v (run S w x) := by
  induction w generalizing x with
  | nil => rfl
  | cons a w ih => exact ih (S.step a x)

def ObsEq (S : System X A O V) (x y : X) : Prop :=
  ∀ w j, behavior S x w j = behavior S y w j

theorem obsEq_refl (S : System X A O V) (x : X) : ObsEq S x x :=
  fun _ _ => rfl

theorem obsEq_symm (S : System X A O V) {x y : X} (h : ObsEq S x y) :
    ObsEq S y x := fun w j => (h w j).symm

theorem obsEq_trans (S : System X A O V) {x y t : X}
    (h : ObsEq S x y) (g : ObsEq S y t) : ObsEq S x t :=
  fun w j => (h w j).trans (g w j)

theorem obsEq_step (S : System X A O V) {x y : X} (h : ObsEq S x y) (a : A) :
    ObsEq S (S.step a x) (S.step a y) := by
  intro w j
  exact h (a :: w) j

theorem invariant_relation_sound (S : System X A O V) (K : X → X → Prop)
    (hout : ∀ x y, K x y → ∀ j, S.observe j x = S.observe j y)
    (hstep : ∀ x y, K x y → ∀ a, K (S.step a x) (S.step a y))
    {x y : X} (h : K x y) : ObsEq S x y := by
  intro w
  induction w generalizing x y with
  | nil => exact hout x y h
  | cons a w ih => exact ih (hstep x y h a)

structure Transport (S : System X A O V) (T : System Y A O V) where
  encode : X → Y
  step_ok : ∀ a x, encode (S.step a x) = T.step a (encode x)
  observe_ok : ∀ j x, S.observe j x = T.observe j (encode x)

theorem transport_run {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (w : List A) (x : X) :
    q.encode (run S w x) = run T w (q.encode x) := by
  induction w generalizing x with
  | nil => rfl
  | cons a w ih =>
    change q.encode (run S w (S.step a x)) = run T w (T.step a (q.encode x))
    rw [ih, q.step_ok]

theorem transport_behavior {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (w : List A) (j : O) (x : X) :
    behavior S x w j = behavior T (q.encode x) w j := by
  unfold behavior
  rw [q.observe_ok, transport_run]

def Transport.comp {S : System X A O V} {T : System Y A O V}
    {U : System Z A O V} (q : Transport S T) (v : Transport T U) : Transport S U where
  encode := v.encode ∘ q.encode
  step_ok := by intro a x; simp only [Function.comp_apply, q.step_ok, v.step_ok]
  observe_ok := by intro j x; exact (q.observe_ok j x).trans (v.observe_ok j (q.encode x))

def behaviorSetoid (S : System X A O V) : Setoid X where
  r := ObsEq S
  iseqv := ⟨obsEq_refl S, obsEq_symm S, obsEq_trans S⟩

abbrev BehaviorQuotient (S : System X A O V) := Quotient (behaviorSetoid S)

def quotientStep (S : System X A O V) (a : A) : BehaviorQuotient S → BehaviorQuotient S :=
  Quotient.lift (fun x => Quotient.mk _ (S.step a x))
    (fun _ _ h => Quotient.sound (obsEq_step S h a))

def quotientObserve (S : System X A O V) (j : O) : BehaviorQuotient S → V :=
  Quotient.lift (S.observe j) (fun _ _ h => h [] j)

def quotientSystem (S : System X A O V) : System (BehaviorQuotient S) A O V where
  step := quotientStep S
  observe := quotientObserve S

def quotientTransport (S : System X A O V) : Transport S (quotientSystem S) where
  encode := Quotient.mk _
  step_ok := by intros; rfl
  observe_ok := by intros; rfl

theorem quotient_exact (S : System X A O V) (x y : X) :
    (quotientTransport S).encode x = (quotientTransport S).encode y ↔ ObsEq S x y :=
by
  constructor
  · intro h; exact Quotient.exact h
  · intro h; exact Quotient.sound (s := behaviorSetoid S) h

theorem transport_kernel_sound {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) {x y : X} (h : q.encode x = q.encode y) : ObsEq S x y := by
  intro w j
  rw [transport_behavior q, transport_behavior q, h]

noncomputable def sufficientFactor {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y) : Y → BehaviorQuotient S :=
  fun y => Quotient.mk _ (Classical.choose (hs y))

theorem sufficientFactor_encode {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y) (x : X) :
    sufficientFactor q hs (q.encode x) = Quotient.mk _ x := by
  apply Quotient.sound
  apply transport_kernel_sound q
  exact Classical.choose_spec (hs (q.encode x))

theorem sufficientFactor_unique {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (f : Y → BehaviorQuotient S) (hf : ∀ x, f (q.encode x) = Quotient.mk _ x) :
    f = sufficientFactor q hs := by
  funext y
  obtain ⟨x, rfl⟩ := hs y
  exact (hf x).trans (sufficientFactor_encode q hs x).symm

noncomputable def sufficientFactorTransport {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y) :
    Transport T (quotientSystem S) where
  encode := sufficientFactor q hs
  step_ok := by
    intro a y
    obtain ⟨x, rfl⟩ := hs y
    rw [← q.step_ok, sufficientFactor_encode, sufficientFactor_encode]
    rfl
  observe_ok := by
    intro j y
    obtain ⟨x, rfl⟩ := hs y
    rw [sufficientFactor_encode]
    exact (q.observe_ok j x).symm

theorem profile_restriction {B : Type v} {J : Type w}
    (S : System X A O V) (actions : B → A) (observations : J → O)
    {x y : X} (h : ObsEq S x y) :
    ObsEq ({ step := fun b => S.step (actions b),
             observe := fun j => S.observe (observations j) } : System X B J V) x y := by
  apply invariant_relation_sound _ (ObsEq S)
  · intro a b hab j; exact hab [] (observations j)
  · intro a b hab c; exact obsEq_step S hab (actions c)
  · exact h

-- Soundness of certificates that explicitly separate every distinct encoded state.
theorem separated_encoding_exact {S : System X A O V} {T : System Y A O V}
    (q : Transport S T)
    (hsep : ∀ y z, y ≠ z → ∃ w j, behavior T y w j ≠ behavior T z w j)
    (x y : X) : ObsEq S x y ↔ q.encode x = q.encode y := by
  constructor
  · intro h
    apply Classical.byContradiction
    intro hne
    obtain ⟨w, j, hw⟩ := hsep _ _ hne
    apply hw
    rw [← transport_behavior q, ← transport_behavior q]
    exact h w j
  · exact transport_kernel_sound q

-- A new semantic action may expose distinctions that the old profile hid.
theorem distinguishing_word_excludes_merge {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (x y : X) (w : List A) (j : O)
    (hne : behavior S x w j ≠ behavior S y w j) : q.encode x ≠ q.encode y := by
  intro heq
  exact hne (transport_kernel_sound q heq w j)

end Komorebi.Representation
