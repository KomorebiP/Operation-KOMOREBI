module
public import CertifiedReplay

@[expose] public section
namespace Komorebi.Discovery.Certified
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {R : Type} [CommRing R] [DecidableEq R] [Fintype R] {d k o : Nat}

/-- Any total proposal function is safe: checked evidence is used, and missing or
invalid evidence falls back to the proved reference decision procedure. This does
not impose an efficiency claim on an arbitrary proposer or on the fallback. -/
def guardedOracle (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R))
    (propose : List (Test k o) → (Fin d → R) → Option (Evidence R d)) :
    SpanOracle A O where
  contains ts v :=
    match (propose ts v).bind (checkMembership A O ts v) with
    | some b => b
    | none => (enumerationOracle A O).contains ts v
  correct ts v := by
    cases hp : propose ts v with
    | none => simp only [Option.bind_none]; exact (enumerationOracle A O).correct ts v
    | some e =>
      simp only [Option.bind_some]
      cases hc : checkMembership A O ts v e with
      | none => exact (enumerationOracle A O).correct ts v
      | some b => exact checked_decision A O ts v e b hc

theorem guardedOracle_accepts_checked (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R))
    (propose : List (Test k o) → (Fin d → R) → Option (Evidence R d))
    (ts : List (Test k o)) (v : Fin d → R) (e : Evidence R d) (b : Bool)
    (hp : propose ts v = some e) (hc : checkMembership A O ts v e = some b) :
    (guardedOracle A O propose).contains ts v = b := by
  simp only [guardedOracle, hp, Option.bind_some, hc]

theorem guardedOracle_bad_falls_back (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R))
    (propose : List (Test k o) → (Fin d → R) → Option (Evidence R d))
    (ts : List (Test k o)) (v : Fin d → R)
    (h : (propose ts v).bind (checkMembership A O ts v) = none) :
    (guardedOracle A O propose).contains ts v = (enumerationOracle A O).contains ts v := by
  simp only [guardedOracle, h]

def guardedPrimeDiscover (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r)))
    (propose : List (Test k o) → (Fin d → ZMod (p^r)) →
      Option (Evidence (ZMod (p^r)) d)) : Option (List (Test k o)) :=
  discover A O (guardedOracle A O propose) (r*d)

/-- Even a proposer that is wrong on every query cannot change the result. -/
theorem guardedPrimeDiscover_eq_reference (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r)))
    (propose : List (Test k o) → (Fin d → ZMod (p^r)) →
      Option (Evidence (ZMod (p^r)) d)) :
    guardedPrimeDiscover p r d A O propose = finitePrimeDiscover p r d A O :=
  worklist_oracle_independent A O (guardedOracle A O propose) (enumerationOracle A O)
    (o + k*(r*d) + 1) [] (roots k o)

theorem guardedPrimeDiscover_total_correct (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r)))
    (propose : List (Test k o) → (Fin d → ZMod (p^r)) →
      Option (Evidence (ZMod (p^r)) d)) :
    ∃ result, guardedPrimeDiscover p r d A O propose = some result ∧
      testSpan A O result = observableSpan A O ∧ result.length ≤ r*d ∧
      (∀ t ∈ result, t.1.length < r*d) := by
  rw [guardedPrimeDiscover_eq_reference]
  exact finitePrimeDiscover_total_correct p r d hp A O

theorem guardedPrimeDiscover_defines_behavior (p r d : Nat) (hp : p.Prime)
    [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (propose : List (Test k o) → (Fin d → ZMod (p^r)) →
      Option (Evidence (ZMod (p^r)) d)) :
    ∃ result, guardedPrimeDiscover p r d (fun a => rowRight (A a)) O propose = some result ∧
      (guardedCodeFormula (V := ZMod (p^r)) result).IsQF ∧
      (∀ e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r)),
        taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
          e ∈ taggedBehaviorSet (linearSystem A O)) := by
  obtain ⟨result,hr,_,_,_,hq,hsem⟩ := prime_discovery_defines_behavior p r d hp A O
  exact ⟨result, (guardedPrimeDiscover_eq_reference p r d _ O propose).trans hr, hq, hsem⟩

end Komorebi.Discovery.Certified
