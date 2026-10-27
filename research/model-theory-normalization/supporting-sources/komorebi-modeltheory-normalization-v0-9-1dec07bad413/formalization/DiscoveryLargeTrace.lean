module
public import DiscoveryTrace

@[expose] public section
namespace Komorebi.Discovery.LargeQueue
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
open scoped BigOperators
set_option maxRecDepth 100000
set_option maxHeartbeats 4000000
abbrev R := ZMod 65536
def A : Fin 2 → Mat R 8 8 := ![![![17698, 7962, 49699, 37320, 23412, 6538, 39824, 34395], ![23464, 37603, 20556, 32118, 60325, 50701, 6345, 63146], ![7061, 60025, 48800, 57289, 7901, 57423, 17450, 21611], ![57954, 1463, 43061, 61981, 12327, 24535, 55220, 20222], ![9538, 34330, 18991, 25859, 64489, 51532, 7482, 17514], ![8262, 4689, 20524, 11331, 58729, 9597, 8879, 16991], ![38245, 65480, 12079, 48575, 41217, 13059, 11905, 14025], ![40555, 32470, 51819, 35275, 34452, 61245, 54300, 32399]], ![![45667, 60993, 42044, 24680, 13027, 39737, 34859, 3988], ![10393, 29683, 38554, 51204, 39690, 4755, 35121, 61378], ![63427, 47581, 32082, 32486, 44031, 34935, 29965, 8363], ![27479, 23039, 1777, 57316, 32532, 42871, 30241, 7992], ![35244, 37369, 1342, 167, 21177, 50423, 62217, 51013], ![29874, 59333, 42924, 46108, 58455, 35340, 60778, 27268], ![52594, 11868, 27092, 9501, 44582, 25499, 5486, 41184], ![1304, 20195, 44643, 12867, 63107, 13759, 28318, 26332]]]
def O : Mat R 1 8 := ![![7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995]]
def AA : Fin 2 → (Fin 8 → R) →ₗ[R] (Fin 8 → R) := fun a => rowRight (A a)
def result : List (Test 2 1) := [([], 0), ([0], 0)]
def accepted0 : List (Test 2 1) := []
def pending0 : List (Test 2 1) := [([], 0)]
def test0 : Test 2 1 := ([], 0)
def delta0 : Fin 8 → R := ![1, 0, 0, 0, 0, 0, 0, 0]
theorem branch0 : testValue AA O test0 ∉ testSpan AA O accepted0 := by
  apply span_nonmember_from_indexed_functional AA O accepted0
    (testValue AA O test0) (rowEvaluate delta0)
  · decide +kernel
  · decide +kernel
def accepted1 : List (Test 2 1) := [([], 0)]
def pending1 : List (Test 2 1) := [([0], 0), ([1], 0)]
def test1 : Test 2 1 := ([0], 0)
def delta1 : Fin 8 → R := ![1, 62136, 0, 0, 0, 0, 0, 0]
theorem branch1 : testValue AA O test1 ∉ testSpan AA O accepted1 := by
  apply span_nonmember_from_indexed_functional AA O accepted1
    (testValue AA O test1) (rowEvaluate delta1)
  · decide +kernel
  · decide +kernel
def accepted2 : List (Test 2 1) := [([], 0), ([0], 0)]
def pending2 : List (Test 2 1) := [([1], 0), ([0,0], 0), ([1,0], 0)]
def test2 : Test 2 1 := ([1], 0)
theorem branch2 : testValue AA O test2 ∈ testSpan AA O accepted2 := by
  apply span_member_from_coefficients AA O accepted2 (testValue AA O test2) (![3, 0])
  decide +kernel
def accepted3 : List (Test 2 1) := [([], 0), ([0], 0)]
def pending3 : List (Test 2 1) := [([0,0], 0), ([1,0], 0)]
def test3 : Test 2 1 := ([0,0], 0)
theorem branch3 : testValue AA O test3 ∈ testSpan AA O accepted3 := by
  apply span_member_from_coefficients AA O accepted3 (testValue AA O test3) (![49151, 16386])
  decide +kernel
def accepted4 : List (Test 2 1) := [([], 0), ([0], 0)]
def pending4 : List (Test 2 1) := [([1,0], 0)]
def test4 : Test 2 1 := ([1,0], 0)
theorem branch4 : testValue AA O test4 ∈ testSpan AA O accepted4 := by
  apply span_member_from_coefficients AA O accepted4 (testValue AA O test4) (![32766, 32773])
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
theorem reference_algorithm_result : finitePrimeDiscover 2 16 8 AA O = some result :=
  prime_trace_matches_reference 2 16 8 (by decide +kernel) AA O result complete_trace
theorem exact_all_words (x y : Fin 8 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  certified_code_exact _ _ (queueTrace_code A O result complete_trace) x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 8 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  queueTrace_standard_definition A O result complete_trace e
end Komorebi.Discovery.LargeQueue
