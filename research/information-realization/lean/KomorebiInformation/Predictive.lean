module
public import KomorebiInformation.Foundations
public import Mathlib.Logic.Function.Iterate
@[expose] public section

namespace KomorebiInformation.Predictive
variable {X O S A : Type*}

/-- Apply a finite action word in chronological order. -/
def run (T : A → X → X) : List A → X → X
  | [], x => x
  | a :: w, x => run T w (T a x)

theorem run_nil (T : A → X → X) (x : X) : run T [] x = x := rfl

theorem run_cons (T : A → X → X) (a : A) (w : List A) (x : X) :
    run T (a::w) x = run T w (T a x) := rfl

theorem run_append (T : A → X → X) (v w : List A) (x : X) :
    run T (v++w) x = run T w (run T v x) := by
  induction v generalizing x with
  | nil => rfl
  | cons a v ih => exact ih (T a x)

/-- One-step commuting equations imply exact simulation for every finite word. -/
theorem simulation_all_words (T : A → X → X) (M : A → S → S) (s : X → S)
    (hstep : ∀ a x, s (T a x) = M a (s x)) (w : List A) (x : X) :
    s (run T w x) = run M w (s x) := by
  induction w generalizing x with
  | nil => rfl
  | cons a w ih =>
    change s (run T w (T a x)) = run M w (M a (s x))
    rw [ih, hstep]

theorem observable_simulation_all_words
    (T : A → X → X) (M : A → S → S) (s : X → S) (r : X → O) (d : S → O)
    (hstep : ∀ a x, s (T a x) = M a (s x)) (hobs : ∀ x, r x = d (s x))
    (w : List A) (x : X) : r (run T w x) = d (run M w (s x)) := by
  rw [hobs, simulation_all_words T M s hstep]

/-- Two states are equivalent precisely when no admissible word distinguishes them. -/
def OperationalEq (T : A → X → X) (r : X → O) (x y : X) : Prop :=
  ∀ w, r (run T w x) = r (run T w y)

def operationalSetoid (T : A → X → X) (r : X → O) : Setoid X where
  r := OperationalEq T r
  iseqv := ⟨fun _ _ => rfl, fun h w => (h w).symm,
    fun hxy hyz w => (hxy w).trans (hyz w)⟩

theorem operational_preserves_observation {T : A → X → X} {r : X → O} {x y : X}
    (h : OperationalEq T r x y) : r x = r y := h []

theorem operational_stable {T : A → X → X} {r : X → O} {x y : X}
    (h : OperationalEq T r x y) (a : A) : OperationalEq T r (T a x) (T a y) := by
  intro w
  exact h (a::w)

/-- Canonical operational information, as a genuine Lean quotient. -/
def InfoSpace (T : A → X → X) (r : X → O) := Quotient (operationalSetoid T r)

def realize (T : A → X → X) (r : X → O) (x : X) : InfoSpace T r :=
  Quotient.mk _ x

def observe (T : A → X → X) (r : X → O) : InfoSpace T r → O :=
  Quotient.lift r (fun _ _ h => operational_preserves_observation h)

def act (T : A → X → X) (r : X → O) (a : A) : InfoSpace T r → InfoSpace T r :=
  Quotient.map (T a) (fun _ _ h => operational_stable h a)

theorem observe_realize (T : A → X → X) (r : X → O) (x : X) :
    observe T r (realize T r x) = r x := rfl

theorem act_realize (T : A → X → X) (r : X → O) (a : A) (x : X) :
    act T r a (realize T r x) = realize T r (T a x) := rfl

theorem realize_eq_iff (T : A → X → X) (r : X → O) (x y : X) :
    realize T r x = realize T r y ↔ OperationalEq T r x y :=
  ⟨Quotient.exact, fun h => @Quotient.sound X (operationalSetoid T r) x y h⟩

/-- Any representation preserving observation and supporting every action
must distinguish every pair distinguished by the canonical quotient. -/
theorem adequate_representation_refines_operational
    (T : A → X → X) (M : A → S → S) (s : X → S) (r : X → O) (d : S → O)
    (hstep : ∀ a x, s (T a x) = M a (s x)) (hobs : ∀ x, r x = d (s x)) :
    Sufficient s (realize T r) := by
  intro x y hxy
  apply Quotient.sound
  intro w
  rw [observable_simulation_all_words T M s r d hstep hobs,
      observable_simulation_all_words T M s r d hstep hobs, hxy]

/-- An adequate representation factors onto the canonical information space. -/
theorem canonical_factorization
    (T : A → X → X) (M : A → S → S) (s : X → S) (r : X → O) (d : S → O)
    (hstep : ∀ a x, s (T a x) = M a (s x)) (hobs : ∀ x, r x = d (s x)) :
    ∃ g : Set.range s → InfoSpace T r,
      ∀ x, g ⟨s x, Set.mem_range_self x⟩ = realize T r x :=
  (sufficient_iff_image_decoder s _).mp
    (adequate_representation_refines_operational T M s r d hstep hobs)

/-- Single-action version convenient for the Haar trajectory certificate. -/
theorem simulation_all_times (T : X → X) (M : S → S) (s : X → S)
    (hstep : ∀ x, s (T x) = M (s x)) (n : Nat) (x : X) :
    s (T^[n] x) = M^[n] (s x) :=
  (show Function.Semiconj s T M from hstep).iterate_right n x
end KomorebiInformation.Predictive
