module
public import EchelonModular
public import DiscoveryLogic

@[expose] public section
namespace Komorebi.Discovery.EchelonBackend
open Komorebi.Echelon
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {d k o : Nat}

def initial (m d : Nat) [NeZero m] : Basis d :=
  diagonal (m:ℤ) (by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)) d

def StateCorrect (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (B : Basis d) (ts : List (Test k o)) : Prop :=
  ∀x, Represents B x ↔ reduce m x ∈ testSpan A O ts

theorem stateCorrect_initial (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) : StateCorrect m A O (initial m d) [] := by
  intro x
  simpa [initial,testSpan] using diagonal_kernel m x

theorem testSpan_snoc {R : Type} [CommRing R]
    (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R)) (O : Fin o → (Fin d → R))
    (ts : List (Test k o)) (t : Test k o) :
    testSpan A O (ts++[t]) = testSpan A O ts ⊔ Submodule.span R {testValue A O t} := by
  apply le_antisymm
  · apply Submodule.span_le.mpr
    rintro _ ⟨u,hu,rfl⟩
    rcases List.mem_append.mp hu with ho | hn
    · exact (show testSpan A O ts ≤ testSpan A O ts ⊔ Submodule.span R {testValue A O t} from le_sup_left) (test_mem_span A O ho)
    · have he : u=t := by simpa using hn
      subst u
      exact (show Submodule.span R {testValue A O t} ≤ testSpan A O ts ⊔ Submodule.span R {testValue A O t} from le_sup_right) (Submodule.subset_span (by simp))
  · apply sup_le (testSpan_append A O ts t)
    apply Submodule.span_le.mpr
    intro x hx
    have he : x=testValue A O t := by simpa using hx
    rw [he]
    exact test_mem_span A O (by simp)

theorem stateCorrect_insert (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (B : Basis d) (ts : List (Test k o))
    (hB : StateCorrect m A O B ts) (t : Test k o) :
    StateCorrect m A O (Komorebi.Echelon.insert B (lift m (testValue A O t))) (ts++[t]) := by
  intro x
  rw [testSpan_snoc]
  exact insert_preimage m B (testSpan A O ts) hB (testValue A O t) x

/-- Stateful FIFO algorithm: retain the integer echelon basis across every queue decision. -/
def fastWorklist (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) :
    Nat → Basis d → List (Test k o) → List (Test k o) → Option (List (Test k o))
  | 0, _, _, _ => none
  | _+1, _, ts, [] => some ts
  | fuel+1, B, ts, t::pending =>
    let v := lift m (testValue A O t)
    if (coordinates B v).isSome then
      fastWorklist m A O fuel B ts pending
    else
      fastWorklist m A O fuel (Komorebi.Echelon.insert B v) (ts++[t]) (pending++children t)

/-- Same decisions and ordered output as every exact oracle, at every fuel budget. -/
theorem fastWorklist_matches (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (oracle : SpanOracle A O)
    (fuel : Nat) (B : Basis d) (ts pending : List (Test k o))
    (hB : StateCorrect m A O B ts) :
    fastWorklist m A O fuel B ts pending = worklist A O oracle fuel ts pending := by
  induction fuel generalizing B ts pending with
  | zero => rfl
  | succ fuel ih =>
    cases pending with
    | nil => rfl
    | cons t pending =>
      have he : (coordinates B (lift m (testValue A O t))).isSome =
          oracle.contains ts (testValue A O t) := by
        apply Bool.eq_iff_iff.mpr
        rw [Option.isSome_iff_exists,coordinates_correct,hB _,reduce_lift]
        exact (oracle.correct _ _).symm
      simp only [fastWorklist,worklist,he]
      split
      · exact ih B ts pending hB
      · exact ih _ _ _ (stateCorrect_insert m A O B ts hB t)

/-- A concrete verified incremental solver with no membership enumeration or untrusted advice. -/
def fastPrimeDiscover (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) : Option (List (Test k o)) :=
  fastWorklist (p^r) A O (o+k*(r*d)+1) (initial (p^r) d) [] (roots k o)

theorem fastPrimeDiscover_eq_reference (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    fastPrimeDiscover p r d A O = finitePrimeDiscover p r d A O := by
  exact fastWorklist_matches (p^r) A O (enumerationOracle A O) _ _ _ _
    (stateCorrect_initial (p^r) A O)

theorem fastPrimeDiscover_total_correct (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    ∃ tests, fastPrimeDiscover p r d A O=some tests ∧
      testSpan A O tests=observableSpan A O ∧ tests.length≤r*d ∧
      (∀t∈tests,t.1.length<r*d) := by
  rw [fastPrimeDiscover_eq_reference]
  exact finitePrimeDiscover_total_correct p r d hp A O

/-- The verified incremental computation supplies the original-language first-order definition. -/
theorem fastPrimeDiscover_defines_behavior (p r d : Nat) (hp : p.Prime)
    [NeZero (p^r)] (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    ∃ tests, fastPrimeDiscover p r d (fun a => rowRight (A a)) O = some tests ∧
      tests.length ≤ r*d ∧ (∀t∈tests,t.1.length<r*d) ∧
      FiniteCodeCertificate (linearSystem A O) tests ∧
      (guardedCodeFormula (V := ZMod (p^r)) tests).IsQF ∧
      (∀e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r)),
        taggedRealize (linearSystem A O) (guardedCodeFormula tests) e ↔
          e ∈ taggedBehaviorSet (linearSystem A O)) := by
  rw [fastPrimeDiscover_eq_reference]
  exact prime_discovery_defines_behavior p r d hp A O

/-- A computed successful output supplies the finite logical certificate directly. -/
theorem fastPrimeDiscover_code (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (result : List (Test k o))
    (h : fastPrimeDiscover p r d (fun a => rowRight (A a)) O=some result) :
    FiniteCodeCertificate (linearSystem A O) result := by
  rw [fastPrimeDiscover_eq_reference] at h
  exact discoveredCodeCertificate A O (enumerationOracle _ O) (r*d) result h

theorem fastPrimeDiscover_standard_formula (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (result : List (Test k o))
    (h : fastPrimeDiscover p r d (fun a => rowRight (A a)) O=some result)
    (e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r))) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  guardedCodeFormula_semantics _ result (fastPrimeDiscover_code p r d A O result h) e

end Komorebi.Discovery.EchelonBackend
