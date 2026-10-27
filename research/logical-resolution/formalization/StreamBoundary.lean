module
public import LogicalHorizon

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation

/-- All infinite binary streams, with shift and head observation. -/
def streamSystem : System (Nat → Bool) Unit Unit Bool where
  step := fun _ s n => s (n+1)
  observe := fun _ s => s 0

theorem stream_run (word : List Unit) (s : Nat → Bool) (n : Nat) :
    run streamSystem word s n = s (n+word.length) := by
  induction word generalizing s with
  | nil => rfl
  | cons a word ih =>
    change run streamSystem word (fun k => s (k+1)) n = _
    rw [ih]
    simp only [List.length_cons]
    congr 1

theorem stream_behavior (s : Nat → Bool) (word : List Unit) (j : Unit) :
    behavior streamSystem s word j = s word.length := by
  change run streamSystem word s 0 = _
  rw [stream_run]
  simp only [Nat.zero_add]

def zeroStream : Nat → Bool := fun _ => false

def spikeStream (k : Nat) : Nat → Bool := fun n => decide (n=k)

theorem stream_finite_agreement (h : Nat) :
    AgreesTo streamSystem h zeroStream (spikeStream (h+1)) := by
  intro word hw j
  rw [stream_behavior,stream_behavior]
  have hn : word.length ≠ h+1 := by omega
  simp [zeroStream,spikeStream,hn]

theorem stream_future_separation (h : Nat) :
    ¬ ObsEq streamSystem zeroStream (spikeStream (h+1)) := by
  intro he
  have hh := he (List.replicate (h+1) ()) ()
  rw [stream_behavior,stream_behavior] at hh
  simp [zeroStream,spikeStream] at hh

theorem stream_behavior_eq_identity (x y : Nat → Bool) :
    ObsEq streamSystem x y ↔ x = y := by
  constructor
  · intro he
    funext n
    have hh := he (List.replicate n ()) ()
    simpa only [stream_behavior,List.length_replicate] using hh
  · intro h; subst y; exact obsEq_refl streamSystem x

/-- No finite observation horizon suffices, even though every unequal pair has
some finite distinguishing word. -/
theorem no_uniform_stream_horizon (h : Nat) :
    ∃ x y, Horizon streamSystem h x y ∧ ¬ ObsEq streamSystem x y := by
  exact ⟨zeroStream,spikeStream (h+1),
    (horizon_iff_agreesTo streamSystem h _ _).mpr (stream_finite_agreement h),
    stream_future_separation h⟩

def pairEnv (x y : Nat → Bool) : Fin 2 → (Nat → Bool) :=
  fun i => if i.val = 0 then x else y

/-- Full stream behavior equality is not definable by ANY one finite formula
of this observational first-order fragment, regardless of quantifier rank. -/
theorem stream_behavior_not_finitely_definable :
    ¬ ∃ f : Formula Unit Unit Bool 2, ∀ x y : Nat → Bool,
      f.Holds streamSystem (pairEnv x y) ↔ ObsEq streamSystem x y := by
  rintro ⟨f,hf⟩
  have henv : ∀ i, AgreesTo streamSystem f.depth
      (pairEnv zeroStream zeroStream i) (pairEnv zeroStream (spikeStream (f.depth+1)) i) := by
    intro i
    by_cases hi : i.val = 0
    · simpa only [pairEnv,hi,ite_true] using agreesTo_refl streamSystem f.depth zeroStream
    · simpa only [pairEnv,hi,ite_false] using stream_finite_agreement f.depth
  have hsame := formula_depth_congr streamSystem f.depth f
    (pairEnv zeroStream zeroStream)
    (pairEnv zeroStream (spikeStream (f.depth+1))) henv (Nat.le_refl _)
  have hdiag := (hf zeroStream zeroStream).mpr (obsEq_refl streamSystem zeroStream)
  exact stream_future_separation f.depth ((hf _ _).mp (hsame.mp hdiag))

end Komorebi.LogicalResolution
