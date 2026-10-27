module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch14
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c168_R := ZMod 32
def c168_A : Fin 1 → Mat c168_R 4 4 := ![![![27, 28, 4, 29], ![14, 19, 14, 27], ![16, 8, 25, 27], ![3, 3, 28, 12]]]
def c168_O : Mat c168_R 2 4 := ![![16, 16, 16, 0], ![16, 0, 16, 0]]
def c168_evidence : List (Evidence c168_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![31, 1, 0, 0]),
  .separation (![0, 0, 0, 1]),
  .combination [0, 1, 0],
  .separation (![31, 0, 1, 0]),
  .combination [0, 0, 1, 0]]
def c168_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0,0], 0)]
theorem c168_checked_data : replaySource c168_A c168_O c168_evidence = some c168_result := by decide +kernel
theorem c168_reference_result :
    finitePrimeDiscover 2 5 4 (fun a => rowRight (c168_A a)) c168_O = some c168_result :=
  replaySource_reference 2 5 4 (by decide +kernel) c168_A c168_O c168_evidence c168_result c168_checked_data
theorem c168_all_words (x y : Fin 4 → c168_R) :
    CodeEqual (linearSystem c168_A c168_O) c168_result x y ↔ ObsEq (linearSystem c168_A c168_O) x y :=
  replaySource_all_words c168_A c168_O c168_evidence c168_result c168_checked_data x y
theorem c168_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c168_R) c168_R) :
    taggedRealize (linearSystem c168_A c168_O) (guardedCodeFormula c168_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c168_A c168_O) :=
  replaySource_standard_formula c168_A c168_O c168_evidence c168_result c168_checked_data e
abbrev c169_R := ZMod 243
def c169_A : Fin 2 → Mat c169_R 4 4 := ![![![32, 180, 15, 20], ![59, 86, 189, 61], ![134, 9, 112, 209], ![81, 1, 99, 94]], ![![177, 114, 54, 45], ![92, 125, 240, 197], ![150, 83, 136, 114], ![5, 176, 145, 7]]]
def c169_O : Mat c169_R 1 4 := ![![73, 8, 194, 48]]
def c169_evidence : List (Evidence c169_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![163, 1, 0, 0]),
  .separation (![37, 33, 1, 0]),
  .separation (![226, 141, 1, 54]),
  .combination [140, 221, 117, 235],
  .combination [64, 222, 87, 69],
  .combination [207, 155, 169, 117],
  .combination [235, 87, 84, 237],
  .combination [218, 148, 147, 55]]
def c169_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c169_checked_data : replaySource c169_A c169_O c169_evidence = some c169_result := by decide +kernel
theorem c169_reference_result :
    finitePrimeDiscover 3 5 4 (fun a => rowRight (c169_A a)) c169_O = some c169_result :=
  replaySource_reference 3 5 4 (by decide +kernel) c169_A c169_O c169_evidence c169_result c169_checked_data
theorem c169_all_words (x y : Fin 4 → c169_R) :
    CodeEqual (linearSystem c169_A c169_O) c169_result x y ↔ ObsEq (linearSystem c169_A c169_O) x y :=
  replaySource_all_words c169_A c169_O c169_evidence c169_result c169_checked_data x y
theorem c169_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c169_R) c169_R) :
    taggedRealize (linearSystem c169_A c169_O) (guardedCodeFormula c169_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c169_A c169_O) :=
  replaySource_standard_formula c169_A c169_O c169_evidence c169_result c169_checked_data e
abbrev c170_R := ZMod 3125
def c170_A : Fin 3 → Mat c170_R 4 4 := ![![![422, 1382, 2161, 2712], ![1903, 1948, 1425, 397], ![1316, 489, 2493, 1136], ![2740, 1710, 724, 569]], ![![2544, 761, 2548, 1006], ![700, 2335, 243, 1972], ![2007, 2783, 2393, 2029], ![1475, 435, 1958, 547]], ![![1602, 2746, 2378, 2127], ![1559, 1191, 150, 2970], ![3057, 2550, 2597, 662], ![1123, 1514, 409, 2522]]]
def c170_O : Mat c170_R 2 4 := ![![1426, 1137, 565, 2015], ![3043, 3060, 2509, 1388]]
def c170_evidence : List (Evidence c170_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![1588, 1, 0, 0]),
  .separation (![107, 2644, 1, 0]),
  .separation (![2353, 1921, 922, 1]),
  .combination [2077, 2862, 2531, 571],
  .combination [2395, 2543, 1268, 1718],
  .combination [1610, 795, 1990, 2060],
  .combination [2086, 2001, 1457, 2552],
  .combination [2766, 2207, 2496, 519],
  .combination [945, 1905, 1045, 3121],
  .combination [466, 39, 2233, 2884],
  .combination [2916, 2530, 959, 393],
  .combination [591, 664, 2115, 2854],
  .combination [3058, 130, 1866, 1601]]
def c170_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c170_checked_data : replaySource c170_A c170_O c170_evidence = some c170_result := by decide +kernel
theorem c170_reference_result :
    finitePrimeDiscover 5 5 4 (fun a => rowRight (c170_A a)) c170_O = some c170_result :=
  replaySource_reference 5 5 4 (by decide +kernel) c170_A c170_O c170_evidence c170_result c170_checked_data
theorem c170_all_words (x y : Fin 4 → c170_R) :
    CodeEqual (linearSystem c170_A c170_O) c170_result x y ↔ ObsEq (linearSystem c170_A c170_O) x y :=
  replaySource_all_words c170_A c170_O c170_evidence c170_result c170_checked_data x y
theorem c170_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c170_R) c170_R) :
    taggedRealize (linearSystem c170_A c170_O) (guardedCodeFormula c170_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c170_A c170_O) :=
  replaySource_standard_formula c170_A c170_O c170_evidence c170_result c170_checked_data e
abbrev c171_R := ZMod 2
def c171_A : Fin 1 → Mat c171_R 5 5 := ![![![0, 0, 0, 0, 1], ![0, 0, 0, 0, 1], ![0, 1, 1, 1, 1], ![0, 0, 0, 1, 0], ![1, 1, 0, 0, 0]]]
def c171_O : Mat c171_R 1 5 := ![![1, 1, 1, 1, 1]]
def c171_evidence : List (Evidence c171_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0]),
  .separation (![0, 1, 0, 1, 0]),
  .separation (![1, 0, 1, 0, 0]),
  .separation (![0, 1, 1, 1, 1]),
  .combination [0, 0, 0, 1, 0]]
def c171_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c171_checked_data : replaySource c171_A c171_O c171_evidence = some c171_result := by decide +kernel
theorem c171_reference_result :
    finitePrimeDiscover 2 1 5 (fun a => rowRight (c171_A a)) c171_O = some c171_result :=
  replaySource_reference 2 1 5 (by decide +kernel) c171_A c171_O c171_evidence c171_result c171_checked_data
theorem c171_all_words (x y : Fin 5 → c171_R) :
    CodeEqual (linearSystem c171_A c171_O) c171_result x y ↔ ObsEq (linearSystem c171_A c171_O) x y :=
  replaySource_all_words c171_A c171_O c171_evidence c171_result c171_checked_data x y
theorem c171_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c171_R) c171_R) :
    taggedRealize (linearSystem c171_A c171_O) (guardedCodeFormula c171_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c171_A c171_O) :=
  replaySource_standard_formula c171_A c171_O c171_evidence c171_result c171_checked_data e
abbrev c172_R := ZMod 3
def c172_A : Fin 2 → Mat c172_R 5 5 := ![![![0, 0, 1, 2, 1], ![1, 1, 1, 1, 0], ![1, 2, 2, 0, 1], ![0, 0, 2, 0, 1], ![2, 1, 2, 1, 1]], ![![0, 0, 0, 2, 2], ![2, 1, 2, 1, 0], ![1, 2, 1, 0, 0], ![1, 1, 2, 1, 1], ![0, 2, 2, 0, 1]]]
def c172_O : Mat c172_R 2 5 := ![![0, 0, 1, 0, 0], ![0, 2, 2, 0, 2]]
def c172_evidence : List (Evidence c172_R 5) := [
  .separation (![0, 0, 1, 0, 0]),
  .separation (![0, 1, 0, 0, 0]),
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 2, 0, 0, 1]),
  .separation (![0, 0, 0, 1, 0]),
  .combination [0, 1, 1, 1, 2],
  .combination [0, 1, 0, 2, 2],
  .combination [1, 2, 1, 0, 1],
  .combination [2, 0, 1, 0, 1],
  .combination [0, 1, 2, 1, 1],
  .combination [2, 0, 1, 2, 1],
  .combination [2, 0, 2, 2, 1]]
def c172_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c172_checked_data : replaySource c172_A c172_O c172_evidence = some c172_result := by decide +kernel
theorem c172_reference_result :
    finitePrimeDiscover 3 1 5 (fun a => rowRight (c172_A a)) c172_O = some c172_result :=
  replaySource_reference 3 1 5 (by decide +kernel) c172_A c172_O c172_evidence c172_result c172_checked_data
theorem c172_all_words (x y : Fin 5 → c172_R) :
    CodeEqual (linearSystem c172_A c172_O) c172_result x y ↔ ObsEq (linearSystem c172_A c172_O) x y :=
  replaySource_all_words c172_A c172_O c172_evidence c172_result c172_checked_data x y
theorem c172_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c172_R) c172_R) :
    taggedRealize (linearSystem c172_A c172_O) (guardedCodeFormula c172_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c172_A c172_O) :=
  replaySource_standard_formula c172_A c172_O c172_evidence c172_result c172_checked_data e
abbrev c173_R := ZMod 5
def c173_A : Fin 3 → Mat c173_R 5 5 := ![![![0, 2, 0, 3, 2], ![0, 2, 3, 1, 1], ![2, 3, 1, 2, 4], ![3, 0, 3, 1, 3], ![1, 2, 2, 4, 2]], ![![1, 1, 3, 0, 1], ![2, 2, 0, 3, 2], ![3, 4, 1, 4, 1], ![2, 3, 4, 1, 3], ![0, 4, 3, 1, 2]], ![![3, 2, 4, 2, 1], ![3, 0, 2, 4, 2], ![4, 1, 4, 1, 1], ![0, 3, 4, 2, 3], ![4, 2, 0, 2, 2]]]
def c173_O : Mat c173_R 1 5 := ![![1, 4, 0, 0, 4]]
def c173_evidence : List (Evidence c173_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0]),
  .combination [1, 2],
  .separation (![0, 0, 1, 0, 0]),
  .separation (![1, 1, 4, 1, 0]),
  .separation (![4, 3, 1, 2, 1]),
  .combination [1, 0, 4, 3, 3],
  .combination [3, 1, 4, 1, 0],
  .combination [1, 3, 1, 1, 2],
  .combination [4, 3, 4, 3, 0],
  .combination [0, 4, 1, 1, 2],
  .combination [2, 3, 4, 4, 3],
  .combination [4, 4, 2, 1, 1],
  .combination [0, 0, 0, 2, 1],
  .combination [4, 3, 0, 3, 1],
  .combination [2, 1, 2, 2, 1]]
def c173_result : List (Test 3 1) := [([], 0), ([0], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c173_checked_data : replaySource c173_A c173_O c173_evidence = some c173_result := by decide +kernel
theorem c173_reference_result :
    finitePrimeDiscover 5 1 5 (fun a => rowRight (c173_A a)) c173_O = some c173_result :=
  replaySource_reference 5 1 5 (by decide +kernel) c173_A c173_O c173_evidence c173_result c173_checked_data
theorem c173_all_words (x y : Fin 5 → c173_R) :
    CodeEqual (linearSystem c173_A c173_O) c173_result x y ↔ ObsEq (linearSystem c173_A c173_O) x y :=
  replaySource_all_words c173_A c173_O c173_evidence c173_result c173_checked_data x y
theorem c173_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c173_R) c173_R) :
    taggedRealize (linearSystem c173_A c173_O) (guardedCodeFormula c173_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c173_A c173_O) :=
  replaySource_standard_formula c173_A c173_O c173_evidence c173_result c173_checked_data e
abbrev c174_R := ZMod 4
def c174_A : Fin 1 → Mat c174_R 5 5 := ![![![1, 0, 2, 1, 3], ![3, 1, 2, 0, 1], ![2, 0, 2, 2, 2], ![2, 3, 0, 2, 0], ![2, 3, 2, 2, 0]]]
def c174_O : Mat c174_R 2 5 := ![![1, 3, 3, 0, 3], ![2, 1, 3, 3, 2]]
def c174_evidence : List (Evidence c174_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0]),
  .separation (![3, 3, 0, 1, 0]),
  .separation (![2, 1, 1, 0, 0]),
  .separation (![0, 2, 2, 0, 0]),
  .combination [1, 3, 2, 0, 1],
  .combination [1, 1, 1, 0, 3]]
def c174_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c174_checked_data : replaySource c174_A c174_O c174_evidence = some c174_result := by decide +kernel
theorem c174_reference_result :
    finitePrimeDiscover 2 2 5 (fun a => rowRight (c174_A a)) c174_O = some c174_result :=
  replaySource_reference 2 2 5 (by decide +kernel) c174_A c174_O c174_evidence c174_result c174_checked_data
theorem c174_all_words (x y : Fin 5 → c174_R) :
    CodeEqual (linearSystem c174_A c174_O) c174_result x y ↔ ObsEq (linearSystem c174_A c174_O) x y :=
  replaySource_all_words c174_A c174_O c174_evidence c174_result c174_checked_data x y
theorem c174_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c174_R) c174_R) :
    taggedRealize (linearSystem c174_A c174_O) (guardedCodeFormula c174_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c174_A c174_O) :=
  replaySource_standard_formula c174_A c174_O c174_evidence c174_result c174_checked_data e
abbrev c175_R := ZMod 9
def c175_A : Fin 2 → Mat c175_R 5 5 := ![![![7, 6, 5, 8, 1], ![3, 1, 2, 2, 7], ![8, 4, 2, 1, 6], ![3, 1, 7, 6, 7], ![7, 6, 7, 8, 4]], ![![6, 2, 8, 1, 5], ![4, 7, 8, 6, 0], ![2, 1, 8, 2, 3], ![1, 7, 4, 0, 8], ![6, 0, 3, 8, 0]]]
def c175_O : Mat c175_R 1 5 := ![![6, 6, 6, 3, 0]]
def c175_evidence : List (Evidence c175_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![8, 1, 0, 0, 0]),
  .separation (![1, 7, 1, 0, 0]),
  .separation (![0, 7, 0, 1, 0]),
  .combination [3, 6, 4, 1],
  .separation (![8, 5, 7, 8, 1]),
  .combination [6, 0, 0, 8, 1],
  .combination [7, 4, 5, 8, 1],
  .combination [0, 2, 8, 2, 0],
  .combination [2, 6, 4, 1, 0],
  .combination [5, 5, 0, 8, 1]]
def c175_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([0,1], 0)]
theorem c175_checked_data : replaySource c175_A c175_O c175_evidence = some c175_result := by decide +kernel
theorem c175_reference_result :
    finitePrimeDiscover 3 2 5 (fun a => rowRight (c175_A a)) c175_O = some c175_result :=
  replaySource_reference 3 2 5 (by decide +kernel) c175_A c175_O c175_evidence c175_result c175_checked_data
theorem c175_all_words (x y : Fin 5 → c175_R) :
    CodeEqual (linearSystem c175_A c175_O) c175_result x y ↔ ObsEq (linearSystem c175_A c175_O) x y :=
  replaySource_all_words c175_A c175_O c175_evidence c175_result c175_checked_data x y
theorem c175_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c175_R) c175_R) :
    taggedRealize (linearSystem c175_A c175_O) (guardedCodeFormula c175_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c175_A c175_O) :=
  replaySource_standard_formula c175_A c175_O c175_evidence c175_result c175_checked_data e
abbrev c176_R := ZMod 25
def c176_A : Fin 3 → Mat c176_R 5 5 := ![![![8, 3, 20, 15, 0], ![10, 17, 7, 17, 23], ![23, 14, 8, 4, 4], ![18, 10, 21, 8, 2], ![17, 4, 18, 8, 13]], ![![22, 14, 5, 15, 8], ![5, 15, 1, 4, 20], ![24, 12, 23, 2, 21], ![10, 9, 5, 18, 21], ![11, 16, 16, 22, 23]], ![![10, 24, 10, 3, 23], ![0, 6, 22, 11, 3], ![21, 15, 20, 0, 11], ![9, 14, 20, 21, 9], ![2, 13, 10, 2, 8]]]
def c176_O : Mat c176_R 2 5 := ![![14, 15, 6, 2, 19], ![11, 22, 22, 4, 19]]
def c176_evidence : List (Evidence c176_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![15, 1, 0, 0, 0]),
  .separation (![11, 6, 1, 0, 0]),
  .separation (![19, 9, 12, 1, 0]),
  .separation (![10, 17, 5, 3, 1]),
  .combination [18, 21, 5, 18, 9],
  .combination [16, 8, 2, 18, 3],
  .combination [9, 10, 13, 2, 23],
  .combination [11, 3, 24, 6, 5],
  .combination [3, 17, 9, 19, 6],
  .combination [3, 16, 3, 9, 8],
  .combination [10, 18, 4, 7, 10],
  .combination [15, 4, 19, 1, 13],
  .combination [15, 24, 12, 9, 22],
  .combination [4, 2, 22, 3, 2],
  .combination [20, 10, 18, 24, 8],
  .combination [23, 1, 3, 8, 18]]
def c176_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)]
theorem c176_checked_data : replaySource c176_A c176_O c176_evidence = some c176_result := by decide +kernel
theorem c176_reference_result :
    finitePrimeDiscover 5 2 5 (fun a => rowRight (c176_A a)) c176_O = some c176_result :=
  replaySource_reference 5 2 5 (by decide +kernel) c176_A c176_O c176_evidence c176_result c176_checked_data
theorem c176_all_words (x y : Fin 5 → c176_R) :
    CodeEqual (linearSystem c176_A c176_O) c176_result x y ↔ ObsEq (linearSystem c176_A c176_O) x y :=
  replaySource_all_words c176_A c176_O c176_evidence c176_result c176_checked_data x y
theorem c176_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c176_R) c176_R) :
    taggedRealize (linearSystem c176_A c176_O) (guardedCodeFormula c176_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c176_A c176_O) :=
  replaySource_standard_formula c176_A c176_O c176_evidence c176_result c176_checked_data e
abbrev c177_R := ZMod 8
def c177_A : Fin 1 → Mat c177_R 5 5 := ![![![6, 2, 6, 0, 0], ![1, 0, 4, 1, 7], ![4, 7, 0, 0, 7], ![2, 3, 6, 4, 2], ![0, 1, 4, 3, 3]]]
def c177_O : Mat c177_R 1 5 := ![![0, 0, 0, 0, 0]]
def c177_evidence : List (Evidence c177_R 5) := [
  .combination []]
def c177_result : List (Test 1 1) := []
theorem c177_checked_data : replaySource c177_A c177_O c177_evidence = some c177_result := by decide +kernel
theorem c177_reference_result :
    finitePrimeDiscover 2 3 5 (fun a => rowRight (c177_A a)) c177_O = some c177_result :=
  replaySource_reference 2 3 5 (by decide +kernel) c177_A c177_O c177_evidence c177_result c177_checked_data
theorem c177_all_words (x y : Fin 5 → c177_R) :
    CodeEqual (linearSystem c177_A c177_O) c177_result x y ↔ ObsEq (linearSystem c177_A c177_O) x y :=
  replaySource_all_words c177_A c177_O c177_evidence c177_result c177_checked_data x y
theorem c177_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c177_R) c177_R) :
    taggedRealize (linearSystem c177_A c177_O) (guardedCodeFormula c177_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c177_A c177_O) :=
  replaySource_standard_formula c177_A c177_O c177_evidence c177_result c177_checked_data e
abbrev c178_R := ZMod 27
def c178_A : Fin 2 → Mat c178_R 5 5 := ![![![9, 26, 6, 11, 22], ![5, 3, 16, 21, 5], ![20, 21, 14, 18, 23], ![22, 10, 10, 0, 11], ![4, 1, 18, 10, 24]], ![![11, 7, 16, 1, 12], ![13, 23, 3, 6, 16], ![18, 0, 21, 9, 3], ![23, 19, 18, 12, 1], ![15, 18, 12, 9, 17]]]
def c178_O : Mat c178_R 2 5 := ![![1, 26, 5, 18, 8], ![1, 8, 11, 8, 14]]
def c178_evidence : List (Evidence c178_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0]),
  .separation (![22, 0, 1, 6, 0]),
  .separation (![23, 1, 1, 15, 0]),
  .separation (![10, 17, 16, 12, 1]),
  .separation (![9, 18, 9, 0, 9]),
  .combination [0, 21, 0, 25, 0, 7],
  .combination [15, 12, 9, 15, 0, 7],
  .combination [7, 26, 8, 20, 0, 0],
  .combination [12, 23, 15, 5, 0, 13],
  .combination [7, 20, 10, 2, 0, 18],
  .combination [3, 11, 6, 1, 0, 1],
  .combination [7, 6, 4, 8, 0, 9],
  .combination [18, 26, 24, 18, 0, 16]]
def c178_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem c178_checked_data : replaySource c178_A c178_O c178_evidence = some c178_result := by decide +kernel
theorem c178_reference_result :
    finitePrimeDiscover 3 3 5 (fun a => rowRight (c178_A a)) c178_O = some c178_result :=
  replaySource_reference 3 3 5 (by decide +kernel) c178_A c178_O c178_evidence c178_result c178_checked_data
theorem c178_all_words (x y : Fin 5 → c178_R) :
    CodeEqual (linearSystem c178_A c178_O) c178_result x y ↔ ObsEq (linearSystem c178_A c178_O) x y :=
  replaySource_all_words c178_A c178_O c178_evidence c178_result c178_checked_data x y
theorem c178_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c178_R) c178_R) :
    taggedRealize (linearSystem c178_A c178_O) (guardedCodeFormula c178_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c178_A c178_O) :=
  replaySource_standard_formula c178_A c178_O c178_evidence c178_result c178_checked_data e
abbrev c179_R := ZMod 125
def c179_A : Fin 3 → Mat c179_R 5 5 := ![![![32, 102, 60, 71, 42], ![88, 6, 107, 17, 38], ![29, 84, 118, 61, 84], ![52, 65, 94, 65, 43], ![68, 84, 122, 55, 44]], ![![86, 96, 83, 4, 9], ![58, 110, 97, 87, 94], ![53, 24, 18, 6, 39], ![104, 47, 51, 52, 67], ![45, 102, 67, 16, 95]], ![![16, 104, 75, 74, 22], ![74, 42, 118, 43, 116], ![48, 29, 7, 71, 96], ![69, 101, 1, 22, 98], ![61, 24, 89, 66, 22]]]
def c179_O : Mat c179_R 1 5 := ![![26, 33, 34, 59, 59]]
def c179_evidence : List (Evidence c179_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![42, 1, 0, 0, 0]),
  .separation (![13, 91, 1, 0, 0]),
  .separation (![113, 71, 1, 90, 0]),
  .separation (![80, 69, 16, 60, 1]),
  .combination [95, 86, 7, 70, 66],
  .combination [37, 7, 73, 38, 66],
  .combination [37, 11, 55, 116, 13],
  .combination [70, 89, 124, 28, 111],
  .combination [63, 83, 48, 67, 95],
  .combination [8, 21, 52, 124, 71],
  .combination [64, 76, 58, 57, 26],
  .combination [28, 30, 109, 84, 110],
  .combination [103, 123, 46, 52, 86],
  .combination [41, 89, 99, 5, 94],
  .combination [29, 60, 59, 107, 95]]
def c179_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c179_checked_data : replaySource c179_A c179_O c179_evidence = some c179_result := by decide +kernel
theorem c179_reference_result :
    finitePrimeDiscover 5 3 5 (fun a => rowRight (c179_A a)) c179_O = some c179_result :=
  replaySource_reference 5 3 5 (by decide +kernel) c179_A c179_O c179_evidence c179_result c179_checked_data
theorem c179_all_words (x y : Fin 5 → c179_R) :
    CodeEqual (linearSystem c179_A c179_O) c179_result x y ↔ ObsEq (linearSystem c179_A c179_O) x y :=
  replaySource_all_words c179_A c179_O c179_evidence c179_result c179_checked_data x y
theorem c179_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c179_R) c179_R) :
    taggedRealize (linearSystem c179_A c179_O) (guardedCodeFormula c179_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c179_A c179_O) :=
  replaySource_standard_formula c179_A c179_O c179_evidence c179_result c179_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch14
