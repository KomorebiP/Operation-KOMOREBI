module
public import CertifiedMembership

@[expose] public section
namespace Komorebi.Discovery.Certified
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {R : Type} [CommRing R] [DecidableEq R] {d k o : Nat}

/-- A total, proof-producing validator for untrusted event data. It reconstructs
its own FIFO queue. A short, trailing, or locally invalid trace returns none. -/
def replay (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) :
    List (Evidence R d) → List (Test k o) → List (Test k o) → Option (List (Test k o))
  | [], ts, [] => some ts
  | [], _, _ :: _ => none
  | _ :: _, _, [] => none
  | e :: es, ts, t :: pending =>
    match checkMembership A O ts (testValue A O t) e with
    | none => none
    | some true => replay A O es ts pending
    | some false => replay A O es (ts ++ [t]) (pending ++ children t)

theorem replay_sound (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (es : List (Evidence R d))
    (ts pending result : List (Test k o))
    (h : replay A O es ts pending = some result) : QueueTrace A O ts pending result := by
  induction es generalizing ts pending with
  | nil =>
    cases pending with
    | nil =>
      simp only [replay, Option.some.injEq] at h
      subst result
      exact QueueTrace.done ts
    | cons => simp only [replay] at h; cases h
  | cons e es ih =>
    cases pending with
    | nil => simp only [replay] at h; cases h
    | cons t pending =>
      cases hc : checkMembership A O ts (testValue A O t) e with
      | none => simp only [replay, hc] at h; cases h
      | some b =>
        cases b with
        | true =>
          simp only [replay, hc] at h
          exact QueueTrace.skip (checked_member A O ts _ e hc) (ih ts pending h)
        | false =>
          simp only [replay, hc] at h
          exact QueueTrace.accept (checked_nonmember A O ts _ e hc)
            (ih (ts ++ [t]) (pending ++ children t) h)

def replaySource (A : Fin k → Mat R d d) (O : Mat R o d)
    (es : List (Evidence R d)) : Option (List (Test k o)) :=
  replay (fun a => rowRight (A a)) O es [] (roots k o)

theorem replaySource_exact (A : Fin k → Mat R d d) (O : Mat R o d)
    (es : List (Evidence R d)) (result : List (Test k o))
    (h : replaySource A O es = some result) :
    testSpan (fun a => rowRight (A a)) O result =
      observableSpan (fun a => rowRight (A a)) O :=
  queueTrace_exact _ _ (replay_sound _ _ es [] (roots k o) result h)

theorem replaySource_all_words (A : Fin k → Mat R d d) (O : Mat R o d)
    (es : List (Evidence R d)) (result : List (Test k o))
    (h : replaySource A O es = some result) (x y : Fin d → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  spanning_tests_exact A O result (replaySource_exact A O es result h) x y

theorem replaySource_standard_formula (A : Fin k → Mat R d d) (O : Mat R o d)
    (es : List (Evidence R d)) (result : List (Test k o))
    (h : replaySource A O es = some result)
    (e : Fin 2 → TaggedCarrier (Fin d → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  queueTrace_standard_definition A O result
    (replay_sound _ _ es [] (roots k o) result h) e

theorem replaySource_reference (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (es : List (Evidence (ZMod (p^r)) d)) (result : List (Test k o))
    (h : replaySource A O es = some result) :
    finitePrimeDiscover p r d (fun a => rowRight (A a)) O = some result :=
  prime_trace_matches_reference p r d hp _ O result
    (replay_sound _ _ es [] (roots k o) result h)

/-- Two independently accepted trace payloads for the same source cannot disagree. -/
theorem replaySource_unique (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (es fs : List (Evidence (ZMod (p^r)) d)) (s t : List (Test k o))
    (hs : replaySource A O es = some s) (ht : replaySource A O fs = some t) : s = t := by
  have he := (replaySource_reference p r d hp A O es s hs).symm.trans
    (replaySource_reference p r d hp A O fs t ht)
  exact Option.some.inj he

end Komorebi.Discovery.Certified
