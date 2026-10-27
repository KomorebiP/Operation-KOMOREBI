module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch05
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c060_R := ZMod 16
def c060_A : Fin 1 → Mat c060_R 3 3 := ![![![15, 5, 9], ![14, 6, 5], ![15, 7, 2]]]
def c060_O : Mat c060_R 2 3 := ![![0, 0, 0], ![0, 0, 0]]
def c060_evidence : List (Evidence c060_R 3) := [
  .combination [],
  .combination []]
def c060_result : List (Test 1 2) := []
theorem c060_checked_data : replaySource c060_A c060_O c060_evidence = some c060_result := by decide +kernel
theorem c060_reference_result :
    finitePrimeDiscover 2 4 3 (fun a => rowRight (c060_A a)) c060_O = some c060_result :=
  replaySource_reference 2 4 3 (by decide +kernel) c060_A c060_O c060_evidence c060_result c060_checked_data
theorem c060_all_words (x y : Fin 3 → c060_R) :
    CodeEqual (linearSystem c060_A c060_O) c060_result x y ↔ ObsEq (linearSystem c060_A c060_O) x y :=
  replaySource_all_words c060_A c060_O c060_evidence c060_result c060_checked_data x y
theorem c060_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c060_R) c060_R) :
    taggedRealize (linearSystem c060_A c060_O) (guardedCodeFormula c060_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c060_A c060_O) :=
  replaySource_standard_formula c060_A c060_O c060_evidence c060_result c060_checked_data e
abbrev c061_R := ZMod 81
def c061_A : Fin 2 → Mat c061_R 3 3 := ![![![9, 78, 10], ![48, 19, 63], ![34, 28, 75]], ![![53, 1, 76], ![6, 14, 48], ![5, 18, 9]]]
def c061_O : Mat c061_R 1 3 := ![![76, 64, 33]]
def c061_evidence : List (Evidence c061_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![29, 1, 0]),
  .separation (![37, 53, 1]),
  .separation (![27, 54, 27]),
  .combination [38, 18, 0, 27],
  .combination [69, 80, 0, 7],
  .combination [6, 68, 0, 12],
  .combination [41, 13, 0, 22],
  .combination [54, 4, 0, 71]]
def c061_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c061_checked_data : replaySource c061_A c061_O c061_evidence = some c061_result := by decide +kernel
theorem c061_reference_result :
    finitePrimeDiscover 3 4 3 (fun a => rowRight (c061_A a)) c061_O = some c061_result :=
  replaySource_reference 3 4 3 (by decide +kernel) c061_A c061_O c061_evidence c061_result c061_checked_data
theorem c061_all_words (x y : Fin 3 → c061_R) :
    CodeEqual (linearSystem c061_A c061_O) c061_result x y ↔ ObsEq (linearSystem c061_A c061_O) x y :=
  replaySource_all_words c061_A c061_O c061_evidence c061_result c061_checked_data x y
theorem c061_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c061_R) c061_R) :
    taggedRealize (linearSystem c061_A c061_O) (guardedCodeFormula c061_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c061_A c061_O) :=
  replaySource_standard_formula c061_A c061_O c061_evidence c061_result c061_checked_data e
abbrev c062_R := ZMod 625
def c062_A : Fin 3 → Mat c062_R 3 3 := ![![![160, 517, 144], ![590, 142, 456], ![497, 266, 206]], ![![136, 113, 520], ![493, 130, 537], ![535, 151, 204]], ![![282, 292, 605], ![375, 467, 617], ![485, 126, 288]]]
def c062_O : Mat c062_R 2 3 := ![![89, 88, 344], ![264, 398, 38]]
def c062_evidence : List (Evidence c062_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![308, 1, 0]),
  .separation (![73, 1, 535]),
  .combination [401, 46, 565],
  .combination [390, 405, 186],
  .combination [435, 114, 295],
  .combination [343, 190, 212],
  .combination [93, 478, 428],
  .combination [118, 253, 394],
  .combination [91, 374, 504],
  .combination [140, 456, 169]]
def c062_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c062_checked_data : replaySource c062_A c062_O c062_evidence = some c062_result := by decide +kernel
theorem c062_reference_result :
    finitePrimeDiscover 5 4 3 (fun a => rowRight (c062_A a)) c062_O = some c062_result :=
  replaySource_reference 5 4 3 (by decide +kernel) c062_A c062_O c062_evidence c062_result c062_checked_data
theorem c062_all_words (x y : Fin 3 → c062_R) :
    CodeEqual (linearSystem c062_A c062_O) c062_result x y ↔ ObsEq (linearSystem c062_A c062_O) x y :=
  replaySource_all_words c062_A c062_O c062_evidence c062_result c062_checked_data x y
theorem c062_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c062_R) c062_R) :
    taggedRealize (linearSystem c062_A c062_O) (guardedCodeFormula c062_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c062_A c062_O) :=
  replaySource_standard_formula c062_A c062_O c062_evidence c062_result c062_checked_data e
abbrev c063_R := ZMod 32
def c063_A : Fin 1 → Mat c063_R 3 3 := ![![![13, 29, 18], ![0, 8, 25], ![5, 2, 10]]]
def c063_O : Mat c063_R 1 3 := ![![16, 16, 0]]
def c063_evidence : List (Evidence c063_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![0, 0, 1]),
  .separation (![31, 1, 0]),
  .combination [1, 0, 1]]
def c063_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c063_checked_data : replaySource c063_A c063_O c063_evidence = some c063_result := by decide +kernel
theorem c063_reference_result :
    finitePrimeDiscover 2 5 3 (fun a => rowRight (c063_A a)) c063_O = some c063_result :=
  replaySource_reference 2 5 3 (by decide +kernel) c063_A c063_O c063_evidence c063_result c063_checked_data
theorem c063_all_words (x y : Fin 3 → c063_R) :
    CodeEqual (linearSystem c063_A c063_O) c063_result x y ↔ ObsEq (linearSystem c063_A c063_O) x y :=
  replaySource_all_words c063_A c063_O c063_evidence c063_result c063_checked_data x y
theorem c063_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c063_R) c063_R) :
    taggedRealize (linearSystem c063_A c063_O) (guardedCodeFormula c063_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c063_A c063_O) :=
  replaySource_standard_formula c063_A c063_O c063_evidence c063_result c063_checked_data e
abbrev c064_R := ZMod 243
def c064_A : Fin 2 → Mat c064_R 3 3 := ![![![210, 234, 106], ![198, 108, 88], ![31, 167, 0]], ![![134, 136, 111], ![198, 36, 175], ![121, 87, 5]]]
def c064_O : Mat c064_R 2 3 := ![![218, 69, 14], ![193, 136, 176]]
def c064_evidence : List (Evidence c064_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![168, 1, 0]),
  .separation (![59, 74, 1]),
  .combination [90, 25, 64],
  .combination [48, 108, 127],
  .combination [138, 214, 216],
  .combination [203, 103, 210],
  .combination [134, 38, 114]]
def c064_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c064_checked_data : replaySource c064_A c064_O c064_evidence = some c064_result := by decide +kernel
theorem c064_reference_result :
    finitePrimeDiscover 3 5 3 (fun a => rowRight (c064_A a)) c064_O = some c064_result :=
  replaySource_reference 3 5 3 (by decide +kernel) c064_A c064_O c064_evidence c064_result c064_checked_data
theorem c064_all_words (x y : Fin 3 → c064_R) :
    CodeEqual (linearSystem c064_A c064_O) c064_result x y ↔ ObsEq (linearSystem c064_A c064_O) x y :=
  replaySource_all_words c064_A c064_O c064_evidence c064_result c064_checked_data x y
theorem c064_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c064_R) c064_R) :
    taggedRealize (linearSystem c064_A c064_O) (guardedCodeFormula c064_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c064_A c064_O) :=
  replaySource_standard_formula c064_A c064_O c064_evidence c064_result c064_checked_data e
abbrev c065_R := ZMod 3125
def c065_A : Fin 3 → Mat c065_R 3 3 := ![![![2173, 2544, 1397], ![1021, 486, 1535], ![1572, 361, 2817]], ![![2288, 2418, 2357], ![2124, 1439, 652], ![718, 1107, 2369]], ![![2742, 560, 1777], ![1221, 571, 2366], ![20, 2849, 1531]]]
def c065_O : Mat c065_R 1 3 := ![![2434, 1545, 60]]
def c065_evidence : List (Evidence c065_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![1870, 1, 0]),
  .separation (![2250, 982, 1]),
  .combination [1794, 782, 1624],
  .combination [1852, 2928, 2382],
  .combination [1618, 951, 825],
  .combination [2617, 2134, 177],
  .combination [1171, 2872, 2548],
  .combination [1122, 3100, 2020],
  .combination [2475, 1862, 916]]
def c065_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c065_checked_data : replaySource c065_A c065_O c065_evidence = some c065_result := by decide +kernel
theorem c065_reference_result :
    finitePrimeDiscover 5 5 3 (fun a => rowRight (c065_A a)) c065_O = some c065_result :=
  replaySource_reference 5 5 3 (by decide +kernel) c065_A c065_O c065_evidence c065_result c065_checked_data
theorem c065_all_words (x y : Fin 3 → c065_R) :
    CodeEqual (linearSystem c065_A c065_O) c065_result x y ↔ ObsEq (linearSystem c065_A c065_O) x y :=
  replaySource_all_words c065_A c065_O c065_evidence c065_result c065_checked_data x y
theorem c065_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c065_R) c065_R) :
    taggedRealize (linearSystem c065_A c065_O) (guardedCodeFormula c065_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c065_A c065_O) :=
  replaySource_standard_formula c065_A c065_O c065_evidence c065_result c065_checked_data e
abbrev c066_R := ZMod 2
def c066_A : Fin 1 → Mat c066_R 4 4 := ![![![1, 1, 0, 1], ![0, 1, 1, 1], ![0, 1, 1, 0], ![0, 0, 1, 0]]]
def c066_O : Mat c066_R 2 4 := ![![0, 1, 1, 1], ![0, 0, 0, 1]]
def c066_evidence : List (Evidence c066_R 4) := [
  .separation (![0, 1, 0, 0]),
  .separation (![0, 1, 0, 1]),
  .separation (![0, 1, 1, 0]),
  .combination [0, 1, 1],
  .combination [1, 0, 1]]
def c066_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c066_checked_data : replaySource c066_A c066_O c066_evidence = some c066_result := by decide +kernel
theorem c066_reference_result :
    finitePrimeDiscover 2 1 4 (fun a => rowRight (c066_A a)) c066_O = some c066_result :=
  replaySource_reference 2 1 4 (by decide +kernel) c066_A c066_O c066_evidence c066_result c066_checked_data
theorem c066_all_words (x y : Fin 4 → c066_R) :
    CodeEqual (linearSystem c066_A c066_O) c066_result x y ↔ ObsEq (linearSystem c066_A c066_O) x y :=
  replaySource_all_words c066_A c066_O c066_evidence c066_result c066_checked_data x y
theorem c066_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c066_R) c066_R) :
    taggedRealize (linearSystem c066_A c066_O) (guardedCodeFormula c066_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c066_A c066_O) :=
  replaySource_standard_formula c066_A c066_O c066_evidence c066_result c066_checked_data e
abbrev c067_R := ZMod 3
def c067_A : Fin 2 → Mat c067_R 4 4 := ![![![1, 1, 2, 1], ![2, 2, 1, 2], ![0, 0, 1, 1], ![0, 0, 0, 1]], ![![2, 1, 0, 0], ![0, 1, 2, 1], ![2, 1, 2, 0], ![2, 2, 1, 1]]]
def c067_O : Mat c067_R 1 4 := ![![2, 2, 2, 2]]
def c067_evidence : List (Evidence c067_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![2, 0, 1, 0]),
  .separation (![2, 1, 0, 0]),
  .separation (![0, 1, 1, 1]),
  .combination [0, 0, 1, 2],
  .combination [1, 2, 0, 1],
  .combination [2, 1, 0, 1],
  .combination [0, 2, 0, 2],
  .combination [2, 1, 1, 0]]
def c067_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c067_checked_data : replaySource c067_A c067_O c067_evidence = some c067_result := by decide +kernel
theorem c067_reference_result :
    finitePrimeDiscover 3 1 4 (fun a => rowRight (c067_A a)) c067_O = some c067_result :=
  replaySource_reference 3 1 4 (by decide +kernel) c067_A c067_O c067_evidence c067_result c067_checked_data
theorem c067_all_words (x y : Fin 4 → c067_R) :
    CodeEqual (linearSystem c067_A c067_O) c067_result x y ↔ ObsEq (linearSystem c067_A c067_O) x y :=
  replaySource_all_words c067_A c067_O c067_evidence c067_result c067_checked_data x y
theorem c067_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c067_R) c067_R) :
    taggedRealize (linearSystem c067_A c067_O) (guardedCodeFormula c067_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c067_A c067_O) :=
  replaySource_standard_formula c067_A c067_O c067_evidence c067_result c067_checked_data e
abbrev c068_R := ZMod 5
def c068_A : Fin 3 → Mat c068_R 4 4 := ![![![0, 2, 0, 0], ![3, 0, 2, 0], ![3, 3, 1, 4], ![0, 3, 3, 0]], ![![1, 0, 3, 0], ![3, 1, 4, 1], ![0, 1, 0, 1], ![1, 1, 0, 2]], ![![2, 0, 4, 0], ![0, 2, 3, 1], ![3, 4, 3, 2], ![0, 2, 3, 3]]]
def c068_O : Mat c068_R 2 4 := ![![3, 3, 3, 3], ![4, 4, 2, 3]]
def c068_evidence : List (Evidence c068_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![4, 0, 1, 0]),
  .separation (![4, 1, 0, 0]),
  .separation (![1, 1, 2, 1]),
  .combination [2, 3, 4, 0],
  .combination [0, 4, 4, 4],
  .combination [4, 4, 2, 2],
  .combination [1, 2, 1, 3],
  .combination [1, 0, 1, 1],
  .combination [4, 3, 1, 4],
  .combination [2, 1, 0, 1],
  .combination [1, 3, 0, 1],
  .combination [3, 1, 2, 4],
  .combination [0, 4, 4, 1]]
def c068_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem c068_checked_data : replaySource c068_A c068_O c068_evidence = some c068_result := by decide +kernel
theorem c068_reference_result :
    finitePrimeDiscover 5 1 4 (fun a => rowRight (c068_A a)) c068_O = some c068_result :=
  replaySource_reference 5 1 4 (by decide +kernel) c068_A c068_O c068_evidence c068_result c068_checked_data
theorem c068_all_words (x y : Fin 4 → c068_R) :
    CodeEqual (linearSystem c068_A c068_O) c068_result x y ↔ ObsEq (linearSystem c068_A c068_O) x y :=
  replaySource_all_words c068_A c068_O c068_evidence c068_result c068_checked_data x y
theorem c068_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c068_R) c068_R) :
    taggedRealize (linearSystem c068_A c068_O) (guardedCodeFormula c068_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c068_A c068_O) :=
  replaySource_standard_formula c068_A c068_O c068_evidence c068_result c068_checked_data e
abbrev c069_R := ZMod 4
def c069_A : Fin 1 → Mat c069_R 4 4 := ![![![0, 3, 1, 3], ![3, 2, 2, 0], ![2, 1, 2, 3], ![0, 3, 2, 1]]]
def c069_O : Mat c069_R 1 4 := ![![1, 1, 3, 1]]
def c069_evidence : List (Evidence c069_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![3, 1, 0, 0]),
  .separation (![1, 0, 1, 0]),
  .combination [2, 1, 0]]
def c069_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c069_checked_data : replaySource c069_A c069_O c069_evidence = some c069_result := by decide +kernel
theorem c069_reference_result :
    finitePrimeDiscover 2 2 4 (fun a => rowRight (c069_A a)) c069_O = some c069_result :=
  replaySource_reference 2 2 4 (by decide +kernel) c069_A c069_O c069_evidence c069_result c069_checked_data
theorem c069_all_words (x y : Fin 4 → c069_R) :
    CodeEqual (linearSystem c069_A c069_O) c069_result x y ↔ ObsEq (linearSystem c069_A c069_O) x y :=
  replaySource_all_words c069_A c069_O c069_evidence c069_result c069_checked_data x y
theorem c069_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c069_R) c069_R) :
    taggedRealize (linearSystem c069_A c069_O) (guardedCodeFormula c069_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c069_A c069_O) :=
  replaySource_standard_formula c069_A c069_O c069_evidence c069_result c069_checked_data e
abbrev c070_R := ZMod 9
def c070_A : Fin 2 → Mat c070_R 4 4 := ![![![4, 2, 3, 1], ![0, 2, 3, 5], ![0, 4, 1, 5], ![3, 2, 2, 3]], ![![6, 7, 4, 4], ![3, 4, 5, 3], ![6, 8, 3, 4], ![5, 4, 3, 6]]]
def c070_O : Mat c070_R 2 4 := ![![3, 6, 3, 3], ![3, 0, 3, 3]]
def c070_evidence : List (Evidence c070_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![7, 1, 0, 0]),
  .separation (![8, 0, 1, 0]),
  .combination [0, 2, 0],
  .separation (![8, 0, 0, 1]),
  .combination [2, 8, 1, 0],
  .combination [8, 6, 5, 0],
  .combination [0, 1, 0, 1],
  .combination [4, 5, 5, 5],
  .combination [4, 4, 5, 5]]
def c070_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c070_checked_data : replaySource c070_A c070_O c070_evidence = some c070_result := by decide +kernel
theorem c070_reference_result :
    finitePrimeDiscover 3 2 4 (fun a => rowRight (c070_A a)) c070_O = some c070_result :=
  replaySource_reference 3 2 4 (by decide +kernel) c070_A c070_O c070_evidence c070_result c070_checked_data
theorem c070_all_words (x y : Fin 4 → c070_R) :
    CodeEqual (linearSystem c070_A c070_O) c070_result x y ↔ ObsEq (linearSystem c070_A c070_O) x y :=
  replaySource_all_words c070_A c070_O c070_evidence c070_result c070_checked_data x y
theorem c070_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c070_R) c070_R) :
    taggedRealize (linearSystem c070_A c070_O) (guardedCodeFormula c070_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c070_A c070_O) :=
  replaySource_standard_formula c070_A c070_O c070_evidence c070_result c070_checked_data e
abbrev c071_R := ZMod 25
def c071_A : Fin 3 → Mat c071_R 4 4 := ![![![2, 3, 23, 12], ![12, 8, 13, 2], ![12, 16, 15, 17], ![16, 6, 12, 11]], ![![14, 10, 3, 5], ![10, 7, 0, 10], ![1, 19, 14, 8], ![15, 1, 12, 12]], ![![19, 24, 18, 22], ![12, 7, 5, 19], ![23, 15, 5, 19], ![22, 17, 8, 6]]]
def c071_O : Mat c071_R 1 4 := ![![1, 8, 11, 6]]
def c071_evidence : List (Evidence c071_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![17, 1, 0, 0]),
  .separation (![8, 7, 1, 0]),
  .separation (![19, 0, 0, 1]),
  .combination [20, 14, 14, 10],
  .combination [20, 13, 20, 24],
  .combination [24, 7, 22, 21],
  .combination [20, 20, 12, 15],
  .combination [1, 13, 24, 22],
  .combination [8, 6, 6, 9],
  .combination [15, 15, 11, 10],
  .combination [21, 15, 14, 10],
  .combination [12, 3, 1, 24]]
def c071_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c071_checked_data : replaySource c071_A c071_O c071_evidence = some c071_result := by decide +kernel
theorem c071_reference_result :
    finitePrimeDiscover 5 2 4 (fun a => rowRight (c071_A a)) c071_O = some c071_result :=
  replaySource_reference 5 2 4 (by decide +kernel) c071_A c071_O c071_evidence c071_result c071_checked_data
theorem c071_all_words (x y : Fin 4 → c071_R) :
    CodeEqual (linearSystem c071_A c071_O) c071_result x y ↔ ObsEq (linearSystem c071_A c071_O) x y :=
  replaySource_all_words c071_A c071_O c071_evidence c071_result c071_checked_data x y
theorem c071_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c071_R) c071_R) :
    taggedRealize (linearSystem c071_A c071_O) (guardedCodeFormula c071_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c071_A c071_O) :=
  replaySource_standard_formula c071_A c071_O c071_evidence c071_result c071_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch05
