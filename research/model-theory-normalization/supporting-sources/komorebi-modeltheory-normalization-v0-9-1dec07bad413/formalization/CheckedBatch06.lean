module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch06
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c072_R := ZMod 8
def c072_A : Fin 1 → Mat c072_R 4 4 := ![![![1, 7, 6, 4], ![7, 6, 3, 3], ![3, 4, 1, 7], ![7, 1, 1, 4]]]
def c072_O : Mat c072_R 2 4 := ![![6, 3, 3, 5], ![4, 3, 3, 1]]
def c072_evidence : List (Evidence c072_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![1, 6, 0, 0]),
  .separation (![4, 0, 0, 0]),
  .separation (![0, 7, 1, 0]),
  .separation (![0, 4, 4, 0]),
  .combination [0, 2, 0, 0, 5],
  .combination [2, 1, 6, 0, 6]]
def c072_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c072_checked_data : replaySource c072_A c072_O c072_evidence = some c072_result := by decide +kernel
theorem c072_reference_result :
    finitePrimeDiscover 2 3 4 (fun a => rowRight (c072_A a)) c072_O = some c072_result :=
  replaySource_reference 2 3 4 (by decide +kernel) c072_A c072_O c072_evidence c072_result c072_checked_data
theorem c072_all_words (x y : Fin 4 → c072_R) :
    CodeEqual (linearSystem c072_A c072_O) c072_result x y ↔ ObsEq (linearSystem c072_A c072_O) x y :=
  replaySource_all_words c072_A c072_O c072_evidence c072_result c072_checked_data x y
theorem c072_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c072_R) c072_R) :
    taggedRealize (linearSystem c072_A c072_O) (guardedCodeFormula c072_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c072_A c072_O) :=
  replaySource_standard_formula c072_A c072_O c072_evidence c072_result c072_checked_data e
abbrev c073_R := ZMod 27
def c073_A : Fin 2 → Mat c073_R 4 4 := ![![![22, 22, 13, 24], ![22, 0, 21, 6], ![19, 23, 2, 0], ![14, 5, 13, 14]], ![![26, 14, 3, 3], ![12, 8, 16, 16], ![9, 15, 18, 6], ![19, 20, 8, 4]]]
def c073_O : Mat c073_R 1 4 := ![![0, 0, 0, 0]]
def c073_evidence : List (Evidence c073_R 4) := [
  .combination []]
def c073_result : List (Test 2 1) := []
theorem c073_checked_data : replaySource c073_A c073_O c073_evidence = some c073_result := by decide +kernel
theorem c073_reference_result :
    finitePrimeDiscover 3 3 4 (fun a => rowRight (c073_A a)) c073_O = some c073_result :=
  replaySource_reference 3 3 4 (by decide +kernel) c073_A c073_O c073_evidence c073_result c073_checked_data
theorem c073_all_words (x y : Fin 4 → c073_R) :
    CodeEqual (linearSystem c073_A c073_O) c073_result x y ↔ ObsEq (linearSystem c073_A c073_O) x y :=
  replaySource_all_words c073_A c073_O c073_evidence c073_result c073_checked_data x y
theorem c073_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c073_R) c073_R) :
    taggedRealize (linearSystem c073_A c073_O) (guardedCodeFormula c073_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c073_A c073_O) :=
  replaySource_standard_formula c073_A c073_O c073_evidence c073_result c073_checked_data e
abbrev c074_R := ZMod 125
def c074_A : Fin 3 → Mat c074_R 4 4 := ![![![122, 32, 47, 33], ![15, 16, 4, 91], ![81, 96, 28, 33], ![0, 107, 7, 111]], ![![19, 62, 92, 116], ![56, 67, 116, 89], ![89, 50, 99, 79], ![12, 78, 75, 119]], ![![48, 106, 46, 6], ![56, 113, 122, 95], ![40, 16, 104, 121], ![21, 82, 16, 58]]]
def c074_O : Mat c074_R 2 4 := ![![104, 94, 58, 17], ![44, 98, 58, 7]]
def c074_evidence : List (Evidence c074_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![64, 1, 0, 0]),
  .separation (![103, 45, 1, 0]),
  .separation (![53, 45, 1, 100]),
  .combination [10, 63, 81, 45],
  .combination [25, 55, 33, 33],
  .combination [31, 55, 72, 119],
  .combination [65, 76, 3, 75],
  .combination [35, 33, 107, 75],
  .combination [64, 29, 56, 62],
  .combination [108, 100, 109, 118],
  .combination [109, 86, 91, 115],
  .combination [3, 30, 107, 68],
  .combination [59, 25, 41, 3]]
def c074_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c074_checked_data : replaySource c074_A c074_O c074_evidence = some c074_result := by decide +kernel
theorem c074_reference_result :
    finitePrimeDiscover 5 3 4 (fun a => rowRight (c074_A a)) c074_O = some c074_result :=
  replaySource_reference 5 3 4 (by decide +kernel) c074_A c074_O c074_evidence c074_result c074_checked_data
theorem c074_all_words (x y : Fin 4 → c074_R) :
    CodeEqual (linearSystem c074_A c074_O) c074_result x y ↔ ObsEq (linearSystem c074_A c074_O) x y :=
  replaySource_all_words c074_A c074_O c074_evidence c074_result c074_checked_data x y
theorem c074_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c074_R) c074_R) :
    taggedRealize (linearSystem c074_A c074_O) (guardedCodeFormula c074_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c074_A c074_O) :=
  replaySource_standard_formula c074_A c074_O c074_evidence c074_result c074_checked_data e
abbrev c075_R := ZMod 16
def c075_A : Fin 1 → Mat c075_R 4 4 := ![![![15, 1, 15, 6], ![8, 4, 6, 15], ![4, 14, 7, 12], ![4, 10, 11, 3]]]
def c075_O : Mat c075_R 1 4 := ![![3, 14, 6, 12]]
def c075_evidence : List (Evidence c075_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![6, 1, 0, 0]),
  .separation (![8, 15, 1, 0]),
  .separation (![12, 5, 15, 1]),
  .combination [4, 5, 11, 13]]
def c075_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem c075_checked_data : replaySource c075_A c075_O c075_evidence = some c075_result := by decide +kernel
theorem c075_reference_result :
    finitePrimeDiscover 2 4 4 (fun a => rowRight (c075_A a)) c075_O = some c075_result :=
  replaySource_reference 2 4 4 (by decide +kernel) c075_A c075_O c075_evidence c075_result c075_checked_data
theorem c075_all_words (x y : Fin 4 → c075_R) :
    CodeEqual (linearSystem c075_A c075_O) c075_result x y ↔ ObsEq (linearSystem c075_A c075_O) x y :=
  replaySource_all_words c075_A c075_O c075_evidence c075_result c075_checked_data x y
theorem c075_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c075_R) c075_R) :
    taggedRealize (linearSystem c075_A c075_O) (guardedCodeFormula c075_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c075_A c075_O) :=
  replaySource_standard_formula c075_A c075_O c075_evidence c075_result c075_checked_data e
abbrev c076_R := ZMod 81
def c076_A : Fin 2 → Mat c076_R 4 4 := ![![![7, 73, 80, 13], ![77, 47, 72, 37], ![17, 80, 62, 14], ![8, 16, 46, 27]], ![![18, 10, 27, 0], ![28, 62, 19, 15], ![73, 35, 57, 75], ![80, 16, 50, 68]]]
def c076_O : Mat c076_R 2 4 := ![![18, 76, 79, 0], ![56, 22, 38, 40]]
def c076_evidence : List (Evidence c076_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![1, 36, 0, 0]),
  .separation (![70, 41, 1, 0]),
  .separation (![44, 74, 49, 1]),
  .combination [27, 49, 8, 57],
  .combination [24, 23, 52, 27],
  .combination [49, 12, 29, 25],
  .combination [25, 63, 60, 6],
  .combination [10, 77, 16, 65],
  .combination [21, 60, 61, 41]]
def c076_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c076_checked_data : replaySource c076_A c076_O c076_evidence = some c076_result := by decide +kernel
theorem c076_reference_result :
    finitePrimeDiscover 3 4 4 (fun a => rowRight (c076_A a)) c076_O = some c076_result :=
  replaySource_reference 3 4 4 (by decide +kernel) c076_A c076_O c076_evidence c076_result c076_checked_data
theorem c076_all_words (x y : Fin 4 → c076_R) :
    CodeEqual (linearSystem c076_A c076_O) c076_result x y ↔ ObsEq (linearSystem c076_A c076_O) x y :=
  replaySource_all_words c076_A c076_O c076_evidence c076_result c076_checked_data x y
theorem c076_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c076_R) c076_R) :
    taggedRealize (linearSystem c076_A c076_O) (guardedCodeFormula c076_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c076_A c076_O) :=
  replaySource_standard_formula c076_A c076_O c076_evidence c076_result c076_checked_data e
abbrev c077_R := ZMod 625
def c077_A : Fin 3 → Mat c077_R 4 4 := ![![![299, 527, 250, 441], ![451, 406, 318, 302], ![234, 59, 177, 312], ![469, 250, 252, 243]], ![![395, 164, 160, 582], ![136, 189, 328, 150], ![406, 53, 261, 547], ![64, 432, 561, 139]], ![![531, 303, 385, 393], ![417, 43, 51, 304], ![74, 386, 27, 527], ![43, 437, 313, 578]]]
def c077_O : Mat c077_R 1 4 := ![![375, 0, 250, 250]]
def c077_evidence : List (Evidence c077_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 1, 0, 0]),
  .separation (![621, 621, 1, 0]),
  .separation (![621, 621, 0, 1]),
  .combination [620, 3, 620, 3],
  .combination [51, 158, 623, 1],
  .combination [102, 314, 622, 2],
  .combination [567, 472, 620, 4],
  .combination [568, 472, 619, 4],
  .combination [576, 467, 4, 0],
  .combination [310, 315, 622, 2],
  .combination [466, 158, 622, 2],
  .combination [207, 2, 623, 1]]
def c077_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c077_checked_data : replaySource c077_A c077_O c077_evidence = some c077_result := by decide +kernel
theorem c077_reference_result :
    finitePrimeDiscover 5 4 4 (fun a => rowRight (c077_A a)) c077_O = some c077_result :=
  replaySource_reference 5 4 4 (by decide +kernel) c077_A c077_O c077_evidence c077_result c077_checked_data
theorem c077_all_words (x y : Fin 4 → c077_R) :
    CodeEqual (linearSystem c077_A c077_O) c077_result x y ↔ ObsEq (linearSystem c077_A c077_O) x y :=
  replaySource_all_words c077_A c077_O c077_evidence c077_result c077_checked_data x y
theorem c077_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c077_R) c077_R) :
    taggedRealize (linearSystem c077_A c077_O) (guardedCodeFormula c077_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c077_A c077_O) :=
  replaySource_standard_formula c077_A c077_O c077_evidence c077_result c077_checked_data e
abbrev c078_R := ZMod 32
def c078_A : Fin 1 → Mat c078_R 4 4 := ![![![18, 0, 1, 27], ![10, 31, 20, 10], ![16, 28, 15, 20], ![25, 21, 30, 23]]]
def c078_O : Mat c078_R 2 4 := ![![23, 1, 19, 28], ![7, 25, 16, 5]]
def c078_evidence : List (Evidence c078_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![25, 1, 0, 0]),
  .separation (![1, 1, 24, 0]),
  .separation (![20, 23, 27, 1]),
  .combination [11, 13, 28, 1],
  .combination [7, 8, 1, 27]]
def c078_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c078_checked_data : replaySource c078_A c078_O c078_evidence = some c078_result := by decide +kernel
theorem c078_reference_result :
    finitePrimeDiscover 2 5 4 (fun a => rowRight (c078_A a)) c078_O = some c078_result :=
  replaySource_reference 2 5 4 (by decide +kernel) c078_A c078_O c078_evidence c078_result c078_checked_data
theorem c078_all_words (x y : Fin 4 → c078_R) :
    CodeEqual (linearSystem c078_A c078_O) c078_result x y ↔ ObsEq (linearSystem c078_A c078_O) x y :=
  replaySource_all_words c078_A c078_O c078_evidence c078_result c078_checked_data x y
theorem c078_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c078_R) c078_R) :
    taggedRealize (linearSystem c078_A c078_O) (guardedCodeFormula c078_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c078_A c078_O) :=
  replaySource_standard_formula c078_A c078_O c078_evidence c078_result c078_checked_data e
abbrev c079_R := ZMod 243
def c079_A : Fin 2 → Mat c079_R 4 4 := ![![![96, 129, 204, 234], ![194, 196, 159, 228], ![178, 201, 118, 143], ![12, 26, 131, 234]], ![![66, 22, 62, 139], ![217, 167, 237, 211], ![120, 101, 225, 199], ![203, 203, 6, 98]]]
def c079_O : Mat c079_R 1 4 := ![![206, 231, 30, 207]]
def c079_evidence : List (Evidence c079_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![177, 1, 0, 0]),
  .separation (![0, 81, 0, 0]),
  .separation (![90, 229, 1, 210]),
  .combination [189, 179, 87, 47],
  .separation (![0, 162, 0, 81]),
  .separation (![0, 81, 162, 81]),
  .combination [75, 0, 225, 0, 102, 48],
  .combination [54, 0, 93, 0, 222, 114],
  .combination [79, 0, 102, 0, 90, 163],
  .combination [165, 0, 126, 0, 119, 226],
  .combination [1, 0, 32, 0, 102, 65],
  .combination [65, 0, 73, 0, 172, 194]]
def c079_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([0,1], 0), ([1,1], 0)]
theorem c079_checked_data : replaySource c079_A c079_O c079_evidence = some c079_result := by decide +kernel
theorem c079_reference_result :
    finitePrimeDiscover 3 5 4 (fun a => rowRight (c079_A a)) c079_O = some c079_result :=
  replaySource_reference 3 5 4 (by decide +kernel) c079_A c079_O c079_evidence c079_result c079_checked_data
theorem c079_all_words (x y : Fin 4 → c079_R) :
    CodeEqual (linearSystem c079_A c079_O) c079_result x y ↔ ObsEq (linearSystem c079_A c079_O) x y :=
  replaySource_all_words c079_A c079_O c079_evidence c079_result c079_checked_data x y
theorem c079_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c079_R) c079_R) :
    taggedRealize (linearSystem c079_A c079_O) (guardedCodeFormula c079_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c079_A c079_O) :=
  replaySource_standard_formula c079_A c079_O c079_evidence c079_result c079_checked_data e
abbrev c080_R := ZMod 3125
def c080_A : Fin 3 → Mat c080_R 4 4 := ![![![2781, 4, 2809, 2360], ![2840, 1576, 1793, 2417], ![2471, 666, 20, 859], ![1063, 1901, 1256, 2242]], ![![401, 2351, 497, 2498], ![246, 1266, 2326, 221], ![1341, 125, 2490, 2472], ![1753, 2328, 2560, 2227]], ![![906, 3001, 682, 563], ![11, 1251, 1314, 1325], ![1536, 2787, 1181, 2031], ![1688, 1888, 1751, 619]]]
def c080_O : Mat c080_R 2 4 := ![![34, 872, 752, 1288], ![2123, 3020, 2824, 1286]]
def c080_evidence : List (Evidence c080_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![342, 1, 0, 0]),
  .separation (![2487, 3020, 1, 0]),
  .separation (![17, 2895, 1, 1460]),
  .combination [2791, 116, 1459, 985],
  .combination [2847, 661, 2876, 2892],
  .combination [2771, 401, 2923, 2689],
  .combination [1391, 2211, 1459, 739],
  .combination [3101, 1310, 2803, 1125],
  .combination [2876, 369, 675, 1348],
  .combination [467, 2979, 2066, 2791],
  .combination [1056, 1200, 285, 30],
  .combination [2599, 1589, 1192, 2183],
  .combination [1530, 277, 2028, 14]]
def c080_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c080_checked_data : replaySource c080_A c080_O c080_evidence = some c080_result := by decide +kernel
theorem c080_reference_result :
    finitePrimeDiscover 5 5 4 (fun a => rowRight (c080_A a)) c080_O = some c080_result :=
  replaySource_reference 5 5 4 (by decide +kernel) c080_A c080_O c080_evidence c080_result c080_checked_data
theorem c080_all_words (x y : Fin 4 → c080_R) :
    CodeEqual (linearSystem c080_A c080_O) c080_result x y ↔ ObsEq (linearSystem c080_A c080_O) x y :=
  replaySource_all_words c080_A c080_O c080_evidence c080_result c080_checked_data x y
theorem c080_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c080_R) c080_R) :
    taggedRealize (linearSystem c080_A c080_O) (guardedCodeFormula c080_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c080_A c080_O) :=
  replaySource_standard_formula c080_A c080_O c080_evidence c080_result c080_checked_data e
abbrev c081_R := ZMod 2
def c081_A : Fin 1 → Mat c081_R 5 5 := ![![![1, 0, 0, 0, 0], ![1, 0, 1, 1, 1], ![1, 1, 1, 0, 0], ![1, 1, 1, 1, 1], ![1, 1, 1, 1, 0]]]
def c081_O : Mat c081_R 1 5 := ![![1, 1, 1, 1, 1]]
def c081_evidence : List (Evidence c081_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 0, 1, 0, 0]),
  .separation (![1, 0, 0, 1, 0]),
  .combination [1, 0, 1]]
def c081_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c081_checked_data : replaySource c081_A c081_O c081_evidence = some c081_result := by decide +kernel
theorem c081_reference_result :
    finitePrimeDiscover 2 1 5 (fun a => rowRight (c081_A a)) c081_O = some c081_result :=
  replaySource_reference 2 1 5 (by decide +kernel) c081_A c081_O c081_evidence c081_result c081_checked_data
theorem c081_all_words (x y : Fin 5 → c081_R) :
    CodeEqual (linearSystem c081_A c081_O) c081_result x y ↔ ObsEq (linearSystem c081_A c081_O) x y :=
  replaySource_all_words c081_A c081_O c081_evidence c081_result c081_checked_data x y
theorem c081_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c081_R) c081_R) :
    taggedRealize (linearSystem c081_A c081_O) (guardedCodeFormula c081_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c081_A c081_O) :=
  replaySource_standard_formula c081_A c081_O c081_evidence c081_result c081_checked_data e
abbrev c082_R := ZMod 3
def c082_A : Fin 2 → Mat c082_R 5 5 := ![![![2, 2, 1, 0, 1], ![1, 2, 2, 2, 2], ![2, 2, 2, 0, 2], ![1, 0, 1, 1, 0], ![0, 2, 2, 2, 1]], ![![0, 0, 2, 2, 2], ![1, 1, 2, 1, 0], ![1, 2, 0, 0, 1], ![0, 1, 2, 0, 0], ![1, 2, 1, 1, 0]]]
def c082_O : Mat c082_R 2 5 := ![![1, 2, 2, 1, 2], ![0, 2, 0, 2, 2]]
def c082_evidence : List (Evidence c082_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0]),
  .separation (![1, 0, 1, 0, 0]),
  .separation (![2, 2, 1, 1, 0]),
  .separation (![1, 0, 2, 2, 1]),
  .combination [0, 0, 0, 0, 1],
  .combination [2, 1, 2, 0, 1],
  .combination [1, 2, 2, 1, 2],
  .combination [1, 1, 1, 1, 0],
  .combination [1, 1, 2, 2, 0],
  .combination [2, 2, 1, 0, 2],
  .combination [0, 2, 0, 2, 0]]
def c082_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c082_checked_data : replaySource c082_A c082_O c082_evidence = some c082_result := by decide +kernel
theorem c082_reference_result :
    finitePrimeDiscover 3 1 5 (fun a => rowRight (c082_A a)) c082_O = some c082_result :=
  replaySource_reference 3 1 5 (by decide +kernel) c082_A c082_O c082_evidence c082_result c082_checked_data
theorem c082_all_words (x y : Fin 5 → c082_R) :
    CodeEqual (linearSystem c082_A c082_O) c082_result x y ↔ ObsEq (linearSystem c082_A c082_O) x y :=
  replaySource_all_words c082_A c082_O c082_evidence c082_result c082_checked_data x y
theorem c082_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c082_R) c082_R) :
    taggedRealize (linearSystem c082_A c082_O) (guardedCodeFormula c082_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c082_A c082_O) :=
  replaySource_standard_formula c082_A c082_O c082_evidence c082_result c082_checked_data e
abbrev c083_R := ZMod 5
def c083_A : Fin 3 → Mat c083_R 5 5 := ![![![0, 1, 2, 0, 4], ![1, 4, 2, 1, 3], ![4, 4, 4, 2, 1], ![4, 4, 1, 1, 2], ![4, 1, 4, 0, 3]], ![![0, 2, 0, 3, 0], ![3, 0, 0, 3, 0], ![2, 3, 2, 4, 0], ![4, 3, 1, 2, 1], ![1, 0, 0, 1, 3]], ![![4, 1, 3, 2, 2], ![3, 4, 0, 0, 4], ![2, 4, 1, 1, 4], ![3, 4, 1, 1, 2], ![0, 0, 0, 1, 2]]]
def c083_O : Mat c083_R 1 5 := ![![3, 4, 0, 3, 1]]
def c083_evidence : List (Evidence c083_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![2, 1, 0, 0, 0]),
  .separation (![4, 2, 1, 0, 0]),
  .separation (![3, 2, 4, 1, 0]),
  .separation (![4, 0, 4, 4, 1]),
  .combination [1, 1, 2, 0, 1],
  .combination [3, 2, 3, 2, 4],
  .combination [0, 4, 0, 4, 1],
  .combination [1, 4, 3, 4, 4],
  .combination [4, 0, 1, 2, 2],
  .combination [4, 4, 1, 0, 2],
  .combination [0, 2, 4, 1, 4],
  .combination [2, 3, 2, 1, 0],
  .combination [1, 0, 1, 0, 2],
  .combination [4, 4, 0, 1, 2],
  .combination [4, 0, 0, 0, 3]]
def c083_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c083_checked_data : replaySource c083_A c083_O c083_evidence = some c083_result := by decide +kernel
theorem c083_reference_result :
    finitePrimeDiscover 5 1 5 (fun a => rowRight (c083_A a)) c083_O = some c083_result :=
  replaySource_reference 5 1 5 (by decide +kernel) c083_A c083_O c083_evidence c083_result c083_checked_data
theorem c083_all_words (x y : Fin 5 → c083_R) :
    CodeEqual (linearSystem c083_A c083_O) c083_result x y ↔ ObsEq (linearSystem c083_A c083_O) x y :=
  replaySource_all_words c083_A c083_O c083_evidence c083_result c083_checked_data x y
theorem c083_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c083_R) c083_R) :
    taggedRealize (linearSystem c083_A c083_O) (guardedCodeFormula c083_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c083_A c083_O) :=
  replaySource_standard_formula c083_A c083_O c083_evidence c083_result c083_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch06
