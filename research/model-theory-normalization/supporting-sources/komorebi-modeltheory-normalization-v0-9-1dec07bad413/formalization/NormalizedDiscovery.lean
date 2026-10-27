module
public import EchelonCanonical
public import EchelonDiscovery

@[expose] public section
namespace Komorebi.Discovery.NormalizedBackend
open Komorebi.Echelon
open Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {d k o : Nat}

theorem stateCorrect_normalize (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (B : Basis d) (ts : List (Test k o))
    (hB : StateCorrect m A O B ts) : StateCorrect m A O (normalize B) ts := by
  intro x
  rw [represents_normalize]
  exact hB x

theorem stateCorrect_normalizedInsert (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (B : Basis d) (ts : List (Test k o))
    (hB : StateCorrect m A O B ts) (t : Test k o) :
    StateCorrect m A O (normalizedInsert B (lift m (testValue A O t))) (ts++[t]) :=
  stateCorrect_normalize m A O _ _ (stateCorrect_insert m A O B ts hB t)

theorem stateCorrect_containsModulus (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (B : Basis d) (ts : List (Test k o))
    (hB : StateCorrect m A O B ts) : ContainsModulus (m:ℤ) B := by
  intro x
  apply (hB _).mpr
  have hz : reduce m ((m:ℤ) • x)=0 := by ext i; simp [reduce]
  rw [hz]
  exact (testSpan A O ts).zero_mem

/-- The normalized cached FIFO run returns its final basis as well as the test list. -/
def normalizedRun (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) :
    Nat → Basis d → List (Test k o) → List (Test k o) → Option (Basis d × List (Test k o))
  | 0, _, _, _ => none
  | _+1, B, ts, [] => some (B,ts)
  | fuel+1, B, ts, t::pending =>
    let v := lift m (testValue A O t)
    if (coordinates B v).isSome then
      normalizedRun m A O fuel B ts pending
    else
      normalizedRun m A O fuel (normalizedInsert B v) (ts++[t]) (pending++children t)

/-- Normalizing between decisions does not alter any ordered decision result. -/
theorem normalizedRun_matches (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (oracle : SpanOracle A O)
    (fuel : Nat) (B : Basis d) (ts pending : List (Test k o))
    (hB : StateCorrect m A O B ts) :
    (normalizedRun m A O fuel B ts pending).map Prod.snd =
      worklist A O oracle fuel ts pending := by
  induction fuel generalizing B ts pending with
  | zero => rfl
  | succ fuel ih =>
    cases pending with
    | nil => rfl
    | cons t pending =>
      have he : (coordinates B (lift m (testValue A O t))).isSome =
          oracle.contains ts (testValue A O t) := by
        apply Bool.eq_iff_iff.mpr
        rw [Option.isSome_iff_exists, coordinates_correct, hB _, reduce_lift]
        exact (oracle.correct _ _).symm
      simp only [normalizedRun, worklist, he]
      split
      · exact ih B ts pending hB
      · exact ih _ _ _ (stateCorrect_normalizedInsert m A O B ts hB t)

/-- Every returned cache is reduced and is the exact modular preimage. -/
theorem normalizedRun_invariant (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (fuel : Nat)
    (B C : Basis d) (ts pending result : List (Test k o))
    (hB : StateCorrect m A O B ts) (hred : Reduced B)
    (h : normalizedRun m A O fuel B ts pending=some (C,result)) :
    StateCorrect m A O C result ∧ Reduced C := by
  induction fuel generalizing B ts pending with
  | zero => cases h
  | succ fuel ih =>
    cases pending with
    | nil =>
      simp only [normalizedRun, Option.some.injEq, Prod.mk.injEq] at h
      rcases h with ⟨rfl,rfl⟩
      exact ⟨hB,hred⟩
    | cons t pending =>
      simp only [normalizedRun] at h
      split at h
      · exact ih B ts pending hB hred h
      · exact ih _ _ _ (stateCorrect_normalizedInsert m A O B ts hB t)
          (normalize_reduced _) h

/-- A uniform stored-cache bound at every successful run boundary. -/
theorem normalizedRun_entry_bounds (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (fuel : Nat)
    (B C : Basis d) (ts pending result : List (Test k o))
    (hB : StateCorrect m A O B ts) (hred : Reduced B)
    (h : normalizedRun m A O fuel B ts pending=some (C,result)) (i j : Fin d) :
    0≤entries C i j ∧ entries C i j≤(m:ℤ) := by
  have hi := normalizedRun_invariant m A O fuel B C ts pending result hB hred h
  exact reduced_entry_bounds (m:ℤ)
    (by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)) C
    (stateCorrect_containsModulus m A O C result hi.1) hi.2 i j

/-- Cached exact discovery, with a reduced integer basis after every accepted row. -/
def normalizedPrimeDiscover (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) : Option (List (Test k o)) :=
  (normalizedRun (p^r) A O (o+k*(r*d)+1)
    (normalize (initial (p^r) d)) [] (roots k o)).map Prod.snd

theorem normalizedPrimeDiscover_eq_reference (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    normalizedPrimeDiscover p r d A O=finitePrimeDiscover p r d A O := by
  exact normalizedRun_matches (p^r) A O (enumerationOracle A O) _ _ _ _
    (stateCorrect_normalize (p^r) A O _ _ (stateCorrect_initial (p^r) A O))

theorem normalizedPrimeDiscover_eq_fast (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    normalizedPrimeDiscover p r d A O=fastPrimeDiscover p r d A O := by
  rw [normalizedPrimeDiscover_eq_reference, fastPrimeDiscover_eq_reference]

theorem normalizedPrimeDiscover_total_correct (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    ∃ tests, normalizedPrimeDiscover p r d A O=some tests ∧
      testSpan A O tests=observableSpan A O ∧ tests.length≤r*d ∧
      (∀t∈tests,t.1.length<r*d) := by
  rw [normalizedPrimeDiscover_eq_reference]
  exact finitePrimeDiscover_total_correct p r d hp A O

theorem normalizedPrimeDiscover_defines_behavior (p r d : Nat) (hp : p.Prime)
    [NeZero (p^r)] (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    ∃ tests, normalizedPrimeDiscover p r d (fun a => rowRight (A a)) O=some tests ∧
      tests.length≤r*d ∧ (∀t∈tests,t.1.length<r*d) ∧
      FiniteCodeCertificate (linearSystem A O) tests ∧
      (guardedCodeFormula (V := ZMod (p^r)) tests).IsQF ∧
      (∀e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r)),
        taggedRealize (linearSystem A O) (guardedCodeFormula tests) e ↔
          e ∈ taggedBehaviorSet (linearSystem A O)) := by
  rw [normalizedPrimeDiscover_eq_reference]
  exact prime_discovery_defines_behavior p r d hp A O

theorem normalizedPrimeDiscover_code (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (result : List (Test k o))
    (h : normalizedPrimeDiscover p r d (fun a => rowRight (A a)) O=some result) :
    FiniteCodeCertificate (linearSystem A O) result := by
  rw [normalizedPrimeDiscover_eq_fast] at h
  exact fastPrimeDiscover_code p r d A O result h

end Komorebi.Discovery.NormalizedBackend
