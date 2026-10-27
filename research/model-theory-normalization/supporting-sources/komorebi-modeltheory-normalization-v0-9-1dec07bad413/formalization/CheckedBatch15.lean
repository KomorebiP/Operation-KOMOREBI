module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch15
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c180_R := ZMod 16
def c180_A : Fin 1 → Mat c180_R 5 5 := ![![![8, 5, 4, 14, 14], ![14, 4, 3, 10, 0], ![4, 12, 8, 11, 11], ![10, 7, 2, 2, 10], ![6, 2, 3, 2, 9]]]
def c180_O : Mat c180_R 2 5 := ![![11, 7, 5, 15, 13], ![14, 8, 15, 11, 2]]
def c180_evidence : List (Evidence c180_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![11, 1, 0, 0, 0]),
  .separation (![1, 1, 6, 0, 0]),
  .separation (![1, 1, 14, 8, 0]),
  .separation (![0, 3, 0, 2, 1]),
  .combination [10, 2, 5, 5, 14],
  .combination [14, 11, 5, 12, 10]]
def c180_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c180_checked_data : replaySource c180_A c180_O c180_evidence = some c180_result := by decide +kernel
theorem c180_reference_result :
    finitePrimeDiscover 2 4 5 (fun a => rowRight (c180_A a)) c180_O = some c180_result :=
  replaySource_reference 2 4 5 (by decide +kernel) c180_A c180_O c180_evidence c180_result c180_checked_data
theorem c180_all_words (x y : Fin 5 → c180_R) :
    CodeEqual (linearSystem c180_A c180_O) c180_result x y ↔ ObsEq (linearSystem c180_A c180_O) x y :=
  replaySource_all_words c180_A c180_O c180_evidence c180_result c180_checked_data x y
theorem c180_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c180_R) c180_R) :
    taggedRealize (linearSystem c180_A c180_O) (guardedCodeFormula c180_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c180_A c180_O) :=
  replaySource_standard_formula c180_A c180_O c180_evidence c180_result c180_checked_data e
abbrev c181_R := ZMod 81
def c181_A : Fin 2 → Mat c181_R 5 5 := ![![![67, 35, 20, 56, 25], ![1, 1, 58, 54, 33], ![42, 48, 80, 17, 7], ![19, 54, 20, 20, 60], ![39, 2, 29, 55, 65]], ![![11, 57, 23, 51, 3], ![23, 77, 48, 66, 33], ![11, 4, 13, 43, 50], ![8, 0, 66, 28, 26], ![21, 42, 48, 55, 21]]]
def c181_O : Mat c181_R 1 5 := ![![30, 60, 25, 52, 17]]
def c181_evidence : List (Evidence c181_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![0, 1, 30, 0, 0]),
  .separation (![1, 14, 30, 0, 0]),
  .separation (![1, 71, 6, 33, 0]),
  .separation (![23, 20, 0, 49, 1]),
  .combination [23, 25, 15, 13, 12],
  .combination [32, 18, 58, 76, 4],
  .combination [62, 7, 68, 62, 23],
  .combination [58, 71, 4, 20, 59],
  .combination [9, 64, 21, 42, 75],
  .combination [18, 46, 13, 10, 72]]
def c181_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem c181_checked_data : replaySource c181_A c181_O c181_evidence = some c181_result := by decide +kernel
theorem c181_reference_result :
    finitePrimeDiscover 3 4 5 (fun a => rowRight (c181_A a)) c181_O = some c181_result :=
  replaySource_reference 3 4 5 (by decide +kernel) c181_A c181_O c181_evidence c181_result c181_checked_data
theorem c181_all_words (x y : Fin 5 → c181_R) :
    CodeEqual (linearSystem c181_A c181_O) c181_result x y ↔ ObsEq (linearSystem c181_A c181_O) x y :=
  replaySource_all_words c181_A c181_O c181_evidence c181_result c181_checked_data x y
theorem c181_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c181_R) c181_R) :
    taggedRealize (linearSystem c181_A c181_O) (guardedCodeFormula c181_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c181_A c181_O) :=
  replaySource_standard_formula c181_A c181_O c181_evidence c181_result c181_checked_data e
abbrev c182_R := ZMod 625
def c182_A : Fin 3 → Mat c182_R 5 5 := ![![![268, 144, 159, 343, 415], ![132, 118, 156, 320, 123], ![14, 451, 581, 616, 522], ![129, 578, 466, 123, 60], ![613, 260, 435, 522, 512]], ![![600, 480, 119, 228, 559], ![486, 510, 619, 445, 189], ![104, 471, 459, 113, 57], ![408, 92, 176, 370, 517], ![194, 172, 537, 585, 241]], ![![139, 573, 318, 393, 37], ![351, 553, 231, 226, 183], ![37, 15, 174, 106, 530], ![46, 606, 525, 224, 85], ![273, 20, 89, 12, 188]]]
def c182_O : Mat c182_R 2 5 := ![![500, 0, 250, 250, 0], ![125, 500, 0, 250, 250]]
def c182_evidence : List (Evidence c182_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![0, 1, 0, 0, 0]),
  .separation (![622, 622, 1, 0, 0]),
  .separation (![6, 8, 622, 1, 0]),
  .separation (![610, 599, 9, 621, 1]),
  .combination [272, 311, 156, 1, 2],
  .combination [390, 0, 313, 1, 0],
  .combination [59, 468, 390, 312, 2],
  .combination [431, 312, 156, 624, 2],
  .combination [391, 468, 156, 624, 2],
  .combination [411, 468, 547, 312, 1],
  .combination [196, 155, 312, 624, 3],
  .combination [118, 624, 468, 624, 2],
  .combination [156, 156, 156, 1, 1],
  .combination [176, 624, 391, 312, 1],
  .combination [273, 156, 0, 1, 0],
  .combination [450, 467, 78, 312, 2]]
def c182_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)]
theorem c182_checked_data : replaySource c182_A c182_O c182_evidence = some c182_result := by decide +kernel
theorem c182_reference_result :
    finitePrimeDiscover 5 4 5 (fun a => rowRight (c182_A a)) c182_O = some c182_result :=
  replaySource_reference 5 4 5 (by decide +kernel) c182_A c182_O c182_evidence c182_result c182_checked_data
theorem c182_all_words (x y : Fin 5 → c182_R) :
    CodeEqual (linearSystem c182_A c182_O) c182_result x y ↔ ObsEq (linearSystem c182_A c182_O) x y :=
  replaySource_all_words c182_A c182_O c182_evidence c182_result c182_checked_data x y
theorem c182_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c182_R) c182_R) :
    taggedRealize (linearSystem c182_A c182_O) (guardedCodeFormula c182_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c182_A c182_O) :=
  replaySource_standard_formula c182_A c182_O c182_evidence c182_result c182_checked_data e
abbrev c183_R := ZMod 32
def c183_A : Fin 1 → Mat c183_R 5 5 := ![![![7, 24, 19, 15, 9], ![12, 29, 18, 19, 3], ![29, 5, 29, 29, 27], ![10, 15, 30, 16, 8], ![31, 20, 23, 25, 3]]]
def c183_O : Mat c183_R 1 5 := ![![15, 1, 30, 24, 4]]
def c183_evidence : List (Evidence c183_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![17, 1, 0, 0, 0]),
  .separation (![13, 1, 18, 0, 0]),
  .separation (![29, 1, 10, 20, 0]),
  .separation (![30, 22, 18, 19, 1]),
  .combination [0, 8, 15, 16, 4]]
def c183_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c183_checked_data : replaySource c183_A c183_O c183_evidence = some c183_result := by decide +kernel
theorem c183_reference_result :
    finitePrimeDiscover 2 5 5 (fun a => rowRight (c183_A a)) c183_O = some c183_result :=
  replaySource_reference 2 5 5 (by decide +kernel) c183_A c183_O c183_evidence c183_result c183_checked_data
theorem c183_all_words (x y : Fin 5 → c183_R) :
    CodeEqual (linearSystem c183_A c183_O) c183_result x y ↔ ObsEq (linearSystem c183_A c183_O) x y :=
  replaySource_all_words c183_A c183_O c183_evidence c183_result c183_checked_data x y
theorem c183_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c183_R) c183_R) :
    taggedRealize (linearSystem c183_A c183_O) (guardedCodeFormula c183_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c183_A c183_O) :=
  replaySource_standard_formula c183_A c183_O c183_evidence c183_result c183_checked_data e
abbrev c184_R := ZMod 243
def c184_A : Fin 2 → Mat c184_R 5 5 := ![![![190, 61, 168, 113, 0], ![16, 1, 13, 131, 109], ![15, 17, 145, 1, 57], ![66, 46, 167, 80, 219], ![82, 90, 236, 120, 79]], ![![182, 240, 208, 122, 72], ![17, 129, 228, 181, 105], ![40, 131, 146, 133, 106], ![164, 47, 217, 2, 17], ![151, 162, 56, 95, 197]]]
def c184_O : Mat c184_R 2 5 := ![![171, 200, 177, 159, 118], ![199, 74, 135, 218, 222]]
def c184_evidence : List (Evidence c184_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 117, 0, 0, 0]),
  .separation (![150, 222, 1, 0, 0]),
  .separation (![61, 45, 98, 1, 0]),
  .separation (![73, 127, 82, 9, 1]),
  .combination [160, 94, 180, 219, 222],
  .combination [213, 85, 166, 2, 146],
  .combination [231, 146, 10, 208, 71],
  .combination [48, 176, 219, 13, 231],
  .combination [46, 34, 86, 105, 164],
  .combination [3, 233, 219, 199, 73],
  .combination [11, 181, 175, 167, 204]]
def c184_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c184_checked_data : replaySource c184_A c184_O c184_evidence = some c184_result := by decide +kernel
theorem c184_reference_result :
    finitePrimeDiscover 3 5 5 (fun a => rowRight (c184_A a)) c184_O = some c184_result :=
  replaySource_reference 3 5 5 (by decide +kernel) c184_A c184_O c184_evidence c184_result c184_checked_data
theorem c184_all_words (x y : Fin 5 → c184_R) :
    CodeEqual (linearSystem c184_A c184_O) c184_result x y ↔ ObsEq (linearSystem c184_A c184_O) x y :=
  replaySource_all_words c184_A c184_O c184_evidence c184_result c184_checked_data x y
theorem c184_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c184_R) c184_R) :
    taggedRealize (linearSystem c184_A c184_O) (guardedCodeFormula c184_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c184_A c184_O) :=
  replaySource_standard_formula c184_A c184_O c184_evidence c184_result c184_checked_data e
abbrev c185_R := ZMod 3125
def c185_A : Fin 3 → Mat c185_R 5 5 := ![![![1331, 1876, 1173, 1684, 1937], ![556, 1499, 2714, 2283, 447], ![2803, 664, 2344, 1296, 1713], ![1422, 841, 2661, 2983, 3011], ![340, 110, 1368, 2398, 1549]], ![![697, 1148, 1073, 245, 517], ![26, 521, 2207, 1239, 2122], ![360, 1178, 355, 1939, 2263], ![1484, 2820, 1204, 2834, 2234], ![2608, 78, 445, 267, 2914]], ![![1649, 1259, 339, 2615, 1617], ![2869, 2745, 1957, 2747, 870], ![2567, 2842, 1321, 2954, 1983], ![2180, 2801, 2172, 2718, 1193], ![2544, 1971, 1024, 1694, 839]]]
def c185_O : Mat c185_R 1 5 := ![![1490, 937, 878, 624, 1892]]
def c185_evidence : List (Evidence c185_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 2980, 0, 0, 0]),
  .separation (![2534, 1826, 1, 0, 0]),
  .separation (![1508, 599, 2606, 1, 0]),
  .separation (![2604, 1036, 1807, 1630, 1]),
  .combination [1236, 3061, 3018, 2335, 1487],
  .combination [2053, 1503, 920, 2493, 2032],
  .combination [3093, 1799, 1870, 924, 811],
  .combination [1777, 43, 125, 970, 2422],
  .combination [331, 2337, 958, 1435, 1231],
  .combination [2462, 2179, 2478, 406, 960],
  .combination [2721, 3055, 1440, 1937, 2454],
  .combination [2083, 779, 1760, 913, 1348],
  .combination [2141, 2874, 2315, 688, 1180],
  .combination [2396, 1849, 1818, 356, 2198],
  .combination [2114, 1920, 1613, 2395, 2773]]
def c185_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c185_checked_data : replaySource c185_A c185_O c185_evidence = some c185_result := by decide +kernel
theorem c185_reference_result :
    finitePrimeDiscover 5 5 5 (fun a => rowRight (c185_A a)) c185_O = some c185_result :=
  replaySource_reference 5 5 5 (by decide +kernel) c185_A c185_O c185_evidence c185_result c185_checked_data
theorem c185_all_words (x y : Fin 5 → c185_R) :
    CodeEqual (linearSystem c185_A c185_O) c185_result x y ↔ ObsEq (linearSystem c185_A c185_O) x y :=
  replaySource_all_words c185_A c185_O c185_evidence c185_result c185_checked_data x y
theorem c185_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c185_R) c185_R) :
    taggedRealize (linearSystem c185_A c185_O) (guardedCodeFormula c185_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c185_A c185_O) :=
  replaySource_standard_formula c185_A c185_O c185_evidence c185_result c185_checked_data e
abbrev c186_R := ZMod 2
def c186_A : Fin 1 → Mat c186_R 6 6 := ![![![0, 1, 1, 0, 1, 0], ![1, 0, 1, 0, 0, 1], ![1, 0, 0, 1, 1, 0], ![0, 1, 0, 1, 1, 0], ![0, 0, 1, 1, 0, 0], ![1, 1, 1, 1, 0, 0]]]
def c186_O : Mat c186_R 2 6 := ![![1, 1, 0, 0, 1, 1], ![0, 0, 1, 0, 1, 0]]
def c186_evidence : List (Evidence c186_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![0, 0, 1, 0, 0, 0]),
  .separation (![1, 0, 1, 0, 1, 0]),
  .separation (![1, 1, 0, 0, 0, 0]),
  .combination [1, 0, 1, 0],
  .combination [1, 0, 1, 0]]
def c186_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c186_checked_data : replaySource c186_A c186_O c186_evidence = some c186_result := by decide +kernel
theorem c186_reference_result :
    finitePrimeDiscover 2 1 6 (fun a => rowRight (c186_A a)) c186_O = some c186_result :=
  replaySource_reference 2 1 6 (by decide +kernel) c186_A c186_O c186_evidence c186_result c186_checked_data
theorem c186_all_words (x y : Fin 6 → c186_R) :
    CodeEqual (linearSystem c186_A c186_O) c186_result x y ↔ ObsEq (linearSystem c186_A c186_O) x y :=
  replaySource_all_words c186_A c186_O c186_evidence c186_result c186_checked_data x y
theorem c186_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c186_R) c186_R) :
    taggedRealize (linearSystem c186_A c186_O) (guardedCodeFormula c186_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c186_A c186_O) :=
  replaySource_standard_formula c186_A c186_O c186_evidence c186_result c186_checked_data e
abbrev c187_R := ZMod 3
def c187_A : Fin 2 → Mat c187_R 6 6 := ![![![2, 2, 2, 1, 1, 1], ![2, 0, 2, 2, 1, 0], ![0, 0, 0, 0, 1, 0], ![2, 0, 2, 1, 0, 1], ![0, 0, 1, 2, 2, 1], ![1, 0, 1, 1, 2, 2]], ![![2, 2, 0, 0, 1, 1], ![0, 0, 2, 0, 1, 2], ![0, 2, 2, 1, 1, 0], ![2, 2, 2, 1, 0, 1], ![1, 2, 0, 0, 2, 0], ![0, 2, 2, 0, 0, 0]]]
def c187_O : Mat c187_R 1 6 := ![![1, 1, 1, 2, 1, 0]]
def c187_evidence : List (Evidence c187_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![2, 0, 1, 0, 0, 0]),
  .separation (![1, 0, 0, 1, 0, 0]),
  .separation (![2, 1, 0, 0, 0, 0]),
  .separation (![0, 0, 2, 2, 0, 1]),
  .combination [1, 2, 0, 0, 2],
  .separation (![1, 0, 0, 2, 1, 0]),
  .combination [1, 2, 0, 1, 2, 2],
  .combination [2, 1, 2, 2, 0, 1],
  .combination [2, 2, 2, 2, 2, 0],
  .combination [1, 1, 2, 0, 1, 1],
  .combination [2, 2, 0, 0, 0, 1],
  .combination [2, 0, 2, 0, 0, 1]]
def c187_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([1,1], 0)]
theorem c187_checked_data : replaySource c187_A c187_O c187_evidence = some c187_result := by decide +kernel
theorem c187_reference_result :
    finitePrimeDiscover 3 1 6 (fun a => rowRight (c187_A a)) c187_O = some c187_result :=
  replaySource_reference 3 1 6 (by decide +kernel) c187_A c187_O c187_evidence c187_result c187_checked_data
theorem c187_all_words (x y : Fin 6 → c187_R) :
    CodeEqual (linearSystem c187_A c187_O) c187_result x y ↔ ObsEq (linearSystem c187_A c187_O) x y :=
  replaySource_all_words c187_A c187_O c187_evidence c187_result c187_checked_data x y
theorem c187_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c187_R) c187_R) :
    taggedRealize (linearSystem c187_A c187_O) (guardedCodeFormula c187_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c187_A c187_O) :=
  replaySource_standard_formula c187_A c187_O c187_evidence c187_result c187_checked_data e
abbrev c188_R := ZMod 5
def c188_A : Fin 3 → Mat c188_R 6 6 := ![![![3, 2, 1, 4, 3, 1], ![4, 3, 3, 0, 3, 3], ![2, 4, 2, 2, 0, 4], ![1, 1, 2, 2, 0, 3], ![3, 2, 4, 1, 4, 3], ![4, 0, 0, 3, 3, 4]], ![![2, 3, 0, 2, 4, 2], ![2, 4, 3, 1, 3, 0], ![2, 4, 3, 1, 2, 0], ![1, 1, 0, 4, 4, 3], ![2, 3, 0, 2, 2, 0], ![1, 1, 3, 1, 2, 0]], ![![0, 4, 3, 0, 4, 2], ![2, 0, 0, 3, 4, 4], ![0, 4, 1, 0, 2, 1], ![1, 2, 1, 2, 1, 0], ![3, 2, 4, 4, 0, 0], ![4, 2, 4, 1, 3, 0]]]
def c188_O : Mat c188_R 2 6 := ![![2, 3, 3, 3, 3, 3], ![4, 0, 3, 4, 1, 4]]
def c188_evidence : List (Evidence c188_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0, 0]),
  .separation (![3, 2, 1, 0, 0, 0]),
  .separation (![0, 1, 3, 0, 1, 0]),
  .separation (![0, 2, 2, 1, 0, 0]),
  .combination [4, 0, 0, 1, 3],
  .combination [1, 3, 3, 2, 0],
  .combination [0, 0, 0, 1, 2],
  .separation (![1, 2, 4, 2, 2, 1]),
  .combination [2, 1, 0, 2, 0, 1],
  .combination [4, 0, 1, 1, 4, 3],
  .combination [2, 4, 3, 1, 2, 0],
  .combination [1, 2, 0, 2, 4, 1],
  .combination [3, 1, 1, 0, 1, 3],
  .combination [3, 2, 4, 4, 1, 3],
  .combination [2, 3, 2, 2, 0, 0],
  .combination [3, 0, 2, 0, 4, 2],
  .combination [4, 0, 1, 3, 1, 1],
  .combination [4, 3, 0, 3, 1, 0],
  .combination [4, 4, 2, 0, 2, 3]]
def c188_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c188_checked_data : replaySource c188_A c188_O c188_evidence = some c188_result := by decide +kernel
theorem c188_reference_result :
    finitePrimeDiscover 5 1 6 (fun a => rowRight (c188_A a)) c188_O = some c188_result :=
  replaySource_reference 5 1 6 (by decide +kernel) c188_A c188_O c188_evidence c188_result c188_checked_data
theorem c188_all_words (x y : Fin 6 → c188_R) :
    CodeEqual (linearSystem c188_A c188_O) c188_result x y ↔ ObsEq (linearSystem c188_A c188_O) x y :=
  replaySource_all_words c188_A c188_O c188_evidence c188_result c188_checked_data x y
theorem c188_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c188_R) c188_R) :
    taggedRealize (linearSystem c188_A c188_O) (guardedCodeFormula c188_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c188_A c188_O) :=
  replaySource_standard_formula c188_A c188_O c188_evidence c188_result c188_checked_data e
abbrev c189_R := ZMod 4
def c189_A : Fin 1 → Mat c189_R 6 6 := ![![![1, 3, 3, 1, 1, 0], ![0, 2, 2, 0, 1, 1], ![2, 3, 3, 3, 3, 0], ![1, 0, 1, 3, 3, 1], ![3, 1, 1, 3, 2, 3], ![3, 1, 3, 2, 3, 3]]]
def c189_O : Mat c189_R 1 6 := ![![0, 0, 0, 0, 0, 2]]
def c189_evidence : List (Evidence c189_R 6) := [
  .separation (![0, 0, 0, 0, 0, 1]),
  .separation (![0, 1, 0, 0, 0, 0]),
  .separation (![0, 0, 0, 1, 0, 0]),
  .separation (![0, 3, 1, 0, 0, 0]),
  .separation (![0, 0, 3, 0, 1, 0]),
  .separation (![1, 0, 3, 3, 0, 0]),
  .combination [0, 0, 1, 0, 0, 0]]
def c189_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0)]
theorem c189_checked_data : replaySource c189_A c189_O c189_evidence = some c189_result := by decide +kernel
theorem c189_reference_result :
    finitePrimeDiscover 2 2 6 (fun a => rowRight (c189_A a)) c189_O = some c189_result :=
  replaySource_reference 2 2 6 (by decide +kernel) c189_A c189_O c189_evidence c189_result c189_checked_data
theorem c189_all_words (x y : Fin 6 → c189_R) :
    CodeEqual (linearSystem c189_A c189_O) c189_result x y ↔ ObsEq (linearSystem c189_A c189_O) x y :=
  replaySource_all_words c189_A c189_O c189_evidence c189_result c189_checked_data x y
theorem c189_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c189_R) c189_R) :
    taggedRealize (linearSystem c189_A c189_O) (guardedCodeFormula c189_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c189_A c189_O) :=
  replaySource_standard_formula c189_A c189_O c189_evidence c189_result c189_checked_data e
abbrev c190_R := ZMod 9
def c190_A : Fin 2 → Mat c190_R 6 6 := ![![![1, 8, 2, 8, 5, 1], ![4, 1, 5, 8, 8, 8], ![1, 6, 8, 3, 7, 3], ![5, 6, 6, 8, 5, 2], ![6, 7, 2, 2, 7, 3], ![1, 4, 4, 5, 1, 5]], ![![5, 4, 1, 0, 0, 0], ![7, 8, 5, 6, 7, 4], ![8, 5, 4, 3, 4, 7], ![6, 7, 3, 2, 3, 3], ![2, 2, 4, 5, 2, 5], ![3, 3, 8, 1, 4, 1]]]
def c190_O : Mat c190_R 2 6 := ![![0, 0, 0, 0, 0, 0], ![0, 0, 0, 0, 0, 0]]
def c190_evidence : List (Evidence c190_R 6) := [
  .combination [],
  .combination []]
def c190_result : List (Test 2 2) := []
theorem c190_checked_data : replaySource c190_A c190_O c190_evidence = some c190_result := by decide +kernel
theorem c190_reference_result :
    finitePrimeDiscover 3 2 6 (fun a => rowRight (c190_A a)) c190_O = some c190_result :=
  replaySource_reference 3 2 6 (by decide +kernel) c190_A c190_O c190_evidence c190_result c190_checked_data
theorem c190_all_words (x y : Fin 6 → c190_R) :
    CodeEqual (linearSystem c190_A c190_O) c190_result x y ↔ ObsEq (linearSystem c190_A c190_O) x y :=
  replaySource_all_words c190_A c190_O c190_evidence c190_result c190_checked_data x y
theorem c190_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c190_R) c190_R) :
    taggedRealize (linearSystem c190_A c190_O) (guardedCodeFormula c190_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c190_A c190_O) :=
  replaySource_standard_formula c190_A c190_O c190_evidence c190_result c190_checked_data e
abbrev c191_R := ZMod 25
def c191_A : Fin 3 → Mat c191_R 6 6 := ![![![20, 21, 12, 18, 2, 6], ![2, 2, 10, 22, 18, 14], ![2, 2, 1, 0, 3, 20], ![8, 18, 2, 4, 13, 20], ![2, 9, 5, 19, 10, 22], ![10, 2, 5, 11, 9, 17]], ![![1, 13, 24, 5, 7, 23], ![8, 5, 5, 24, 18, 1], ![4, 5, 21, 20, 6, 5], ![0, 1, 6, 23, 5, 0], ![8, 2, 12, 13, 4, 1], ![7, 15, 19, 21, 12, 17]], ![![16, 23, 14, 24, 6, 21], ![23, 14, 0, 1, 22, 1], ![10, 10, 23, 13, 5, 17], ![23, 0, 5, 2, 5, 0], ![5, 12, 15, 16, 1, 10], ![24, 13, 21, 24, 14, 2]]]
def c191_O : Mat c191_R 1 6 := ![![22, 19, 4, 10, 21, 15]]
def c191_evidence : List (Evidence c191_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![23, 1, 0, 0, 0, 0]),
  .separation (![12, 3, 1, 0, 0, 0]),
  .separation (![2, 21, 18, 1, 0, 0]),
  .separation (![19, 12, 2, 0, 1, 0]),
  .separation (![17, 3, 2, 18, 21, 1]),
  .combination [19, 3, 15, 24, 2, 19],
  .combination [8, 20, 22, 18, 9, 22],
  .combination [0, 9, 23, 4, 13, 2],
  .combination [19, 3, 21, 22, 18, 14],
  .combination [16, 8, 12, 7, 4, 3],
  .combination [5, 6, 14, 3, 22, 20],
  .combination [0, 18, 3, 1, 20, 11],
  .combination [15, 24, 8, 17, 17, 5],
  .combination [6, 13, 14, 2, 15, 9],
  .combination [5, 23, 3, 2, 23, 9],
  .combination [19, 7, 18, 2, 13, 8],
  .combination [5, 24, 12, 9, 10, 5],
  .combination [8, 3, 10, 7, 8, 10]]
def c191_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c191_checked_data : replaySource c191_A c191_O c191_evidence = some c191_result := by decide +kernel
theorem c191_reference_result :
    finitePrimeDiscover 5 2 6 (fun a => rowRight (c191_A a)) c191_O = some c191_result :=
  replaySource_reference 5 2 6 (by decide +kernel) c191_A c191_O c191_evidence c191_result c191_checked_data
theorem c191_all_words (x y : Fin 6 → c191_R) :
    CodeEqual (linearSystem c191_A c191_O) c191_result x y ↔ ObsEq (linearSystem c191_A c191_O) x y :=
  replaySource_all_words c191_A c191_O c191_evidence c191_result c191_checked_data x y
theorem c191_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c191_R) c191_R) :
    taggedRealize (linearSystem c191_A c191_O) (guardedCodeFormula c191_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c191_A c191_O) :=
  replaySource_standard_formula c191_A c191_O c191_evidence c191_result c191_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch15
