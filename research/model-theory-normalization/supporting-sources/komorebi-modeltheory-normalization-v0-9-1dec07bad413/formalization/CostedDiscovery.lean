module
public import CostedLattice
public import BoundedDiscovery

@[expose] public section
namespace Komorebi.Costed
open Komorebi.Echelon Komorebi.Echelon.Cost
open Komorebi.Discovery Komorebi.Discovery.BoundedBackend
open Komorebi.Discovery.EchelonBackend Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {d k o : Nat}

/-- Costed FIFO interpreter. Its value is computed through the metered subroutines.
A popped row is reconstructed, not cached. Charge one extraction per lifted entry
and one membership-result test. List allocation, traversal, proof checking and the
primitive bignum runtime are outside this explicitly arithmetic cost model. -/
def runEval (m : Nat) [NeZero m]
    (A : Fin k → Mat (ZMod m) d d) (O : Mat (ZMod m) o d) :
    Nat → Basis d → List (Test k o) → List (Test k o) →
      Eval (Option (Basis d × List (Test k o)))
  | 0,_,_,_ => (none,0)
  | _+1,B,ts,[] => (some (B,ts),0)
  | fuel+1,B,ts,t::pending =>
    let source := testEval A O t
    let v := lift m source.1
    let mem := coordinatesEval B v
    let localUnits := source.2+mem.2+d+1
    if mem.1.isSome then
      let z := runEval m A O fuel B ts pending
      (z.1,localUnits+z.2)
    else
      let next := updateEval B v
      let z := runEval m A O fuel next.1 (ts++[t]) (pending++children t)
      (z.1,localUnits+next.2+z.2)

@[simp] theorem runEval_value (m : Nat) [NeZero m]
    (A : Fin k → Mat (ZMod m) d d) (O : Mat (ZMod m) o d)
    (fuel : Nat) (B : Basis d) (ts pending : List (Test k o)) :
    (runEval m A O fuel B ts pending).1=
      boundedRun m (fun a => rowRight (A a)) O fuel B ts pending := by
  induction fuel generalizing B ts pending with
  | zero => rfl
  | succ fuel ih =>
    cases pending with
    | nil => rfl
    | cons t pending =>
      simp only [runEval,boundedRun,testEval_value,coordinatesEval_value,updateEval_value]
      split <;> exact ih _ _ _

/-- Includes arithmetic spent normalizing the actual initial diagonal cache.
The supplied modulus and matrices are treated as input; constructing p^r itself
and parsing/serialization are not charges in this evaluator. -/
def discoverEval (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    Eval (Option (List (Test k o))) :=
  let initialEval := normalizeEval (initial (p^r) d)
  let z := runEval (p^r) A O (o+k*(r*d)+1) initialEval.1 [] (roots k o)
  (z.1.map Prod.snd,initialEval.2+z.2)

@[simp] theorem discoverEval_value (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    (discoverEval p r d A O).1=
      boundedPrimeDiscover p r d (fun a => rowRight (A a)) O := by
  simp only [discoverEval,normalizeEval_value,runEval_value,boundedPrimeDiscover]

theorem discoverEval_eq_reference (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    (discoverEval p r d A O).1=finitePrimeDiscover p r d (fun a => rowRight (A a)) O := by
  rw [discoverEval_value,boundedPrimeDiscover_eq_reference]

theorem discoverEval_total_correct (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    ∃ tests, (discoverEval p r d A O).1=some tests ∧
      testSpan (fun a => rowRight (A a)) O tests=observableSpan (fun a => rowRight (A a)) O ∧
      tests.length≤r*d ∧ (∀t∈tests,t.1.length<r*d) := by
  simp only [discoverEval_value]
  exact boundedPrimeDiscover_total_correct p r d hp _ O

theorem discoverEval_defines_behavior (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    ∃ tests, (discoverEval p r d A O).1=some tests ∧
      tests.length≤r*d ∧ (∀t∈tests,t.1.length<r*d) ∧
      FiniteCodeCertificate (linearSystem A O) tests ∧
      (guardedCodeFormula (V := ZMod (p^r)) tests).IsQF ∧
      (∀e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r)),
        taggedRealize (linearSystem A O) (guardedCodeFormula tests) e ↔
          e ∈ taggedBehaviorSet (linearSystem A O)) := by
  simp only [discoverEval_value]
  exact boundedPrimeDiscover_defines_behavior p r d hp A O

/-- A computed successful answer yields the inherited local logical certificate. -/
theorem discoverEval_code (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (tests : List (Test k o)) (h : (discoverEval p r d A O).1=some tests) :
    FiniteCodeCertificate (linearSystem A O) tests := by
  rw [discoverEval_value] at h
  exact boundedPrimeDiscover_code p r d A O tests h

end Komorebi.Costed
