module
public import DiscoveryTrace

@[expose] public section
namespace Komorebi.Discovery.TorsionQueue
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
open scoped BigOperators
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
abbrev R := ZMod 4
def A : Fin 2 → Mat R 4 4 := ![![![3, 2, 0, 2], ![1, 2, 3, 1], ![1, 2, 1, 3], ![3, 3, 3, 0]], ![![2, 0, 0, 0], ![1, 0, 2, 1], ![2, 0, 0, 2], ![2, 3, 2, 2]]]
def O : Mat R 1 4 := ![![3, 0, 0, 0]]
def AA : Fin 2 → (Fin 4 → R) →ₗ[R] (Fin 4 → R) := fun a => rowRight (A a)
def result : List (Test 2 1) := [([], 0), ([0], 0)]
def accepted0 : List (Test 2 1) := []
def pending0 : List (Test 2 1) := [([], 0)]
def test0 : Test 2 1 := ([], 0)
def delta0 : Fin 4 → R := ![1, 0, 0, 0]
theorem branch0 : testValue AA O test0 ∉ testSpan AA O accepted0 := by
  apply span_nonmember_from_indexed_functional AA O accepted0
    (testValue AA O test0) (rowEvaluate delta0)
  · decide +kernel
  · decide +kernel
def accepted1 : List (Test 2 1) := [([], 0)]
def pending1 : List (Test 2 1) := [([0], 0), ([1], 0)]
def test1 : Test 2 1 := ([0], 0)
def delta1 : Fin 4 → R := ![0, 1, 0, 0]
theorem branch1 : testValue AA O test1 ∉ testSpan AA O accepted1 := by
  apply span_nonmember_from_indexed_functional AA O accepted1
    (testValue AA O test1) (rowEvaluate delta1)
  · decide +kernel
  · decide +kernel
def accepted2 : List (Test 2 1) := [([], 0), ([0], 0)]
def pending2 : List (Test 2 1) := [([1], 0), ([0,0], 0), ([1,0], 0)]
def test2 : Test 2 1 := ([1], 0)
theorem branch2 : testValue AA O test2 ∈ testSpan AA O accepted2 := by
  apply span_member_from_coefficients AA O accepted2 (testValue AA O test2) (![2, 0])
  decide +kernel
def accepted3 : List (Test 2 1) := [([], 0), ([0], 0)]
def pending3 : List (Test 2 1) := [([0,0], 0), ([1,0], 0)]
def test3 : Test 2 1 := ([0,0], 0)
theorem branch3 : testValue AA O test3 ∈ testSpan AA O accepted3 := by
  apply span_member_from_coefficients AA O accepted3 (testValue AA O test3) (![1, 0])
  decide +kernel
def accepted4 : List (Test 2 1) := [([], 0), ([0], 0)]
def pending4 : List (Test 2 1) := [([1,0], 0)]
def test4 : Test 2 1 := ([1,0], 0)
theorem branch4 : testValue AA O test4 ∈ testSpan AA O accepted4 := by
  apply span_member_from_coefficients AA O accepted4 (testValue AA O test4) (![1, 1])
  decide +kernel
theorem trace5 : QueueTrace AA O result [] result := QueueTrace.done result
theorem trace4 : QueueTrace AA O accepted4 pending4 result := by
  exact QueueTrace.skip branch4 trace5
theorem trace3 : QueueTrace AA O accepted3 pending3 result := by
  exact QueueTrace.skip branch3 trace4
theorem trace2 : QueueTrace AA O accepted2 pending2 result := by
  exact QueueTrace.skip branch2 trace3
theorem trace1 : QueueTrace AA O accepted1 pending1 result := by
  exact QueueTrace.accept branch1 trace2
theorem trace0 : QueueTrace AA O accepted0 pending0 result := by
  exact QueueTrace.accept branch0 trace1
theorem complete_trace : QueueTrace AA O [] (roots 2 1) result := trace0
theorem exact_observable_span : testSpan AA O result = observableSpan AA O :=
  queueTrace_exact AA O complete_trace
theorem reference_algorithm_result : finitePrimeDiscover 2 2 4 AA O = some result :=
  prime_trace_matches_reference 2 2 4 (by decide +kernel) AA O result complete_trace
theorem exact_all_words (x y : Fin 4 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  certified_code_exact _ _ (queueTrace_code A O result complete_trace) x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  queueTrace_standard_definition A O result complete_trace e
end Komorebi.Discovery.TorsionQueue
