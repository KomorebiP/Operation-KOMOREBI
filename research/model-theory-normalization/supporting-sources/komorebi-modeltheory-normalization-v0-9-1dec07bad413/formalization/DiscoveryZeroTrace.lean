module
public import DiscoveryTrace

@[expose] public section
namespace Komorebi.Discovery.ZeroQueue
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
open scoped BigOperators
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
abbrev R := ZMod 2
def A : Fin 1 → Mat R 1 1 := ![![![1]]]
def O : Mat R 1 1 := ![![0]]
def AA : Fin 1 → (Fin 1 → R) →ₗ[R] (Fin 1 → R) := fun a => rowRight (A a)
def result : List (Test 1 1) := []
def accepted0 : List (Test 1 1) := []
def pending0 : List (Test 1 1) := [([], 0)]
def test0 : Test 1 1 := ([], 0)
theorem branch0 : testValue AA O test0 ∈ testSpan AA O accepted0 := by
  apply span_member_from_coefficients AA O accepted0 (testValue AA O test0) (Fin.elim0)
  decide +kernel
theorem trace1 : QueueTrace AA O result [] result := QueueTrace.done result
theorem trace0 : QueueTrace AA O accepted0 pending0 result := by
  exact QueueTrace.skip branch0 trace1
theorem complete_trace : QueueTrace AA O [] (roots 1 1) result := trace0
theorem exact_observable_span : testSpan AA O result = observableSpan AA O :=
  queueTrace_exact AA O complete_trace
theorem reference_algorithm_result : finitePrimeDiscover 2 1 1 AA O = some result :=
  prime_trace_matches_reference 2 1 1 (by decide +kernel) AA O result complete_trace
theorem exact_all_words (x y : Fin 1 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  certified_code_exact _ _ (queueTrace_code A O result complete_trace) x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  queueTrace_standard_definition A O result complete_trace e
end Komorebi.Discovery.ZeroQueue
