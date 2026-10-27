module
public import DiscoveryTrace

@[expose] public section
namespace Komorebi.Discovery.DelayQueue
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
open scoped BigOperators
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
abbrev R := ZMod 16
def A : Fin 1 → Mat R 8 8 := ![![![0, 1, 0, 0, 0, 0, 0, 0], ![0, 0, 1, 0, 0, 0, 0, 0], ![0, 0, 0, 1, 0, 0, 0, 0], ![0, 0, 0, 0, 1, 0, 0, 0], ![0, 0, 0, 0, 0, 1, 0, 0], ![0, 0, 0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 0, 0, 0, 1], ![0, 0, 0, 0, 0, 0, 0, 0]]]
def O : Mat R 1 8 := ![![1, 0, 0, 0, 0, 0, 0, 0]]
def AA : Fin 1 → (Fin 8 → R) →ₗ[R] (Fin 8 → R) := fun a => rowRight (A a)
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0), ([0,0,0,0,0,0], 0), ([0,0,0,0,0,0,0], 0)]
def accepted0 : List (Test 1 1) := []
def pending0 : List (Test 1 1) := [([], 0)]
def test0 : Test 1 1 := ([], 0)
def delta0 : Fin 8 → R := ![1, 0, 0, 0, 0, 0, 0, 0]
theorem branch0 : testValue AA O test0 ∉ testSpan AA O accepted0 := by
  apply span_nonmember_from_indexed_functional AA O accepted0
    (testValue AA O test0) (rowEvaluate delta0)
  · decide +kernel
  · decide +kernel
def accepted1 : List (Test 1 1) := [([], 0)]
def pending1 : List (Test 1 1) := [([0], 0)]
def test1 : Test 1 1 := ([0], 0)
def delta1 : Fin 8 → R := ![0, 1, 0, 0, 0, 0, 0, 0]
theorem branch1 : testValue AA O test1 ∉ testSpan AA O accepted1 := by
  apply span_nonmember_from_indexed_functional AA O accepted1
    (testValue AA O test1) (rowEvaluate delta1)
  · decide +kernel
  · decide +kernel
def accepted2 : List (Test 1 1) := [([], 0), ([0], 0)]
def pending2 : List (Test 1 1) := [([0,0], 0)]
def test2 : Test 1 1 := ([0,0], 0)
def delta2 : Fin 8 → R := ![0, 0, 1, 0, 0, 0, 0, 0]
theorem branch2 : testValue AA O test2 ∉ testSpan AA O accepted2 := by
  apply span_nonmember_from_indexed_functional AA O accepted2
    (testValue AA O test2) (rowEvaluate delta2)
  · decide +kernel
  · decide +kernel
def accepted3 : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
def pending3 : List (Test 1 1) := [([0,0,0], 0)]
def test3 : Test 1 1 := ([0,0,0], 0)
def delta3 : Fin 8 → R := ![0, 0, 0, 1, 0, 0, 0, 0]
theorem branch3 : testValue AA O test3 ∉ testSpan AA O accepted3 := by
  apply span_nonmember_from_indexed_functional AA O accepted3
    (testValue AA O test3) (rowEvaluate delta3)
  · decide +kernel
  · decide +kernel
def accepted4 : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
def pending4 : List (Test 1 1) := [([0,0,0,0], 0)]
def test4 : Test 1 1 := ([0,0,0,0], 0)
def delta4 : Fin 8 → R := ![0, 0, 0, 0, 1, 0, 0, 0]
theorem branch4 : testValue AA O test4 ∉ testSpan AA O accepted4 := by
  apply span_nonmember_from_indexed_functional AA O accepted4
    (testValue AA O test4) (rowEvaluate delta4)
  · decide +kernel
  · decide +kernel
def accepted5 : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
def pending5 : List (Test 1 1) := [([0,0,0,0,0], 0)]
def test5 : Test 1 1 := ([0,0,0,0,0], 0)
def delta5 : Fin 8 → R := ![0, 0, 0, 0, 0, 1, 0, 0]
theorem branch5 : testValue AA O test5 ∉ testSpan AA O accepted5 := by
  apply span_nonmember_from_indexed_functional AA O accepted5
    (testValue AA O test5) (rowEvaluate delta5)
  · decide +kernel
  · decide +kernel
def accepted6 : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0)]
def pending6 : List (Test 1 1) := [([0,0,0,0,0,0], 0)]
def test6 : Test 1 1 := ([0,0,0,0,0,0], 0)
def delta6 : Fin 8 → R := ![0, 0, 0, 0, 0, 0, 1, 0]
theorem branch6 : testValue AA O test6 ∉ testSpan AA O accepted6 := by
  apply span_nonmember_from_indexed_functional AA O accepted6
    (testValue AA O test6) (rowEvaluate delta6)
  · decide +kernel
  · decide +kernel
def accepted7 : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0), ([0,0,0,0,0,0], 0)]
def pending7 : List (Test 1 1) := [([0,0,0,0,0,0,0], 0)]
def test7 : Test 1 1 := ([0,0,0,0,0,0,0], 0)
def delta7 : Fin 8 → R := ![0, 0, 0, 0, 0, 0, 0, 1]
theorem branch7 : testValue AA O test7 ∉ testSpan AA O accepted7 := by
  apply span_nonmember_from_indexed_functional AA O accepted7
    (testValue AA O test7) (rowEvaluate delta7)
  · decide +kernel
  · decide +kernel
def accepted8 : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0), ([0,0,0,0,0,0], 0), ([0,0,0,0,0,0,0], 0)]
def pending8 : List (Test 1 1) := [([0,0,0,0,0,0,0,0], 0)]
def test8 : Test 1 1 := ([0,0,0,0,0,0,0,0], 0)
theorem branch8 : testValue AA O test8 ∈ testSpan AA O accepted8 := by
  apply span_member_from_coefficients AA O accepted8 (testValue AA O test8) (![0, 0, 0, 0, 0, 0, 0, 0])
  decide +kernel
theorem trace9 : QueueTrace AA O result [] result := QueueTrace.done result
theorem trace8 : QueueTrace AA O accepted8 pending8 result := by
  exact QueueTrace.skip branch8 trace9
theorem trace7 : QueueTrace AA O accepted7 pending7 result := by
  exact QueueTrace.accept branch7 trace8
theorem trace6 : QueueTrace AA O accepted6 pending6 result := by
  exact QueueTrace.accept branch6 trace7
theorem trace5 : QueueTrace AA O accepted5 pending5 result := by
  exact QueueTrace.accept branch5 trace6
theorem trace4 : QueueTrace AA O accepted4 pending4 result := by
  exact QueueTrace.accept branch4 trace5
theorem trace3 : QueueTrace AA O accepted3 pending3 result := by
  exact QueueTrace.accept branch3 trace4
theorem trace2 : QueueTrace AA O accepted2 pending2 result := by
  exact QueueTrace.accept branch2 trace3
theorem trace1 : QueueTrace AA O accepted1 pending1 result := by
  exact QueueTrace.accept branch1 trace2
theorem trace0 : QueueTrace AA O accepted0 pending0 result := by
  exact QueueTrace.accept branch0 trace1
theorem complete_trace : QueueTrace AA O [] (roots 1 1) result := trace0
theorem exact_observable_span : testSpan AA O result = observableSpan AA O :=
  queueTrace_exact AA O complete_trace
theorem reference_algorithm_result : finitePrimeDiscover 2 4 8 AA O = some result :=
  prime_trace_matches_reference 2 4 8 (by decide +kernel) AA O result complete_trace
theorem exact_all_words (x y : Fin 8 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  certified_code_exact _ _ (queueTrace_code A O result complete_trace) x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 8 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  queueTrace_standard_definition A O result complete_trace e
end Komorebi.Discovery.DelayQueue
