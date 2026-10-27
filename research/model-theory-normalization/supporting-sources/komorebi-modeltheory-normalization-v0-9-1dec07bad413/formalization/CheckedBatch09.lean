module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch09
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c108_R := ZMod 32
def c108_A : Fin 1 → Mat c108_R 6 6 := ![![![2, 29, 20, 13, 9, 8], ![29, 13, 18, 27, 27, 26], ![18, 28, 13, 11, 16, 31], ![5, 27, 2, 29, 9, 26], ![5, 8, 8, 4, 5, 6], ![7, 10, 26, 15, 8, 3]]]
def c108_O : Mat c108_R 2 6 := ![![31, 20, 26, 31, 24, 4], ![5, 27, 25, 8, 27, 1]]
def c108_evidence : List (Evidence c108_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![20, 1, 0, 0, 0, 0]),
  .separation (![22, 27, 1, 0, 0, 0]),
  .separation (![16, 5, 1, 14, 0, 0]),
  .separation (![2, 26, 5, 0, 1, 0]),
  .separation (![26, 3, 7, 4, 7, 1]),
  .combination [8, 15, 1, 16, 12, 25],
  .combination [4, 1, 15, 11, 26, 21]]
def c108_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem c108_checked_data : replaySource c108_A c108_O c108_evidence = some c108_result := by decide +kernel
theorem c108_reference_result :
    finitePrimeDiscover 2 5 6 (fun a => rowRight (c108_A a)) c108_O = some c108_result :=
  replaySource_reference 2 5 6 (by decide +kernel) c108_A c108_O c108_evidence c108_result c108_checked_data
theorem c108_all_words (x y : Fin 6 → c108_R) :
    CodeEqual (linearSystem c108_A c108_O) c108_result x y ↔ ObsEq (linearSystem c108_A c108_O) x y :=
  replaySource_all_words c108_A c108_O c108_evidence c108_result c108_checked_data x y
theorem c108_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c108_R) c108_R) :
    taggedRealize (linearSystem c108_A c108_O) (guardedCodeFormula c108_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c108_A c108_O) :=
  replaySource_standard_formula c108_A c108_O c108_evidence c108_result c108_checked_data e
abbrev c109_R := ZMod 243
def c109_A : Fin 2 → Mat c109_R 6 6 := ![![![224, 222, 200, 133, 150, 117], ![211, 27, 21, 16, 33, 38], ![49, 200, 26, 194, 114, 187], ![70, 139, 218, 132, 171, 192], ![238, 0, 168, 230, 229, 236], ![23, 70, 137, 144, 48, 203]], ![![90, 175, 5, 73, 67, 160], ![74, 133, 78, 68, 78, 162], ![63, 229, 178, 221, 54, 180], ![195, 221, 39, 206, 141, 168], ![64, 86, 71, 3, 86, 88], ![87, 215, 112, 35, 116, 178]]]
def c109_O : Mat c109_R 1 6 := ![![179, 134, 33, 180, 172, 25]]
def c109_evidence : List (Evidence c109_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![116, 1, 0, 0, 0, 0]),
  .separation (![24, 198, 1, 0, 0, 0]),
  .separation (![108, 24, 217, 1, 0, 0]),
  .separation (![50, 56, 91, 165, 1, 0]),
  .separation (![162, 162, 81, 0, 81, 0]),
  .separation (![27, 225, 18, 99, 81, 9]),
  .combination [97, 71, 232, 20, 0, 31, 236],
  .combination [239, 235, 209, 240, 0, 72, 60],
  .combination [154, 203, 154, 31, 0, 163, 200],
  .combination [106, 134, 123, 37, 0, 188, 185],
  .combination [218, 129, 8, 148, 0, 3, 36],
  .separation (![0, 81, 162, 162, 0, 81]),
  .combination [92, 234, 97, 71, 0, 38, 0, 105],
  .combination [213, 146, 46, 23, 0, 218, 0, 188],
  .combination [211, 70, 202, 235, 0, 223, 0, 25],
  .combination [16, 116, 200, 236, 0, 162, 0, 22]]
def c109_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0), ([1,1], 0), ([1,0,1], 0)]
theorem c109_checked_data : replaySource c109_A c109_O c109_evidence = some c109_result := by decide +kernel
theorem c109_reference_result :
    finitePrimeDiscover 3 5 6 (fun a => rowRight (c109_A a)) c109_O = some c109_result :=
  replaySource_reference 3 5 6 (by decide +kernel) c109_A c109_O c109_evidence c109_result c109_checked_data
theorem c109_all_words (x y : Fin 6 → c109_R) :
    CodeEqual (linearSystem c109_A c109_O) c109_result x y ↔ ObsEq (linearSystem c109_A c109_O) x y :=
  replaySource_all_words c109_A c109_O c109_evidence c109_result c109_checked_data x y
theorem c109_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c109_R) c109_R) :
    taggedRealize (linearSystem c109_A c109_O) (guardedCodeFormula c109_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c109_A c109_O) :=
  replaySource_standard_formula c109_A c109_O c109_evidence c109_result c109_checked_data e
abbrev c110_R := ZMod 3125
def c110_A : Fin 3 → Mat c110_R 6 6 := ![![![724, 1560, 885, 2546, 1128, 729], ![73, 2514, 710, 2659, 160, 1800], ![1038, 2447, 616, 2163, 2311, 2969], ![2970, 263, 1847, 961, 745, 1890], ![2447, 1128, 1684, 1877, 612, 2102], ![790, 470, 1208, 114, 2390, 1720]], ![![2979, 2844, 2145, 2544, 2434, 782], ![2981, 1543, 154, 1441, 1023, 43], ![2014, 2649, 2887, 1530, 1998, 405], ![188, 1504, 1199, 381, 945, 1093], ![1804, 2691, 2080, 478, 1283, 777], ![2434, 940, 2908, 2156, 277, 2431]], ![![2327, 1915, 1476, 2667, 62, 2263], ![995, 76, 1216, 1433, 2644, 551], ![2062, 772, 15, 1719, 3080, 3121], ![663, 2382, 1743, 773, 2452, 1376], ![959, 144, 2650, 886, 2594, 1100], ![1779, 1359, 651, 244, 1473, 2482]]]
def c110_O : Mat c110_R 2 6 := ![![1423, 806, 1109, 737, 2988, 2679], ![1430, 2147, 226, 542, 925, 1357]]
def c110_evidence : List (Evidence c110_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![353, 1, 0, 0, 0, 0]),
  .separation (![958, 2072, 1, 0, 0, 0]),
  .separation (![1993, 1419, 0, 1, 770, 0]),
  .separation (![2788, 272, 1, 0, 2870, 2475]),
  .separation (![2033, 982, 1, 2890, 2495, 2050]),
  .combination [1785, 716, 1446, 2236, 309, 2613],
  .combination [313, 1206, 1523, 2899, 1052, 2685],
  .separation (![1875, 1250, 625, 0, 0, 0]),
  .combination [416, 437, 1346, 2674, 2713, 0, 378],
  .combination [1910, 2227, 3005, 1866, 2964, 0, 1433],
  .combination [3094, 1129, 1583, 1740, 2459, 0, 2907],
  .combination [1750, 1549, 2974, 2439, 1019, 0, 693],
  .combination [1794, 1626, 402, 2639, 2475, 0, 2855],
  .combination [1953, 119, 2214, 1171, 2351, 0, 1283],
  .combination [1463, 738, 2150, 3095, 1992, 0, 696],
  .combination [613, 1202, 400, 435, 2292, 0, 2711],
  .combination [1377, 2084, 884, 82, 1390, 0, 2870],
  .combination [2391, 808, 1297, 2077, 3003, 0, 150],
  .combination [2885, 1029, 801, 832, 2830, 0, 1867],
  .combination [596, 497, 810, 2836, 2777, 0, 313],
  .combination [288, 2687, 476, 3123, 820, 0, 52],
  .combination [710, 168, 2732, 1721, 739, 0, 2920]]
def c110_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([0,0], 0)]
theorem c110_checked_data : replaySource c110_A c110_O c110_evidence = some c110_result := by decide +kernel
theorem c110_reference_result :
    finitePrimeDiscover 5 5 6 (fun a => rowRight (c110_A a)) c110_O = some c110_result :=
  replaySource_reference 5 5 6 (by decide +kernel) c110_A c110_O c110_evidence c110_result c110_checked_data
theorem c110_all_words (x y : Fin 6 → c110_R) :
    CodeEqual (linearSystem c110_A c110_O) c110_result x y ↔ ObsEq (linearSystem c110_A c110_O) x y :=
  replaySource_all_words c110_A c110_O c110_evidence c110_result c110_checked_data x y
theorem c110_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c110_R) c110_R) :
    taggedRealize (linearSystem c110_A c110_O) (guardedCodeFormula c110_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c110_A c110_O) :=
  replaySource_standard_formula c110_A c110_O c110_evidence c110_result c110_checked_data e
abbrev c111_R := ZMod 2
def c111_A : Fin 1 → Mat c111_R 1 1 := ![![![1]]]
def c111_O : Mat c111_R 1 1 := ![![0]]
def c111_evidence : List (Evidence c111_R 1) := [
  .combination []]
def c111_result : List (Test 1 1) := []
theorem c111_checked_data : replaySource c111_A c111_O c111_evidence = some c111_result := by decide +kernel
theorem c111_reference_result :
    finitePrimeDiscover 2 1 1 (fun a => rowRight (c111_A a)) c111_O = some c111_result :=
  replaySource_reference 2 1 1 (by decide +kernel) c111_A c111_O c111_evidence c111_result c111_checked_data
theorem c111_all_words (x y : Fin 1 → c111_R) :
    CodeEqual (linearSystem c111_A c111_O) c111_result x y ↔ ObsEq (linearSystem c111_A c111_O) x y :=
  replaySource_all_words c111_A c111_O c111_evidence c111_result c111_checked_data x y
theorem c111_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c111_R) c111_R) :
    taggedRealize (linearSystem c111_A c111_O) (guardedCodeFormula c111_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c111_A c111_O) :=
  replaySource_standard_formula c111_A c111_O c111_evidence c111_result c111_checked_data e
abbrev c112_R := ZMod 3
def c112_A : Fin 2 → Mat c112_R 1 1 := ![![![1]], ![![0]]]
def c112_O : Mat c112_R 2 1 := ![![0], ![0]]
def c112_evidence : List (Evidence c112_R 1) := [
  .combination [],
  .combination []]
def c112_result : List (Test 2 2) := []
theorem c112_checked_data : replaySource c112_A c112_O c112_evidence = some c112_result := by decide +kernel
theorem c112_reference_result :
    finitePrimeDiscover 3 1 1 (fun a => rowRight (c112_A a)) c112_O = some c112_result :=
  replaySource_reference 3 1 1 (by decide +kernel) c112_A c112_O c112_evidence c112_result c112_checked_data
theorem c112_all_words (x y : Fin 1 → c112_R) :
    CodeEqual (linearSystem c112_A c112_O) c112_result x y ↔ ObsEq (linearSystem c112_A c112_O) x y :=
  replaySource_all_words c112_A c112_O c112_evidence c112_result c112_checked_data x y
theorem c112_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c112_R) c112_R) :
    taggedRealize (linearSystem c112_A c112_O) (guardedCodeFormula c112_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c112_A c112_O) :=
  replaySource_standard_formula c112_A c112_O c112_evidence c112_result c112_checked_data e
abbrev c113_R := ZMod 5
def c113_A : Fin 3 → Mat c113_R 1 1 := ![![![4]], ![![4]], ![![4]]]
def c113_O : Mat c113_R 1 1 := ![![0]]
def c113_evidence : List (Evidence c113_R 1) := [
  .combination []]
def c113_result : List (Test 3 1) := []
theorem c113_checked_data : replaySource c113_A c113_O c113_evidence = some c113_result := by decide +kernel
theorem c113_reference_result :
    finitePrimeDiscover 5 1 1 (fun a => rowRight (c113_A a)) c113_O = some c113_result :=
  replaySource_reference 5 1 1 (by decide +kernel) c113_A c113_O c113_evidence c113_result c113_checked_data
theorem c113_all_words (x y : Fin 1 → c113_R) :
    CodeEqual (linearSystem c113_A c113_O) c113_result x y ↔ ObsEq (linearSystem c113_A c113_O) x y :=
  replaySource_all_words c113_A c113_O c113_evidence c113_result c113_checked_data x y
theorem c113_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c113_R) c113_R) :
    taggedRealize (linearSystem c113_A c113_O) (guardedCodeFormula c113_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c113_A c113_O) :=
  replaySource_standard_formula c113_A c113_O c113_evidence c113_result c113_checked_data e
abbrev c114_R := ZMod 4
def c114_A : Fin 1 → Mat c114_R 1 1 := ![![![3]]]
def c114_O : Mat c114_R 2 1 := ![![2], ![1]]
def c114_evidence : List (Evidence c114_R 1) := [
  .separation (![1]),
  .separation (![2]),
  .combination [0, 2],
  .combination [0, 3]]
def c114_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c114_checked_data : replaySource c114_A c114_O c114_evidence = some c114_result := by decide +kernel
theorem c114_reference_result :
    finitePrimeDiscover 2 2 1 (fun a => rowRight (c114_A a)) c114_O = some c114_result :=
  replaySource_reference 2 2 1 (by decide +kernel) c114_A c114_O c114_evidence c114_result c114_checked_data
theorem c114_all_words (x y : Fin 1 → c114_R) :
    CodeEqual (linearSystem c114_A c114_O) c114_result x y ↔ ObsEq (linearSystem c114_A c114_O) x y :=
  replaySource_all_words c114_A c114_O c114_evidence c114_result c114_checked_data x y
theorem c114_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c114_R) c114_R) :
    taggedRealize (linearSystem c114_A c114_O) (guardedCodeFormula c114_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c114_A c114_O) :=
  replaySource_standard_formula c114_A c114_O c114_evidence c114_result c114_checked_data e
abbrev c115_R := ZMod 9
def c115_A : Fin 2 → Mat c115_R 1 1 := ![![![0]], ![![1]]]
def c115_O : Mat c115_R 1 1 := ![![2]]
def c115_evidence : List (Evidence c115_R 1) := [
  .separation (![1]),
  .combination [0],
  .combination [1]]
def c115_result : List (Test 2 1) := [([], 0)]
theorem c115_checked_data : replaySource c115_A c115_O c115_evidence = some c115_result := by decide +kernel
theorem c115_reference_result :
    finitePrimeDiscover 3 2 1 (fun a => rowRight (c115_A a)) c115_O = some c115_result :=
  replaySource_reference 3 2 1 (by decide +kernel) c115_A c115_O c115_evidence c115_result c115_checked_data
theorem c115_all_words (x y : Fin 1 → c115_R) :
    CodeEqual (linearSystem c115_A c115_O) c115_result x y ↔ ObsEq (linearSystem c115_A c115_O) x y :=
  replaySource_all_words c115_A c115_O c115_evidence c115_result c115_checked_data x y
theorem c115_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c115_R) c115_R) :
    taggedRealize (linearSystem c115_A c115_O) (guardedCodeFormula c115_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c115_A c115_O) :=
  replaySource_standard_formula c115_A c115_O c115_evidence c115_result c115_checked_data e
abbrev c116_R := ZMod 25
def c116_A : Fin 3 → Mat c116_R 1 1 := ![![![1]], ![![10]], ![![16]]]
def c116_O : Mat c116_R 2 1 := ![![12], ![1]]
def c116_evidence : List (Evidence c116_R 1) := [
  .separation (![1]),
  .combination [23],
  .combination [1],
  .combination [10],
  .combination [16]]
def c116_result : List (Test 3 2) := [([], 0)]
theorem c116_checked_data : replaySource c116_A c116_O c116_evidence = some c116_result := by decide +kernel
theorem c116_reference_result :
    finitePrimeDiscover 5 2 1 (fun a => rowRight (c116_A a)) c116_O = some c116_result :=
  replaySource_reference 5 2 1 (by decide +kernel) c116_A c116_O c116_evidence c116_result c116_checked_data
theorem c116_all_words (x y : Fin 1 → c116_R) :
    CodeEqual (linearSystem c116_A c116_O) c116_result x y ↔ ObsEq (linearSystem c116_A c116_O) x y :=
  replaySource_all_words c116_A c116_O c116_evidence c116_result c116_checked_data x y
theorem c116_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c116_R) c116_R) :
    taggedRealize (linearSystem c116_A c116_O) (guardedCodeFormula c116_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c116_A c116_O) :=
  replaySource_standard_formula c116_A c116_O c116_evidence c116_result c116_checked_data e
abbrev c117_R := ZMod 8
def c117_A : Fin 1 → Mat c117_R 1 1 := ![![![2]]]
def c117_O : Mat c117_R 1 1 := ![![5]]
def c117_evidence : List (Evidence c117_R 1) := [
  .separation (![1]),
  .combination [2]]
def c117_result : List (Test 1 1) := [([], 0)]
theorem c117_checked_data : replaySource c117_A c117_O c117_evidence = some c117_result := by decide +kernel
theorem c117_reference_result :
    finitePrimeDiscover 2 3 1 (fun a => rowRight (c117_A a)) c117_O = some c117_result :=
  replaySource_reference 2 3 1 (by decide +kernel) c117_A c117_O c117_evidence c117_result c117_checked_data
theorem c117_all_words (x y : Fin 1 → c117_R) :
    CodeEqual (linearSystem c117_A c117_O) c117_result x y ↔ ObsEq (linearSystem c117_A c117_O) x y :=
  replaySource_all_words c117_A c117_O c117_evidence c117_result c117_checked_data x y
theorem c117_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c117_R) c117_R) :
    taggedRealize (linearSystem c117_A c117_O) (guardedCodeFormula c117_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c117_A c117_O) :=
  replaySource_standard_formula c117_A c117_O c117_evidence c117_result c117_checked_data e
abbrev c118_R := ZMod 27
def c118_A : Fin 2 → Mat c118_R 1 1 := ![![![13]], ![![25]]]
def c118_O : Mat c118_R 2 1 := ![![20], ![11]]
def c118_evidence : List (Evidence c118_R 1) := [
  .separation (![1]),
  .combination [10],
  .combination [13],
  .combination [25]]
def c118_result : List (Test 2 2) := [([], 0)]
theorem c118_checked_data : replaySource c118_A c118_O c118_evidence = some c118_result := by decide +kernel
theorem c118_reference_result :
    finitePrimeDiscover 3 3 1 (fun a => rowRight (c118_A a)) c118_O = some c118_result :=
  replaySource_reference 3 3 1 (by decide +kernel) c118_A c118_O c118_evidence c118_result c118_checked_data
theorem c118_all_words (x y : Fin 1 → c118_R) :
    CodeEqual (linearSystem c118_A c118_O) c118_result x y ↔ ObsEq (linearSystem c118_A c118_O) x y :=
  replaySource_all_words c118_A c118_O c118_evidence c118_result c118_checked_data x y
theorem c118_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c118_R) c118_R) :
    taggedRealize (linearSystem c118_A c118_O) (guardedCodeFormula c118_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c118_A c118_O) :=
  replaySource_standard_formula c118_A c118_O c118_evidence c118_result c118_checked_data e
abbrev c119_R := ZMod 125
def c119_A : Fin 3 → Mat c119_R 1 1 := ![![![60]], ![![100]], ![![84]]]
def c119_O : Mat c119_R 1 1 := ![![75]]
def c119_evidence : List (Evidence c119_R 1) := [
  .separation (![1]),
  .combination [0],
  .combination [0],
  .combination [84]]
def c119_result : List (Test 3 1) := [([], 0)]
theorem c119_checked_data : replaySource c119_A c119_O c119_evidence = some c119_result := by decide +kernel
theorem c119_reference_result :
    finitePrimeDiscover 5 3 1 (fun a => rowRight (c119_A a)) c119_O = some c119_result :=
  replaySource_reference 5 3 1 (by decide +kernel) c119_A c119_O c119_evidence c119_result c119_checked_data
theorem c119_all_words (x y : Fin 1 → c119_R) :
    CodeEqual (linearSystem c119_A c119_O) c119_result x y ↔ ObsEq (linearSystem c119_A c119_O) x y :=
  replaySource_all_words c119_A c119_O c119_evidence c119_result c119_checked_data x y
theorem c119_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c119_R) c119_R) :
    taggedRealize (linearSystem c119_A c119_O) (guardedCodeFormula c119_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c119_A c119_O) :=
  replaySource_standard_formula c119_A c119_O c119_evidence c119_result c119_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch09
