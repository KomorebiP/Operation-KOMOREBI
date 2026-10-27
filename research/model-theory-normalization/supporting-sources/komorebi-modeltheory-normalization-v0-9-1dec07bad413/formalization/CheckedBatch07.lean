module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch07
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c084_R := ZMod 4
def c084_A : Fin 1 → Mat c084_R 5 5 := ![![![0, 1, 0, 2, 0], ![2, 1, 1, 3, 3], ![2, 0, 1, 2, 1], ![0, 2, 1, 2, 2], ![0, 0, 0, 0, 3]]]
def c084_O : Mat c084_R 2 5 := ![![0, 2, 0, 0, 2], ![0, 0, 0, 2, 0]]
def c084_evidence : List (Evidence c084_R 5) := [
  .separation (![0, 1, 0, 0, 0]),
  .separation (![0, 0, 0, 1, 0]),
  .separation (![0, 0, 1, 0, 0]),
  .separation (![0, 3, 3, 0, 1]),
  .combination [0, 0, 1, 0],
  .combination [3, 3, 1, 0]]
def c084_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem c084_checked_data : replaySource c084_A c084_O c084_evidence = some c084_result := by decide +kernel
theorem c084_reference_result :
    finitePrimeDiscover 2 2 5 (fun a => rowRight (c084_A a)) c084_O = some c084_result :=
  replaySource_reference 2 2 5 (by decide +kernel) c084_A c084_O c084_evidence c084_result c084_checked_data
theorem c084_all_words (x y : Fin 5 → c084_R) :
    CodeEqual (linearSystem c084_A c084_O) c084_result x y ↔ ObsEq (linearSystem c084_A c084_O) x y :=
  replaySource_all_words c084_A c084_O c084_evidence c084_result c084_checked_data x y
theorem c084_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c084_R) c084_R) :
    taggedRealize (linearSystem c084_A c084_O) (guardedCodeFormula c084_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c084_A c084_O) :=
  replaySource_standard_formula c084_A c084_O c084_evidence c084_result c084_checked_data e
abbrev c085_R := ZMod 9
def c085_A : Fin 2 → Mat c085_R 5 5 := ![![![1, 5, 0, 8, 8], ![8, 0, 6, 3, 1], ![6, 6, 4, 4, 3], ![4, 5, 3, 8, 7], ![2, 3, 8, 6, 6]], ![![5, 6, 5, 0, 6], ![4, 3, 2, 2, 3], ![2, 7, 2, 5, 5], ![1, 4, 4, 7, 2], ![8, 7, 7, 8, 2]]]
def c085_O : Mat c085_R 1 5 := ![![1, 0, 2, 2, 5]]
def c085_evidence : List (Evidence c085_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![0, 1, 0, 0, 0]),
  .separation (![3, 1, 3, 0, 0]),
  .separation (![0, 1, 3, 6, 0]),
  .separation (![6, 1, 0, 0, 6]),
  .separation (![0, 3, 0, 0, 0]),
  .combination [6, 1, 1, 2, 0, 1],
  .combination [3, 2, 8, 3, 0, 2],
  .combination [1, 8, 3, 8, 0, 3],
  .combination [3, 0, 4, 0, 0, 1],
  .combination [2, 1, 5, 4, 0, 3],
  .combination [4, 0, 4, 7, 0, 7],
  .combination [1, 8, 2, 8, 0, 4]]
def c085_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c085_checked_data : replaySource c085_A c085_O c085_evidence = some c085_result := by decide +kernel
theorem c085_reference_result :
    finitePrimeDiscover 3 2 5 (fun a => rowRight (c085_A a)) c085_O = some c085_result :=
  replaySource_reference 3 2 5 (by decide +kernel) c085_A c085_O c085_evidence c085_result c085_checked_data
theorem c085_all_words (x y : Fin 5 → c085_R) :
    CodeEqual (linearSystem c085_A c085_O) c085_result x y ↔ ObsEq (linearSystem c085_A c085_O) x y :=
  replaySource_all_words c085_A c085_O c085_evidence c085_result c085_checked_data x y
theorem c085_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c085_R) c085_R) :
    taggedRealize (linearSystem c085_A c085_O) (guardedCodeFormula c085_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c085_A c085_O) :=
  replaySource_standard_formula c085_A c085_O c085_evidence c085_result c085_checked_data e
abbrev c086_R := ZMod 25
def c086_A : Fin 3 → Mat c086_R 5 5 := ![![![5, 8, 19, 5, 3], ![22, 0, 0, 17, 0], ![15, 1, 16, 11, 14], ![13, 7, 4, 19, 1], ![0, 3, 8, 13, 2]], ![![12, 3, 11, 4, 10], ![8, 19, 3, 22, 14], ![4, 8, 3, 8, 21], ![2, 14, 19, 9, 1], ![24, 18, 7, 19, 0]], ![![23, 21, 23, 0, 5], ![21, 23, 17, 13, 18], ![13, 23, 9, 9, 11], ![10, 1, 15, 8, 18], ![9, 17, 15, 24, 15]]]
def c086_O : Mat c086_R 2 5 := ![![0, 0, 0, 0, 0], ![0, 0, 0, 0, 0]]
def c086_evidence : List (Evidence c086_R 5) := [
  .combination [],
  .combination []]
def c086_result : List (Test 3 2) := []
theorem c086_checked_data : replaySource c086_A c086_O c086_evidence = some c086_result := by decide +kernel
theorem c086_reference_result :
    finitePrimeDiscover 5 2 5 (fun a => rowRight (c086_A a)) c086_O = some c086_result :=
  replaySource_reference 5 2 5 (by decide +kernel) c086_A c086_O c086_evidence c086_result c086_checked_data
theorem c086_all_words (x y : Fin 5 → c086_R) :
    CodeEqual (linearSystem c086_A c086_O) c086_result x y ↔ ObsEq (linearSystem c086_A c086_O) x y :=
  replaySource_all_words c086_A c086_O c086_evidence c086_result c086_checked_data x y
theorem c086_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c086_R) c086_R) :
    taggedRealize (linearSystem c086_A c086_O) (guardedCodeFormula c086_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c086_A c086_O) :=
  replaySource_standard_formula c086_A c086_O c086_evidence c086_result c086_checked_data e
abbrev c087_R := ZMod 8
def c087_A : Fin 1 → Mat c087_R 5 5 := ![![![6, 0, 4, 6, 1], ![7, 3, 7, 1, 7], ![5, 4, 1, 0, 4], ![1, 0, 1, 7, 7], ![1, 1, 2, 5, 0]]]
def c087_O : Mat c087_R 1 5 := ![![4, 1, 6, 7, 2]]
def c087_evidence : List (Evidence c087_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 4, 0, 0, 0]),
  .separation (![0, 0, 1, 6, 0]),
  .separation (![1, 2, 1, 4, 0]),
  .separation (![2, 0, 7, 4, 1]),
  .combination [5, 3, 1, 0, 1]]
def c087_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c087_checked_data : replaySource c087_A c087_O c087_evidence = some c087_result := by decide +kernel
theorem c087_reference_result :
    finitePrimeDiscover 2 3 5 (fun a => rowRight (c087_A a)) c087_O = some c087_result :=
  replaySource_reference 2 3 5 (by decide +kernel) c087_A c087_O c087_evidence c087_result c087_checked_data
theorem c087_all_words (x y : Fin 5 → c087_R) :
    CodeEqual (linearSystem c087_A c087_O) c087_result x y ↔ ObsEq (linearSystem c087_A c087_O) x y :=
  replaySource_all_words c087_A c087_O c087_evidence c087_result c087_checked_data x y
theorem c087_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c087_R) c087_R) :
    taggedRealize (linearSystem c087_A c087_O) (guardedCodeFormula c087_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c087_A c087_O) :=
  replaySource_standard_formula c087_A c087_O c087_evidence c087_result c087_checked_data e
abbrev c088_R := ZMod 27
def c088_A : Fin 2 → Mat c088_R 5 5 := ![![![1, 18, 5, 18, 4], ![16, 24, 12, 10, 0], ![19, 8, 7, 20, 23], ![4, 9, 5, 1, 12], ![22, 23, 1, 16, 6]], ![![21, 13, 22, 10, 7], ![20, 22, 8, 19, 4], ![14, 9, 20, 8, 23], ![2, 18, 7, 1, 5], ![19, 12, 4, 11, 12]]]
def c088_O : Mat c088_R 2 5 := ![![6, 13, 22, 8, 3], ![12, 5, 9, 16, 22]]
def c088_evidence : List (Evidence c088_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 12, 0, 0, 0]),
  .separation (![1, 3, 9, 0, 0]),
  .separation (![26, 10, 21, 1, 0]),
  .separation (![11, 21, 11, 8, 1]),
  .combination [22, 25, 16, 10, 19],
  .combination [19, 11, 9, 0, 9],
  .combination [23, 0, 16, 6, 19],
  .combination [12, 7, 3, 22, 7],
  .combination [23, 4, 4, 10, 10],
  .combination [10, 18, 18, 19, 8],
  .combination [19, 13, 22, 8, 25]]
def c088_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c088_checked_data : replaySource c088_A c088_O c088_evidence = some c088_result := by decide +kernel
theorem c088_reference_result :
    finitePrimeDiscover 3 3 5 (fun a => rowRight (c088_A a)) c088_O = some c088_result :=
  replaySource_reference 3 3 5 (by decide +kernel) c088_A c088_O c088_evidence c088_result c088_checked_data
theorem c088_all_words (x y : Fin 5 → c088_R) :
    CodeEqual (linearSystem c088_A c088_O) c088_result x y ↔ ObsEq (linearSystem c088_A c088_O) x y :=
  replaySource_all_words c088_A c088_O c088_evidence c088_result c088_checked_data x y
theorem c088_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c088_R) c088_R) :
    taggedRealize (linearSystem c088_A c088_O) (guardedCodeFormula c088_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c088_A c088_O) :=
  replaySource_standard_formula c088_A c088_O c088_evidence c088_result c088_checked_data e
abbrev c089_R := ZMod 125
def c089_A : Fin 3 → Mat c089_R 5 5 := ![![![101, 120, 94, 14, 114], ![41, 12, 12, 48, 97], ![78, 55, 52, 92, 34], ![46, 22, 31, 12, 90], ![44, 66, 51, 53, 121]], ![![75, 20, 44, 43, 11], ![117, 80, 29, 45, 35], ![47, 47, 123, 120, 69], ![58, 34, 51, 24, 39], ![48, 87, 116, 59, 21]], ![![19, 66, 59, 54, 73], ![102, 57, 76, 101, 66], ![106, 91, 0, 94, 117], ![89, 66, 65, 97, 51], ![74, 50, 101, 48, 72]]]
def c089_O : Mat c089_R 1 5 := ![![37, 85, 115, 110, 96]]
def c089_evidence : List (Evidence c089_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![45, 1, 0, 0, 0]),
  .separation (![25, 26, 1, 0, 0]),
  .separation (![75, 121, 92, 1, 0]),
  .separation (![122, 109, 52, 82, 1]),
  .combination [81, 11, 5, 98, 116],
  .combination [95, 85, 109, 76, 66],
  .combination [32, 14, 33, 66, 25],
  .combination [88, 83, 5, 35, 57],
  .combination [41, 45, 59, 74, 10],
  .combination [14, 67, 95, 0, 14],
  .combination [86, 41, 115, 24, 28],
  .combination [10, 29, 38, 109, 61],
  .combination [2, 59, 120, 103, 15],
  .combination [123, 1, 68, 20, 33],
  .combination [47, 51, 99, 40, 117]]
def c089_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c089_checked_data : replaySource c089_A c089_O c089_evidence = some c089_result := by decide +kernel
theorem c089_reference_result :
    finitePrimeDiscover 5 3 5 (fun a => rowRight (c089_A a)) c089_O = some c089_result :=
  replaySource_reference 5 3 5 (by decide +kernel) c089_A c089_O c089_evidence c089_result c089_checked_data
theorem c089_all_words (x y : Fin 5 → c089_R) :
    CodeEqual (linearSystem c089_A c089_O) c089_result x y ↔ ObsEq (linearSystem c089_A c089_O) x y :=
  replaySource_all_words c089_A c089_O c089_evidence c089_result c089_checked_data x y
theorem c089_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c089_R) c089_R) :
    taggedRealize (linearSystem c089_A c089_O) (guardedCodeFormula c089_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c089_A c089_O) :=
  replaySource_standard_formula c089_A c089_O c089_evidence c089_result c089_checked_data e
abbrev c090_R := ZMod 16
def c090_A : Fin 1 → Mat c090_R 5 5 := ![![![12, 15, 0, 3, 11], ![12, 0, 6, 13, 1], ![9, 8, 15, 8, 10], ![2, 14, 13, 15, 3], ![14, 3, 0, 5, 13]]]
def c090_O : Mat c090_R 2 5 := ![![7, 3, 15, 10, 11], ![11, 8, 5, 10, 3]]
def c090_evidence : List (Evidence c090_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![11, 1, 0, 0, 0]),
  .separation (![1, 14, 1, 0, 0]),
  .separation (![3, 12, 0, 14, 1]),
  .separation (![13, 14, 1, 14, 0]),
  .combination [5, 3, 7, 8, 14],
  .combination [12, 0, 12, 15, 15]]
def c090_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c090_checked_data : replaySource c090_A c090_O c090_evidence = some c090_result := by decide +kernel
theorem c090_reference_result :
    finitePrimeDiscover 2 4 5 (fun a => rowRight (c090_A a)) c090_O = some c090_result :=
  replaySource_reference 2 4 5 (by decide +kernel) c090_A c090_O c090_evidence c090_result c090_checked_data
theorem c090_all_words (x y : Fin 5 → c090_R) :
    CodeEqual (linearSystem c090_A c090_O) c090_result x y ↔ ObsEq (linearSystem c090_A c090_O) x y :=
  replaySource_all_words c090_A c090_O c090_evidence c090_result c090_checked_data x y
theorem c090_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c090_R) c090_R) :
    taggedRealize (linearSystem c090_A c090_O) (guardedCodeFormula c090_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c090_A c090_O) :=
  replaySource_standard_formula c090_A c090_O c090_evidence c090_result c090_checked_data e
abbrev c091_R := ZMod 81
def c091_A : Fin 2 → Mat c091_R 5 5 := ![![![9, 43, 18, 8, 34], ![48, 74, 48, 28, 54], ![26, 79, 40, 1, 35], ![17, 17, 42, 77, 64], ![26, 14, 35, 17, 17]], ![![22, 79, 68, 63, 14], ![69, 76, 64, 36, 56], ![69, 12, 14, 69, 20], ![0, 56, 30, 63, 0], ![21, 4, 75, 34, 71]]]
def c091_O : Mat c091_R 1 5 := ![![0, 54, 54, 27, 27]]
def c091_evidence : List (Evidence c091_R 5) := [
  .separation (![0, 1, 0, 0, 0]),
  .separation (![1, 0, 0, 0, 0]),
  .separation (![0, 80, 1, 0, 0]),
  .separation (![0, 79, 0, 1, 0]),
  .separation (![80, 0, 0, 80, 1]),
  .combination [65, 38, 76, 1, 2],
  .combination [4, 79, 77, 0, 2],
  .combination [63, 39, 78, 1, 1],
  .combination [3, 79, 76, 1, 2],
  .combination [64, 38, 37, 41, 2],
  .combination [40, 0, 0, 1, 0]]
def c091_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem c091_checked_data : replaySource c091_A c091_O c091_evidence = some c091_result := by decide +kernel
theorem c091_reference_result :
    finitePrimeDiscover 3 4 5 (fun a => rowRight (c091_A a)) c091_O = some c091_result :=
  replaySource_reference 3 4 5 (by decide +kernel) c091_A c091_O c091_evidence c091_result c091_checked_data
theorem c091_all_words (x y : Fin 5 → c091_R) :
    CodeEqual (linearSystem c091_A c091_O) c091_result x y ↔ ObsEq (linearSystem c091_A c091_O) x y :=
  replaySource_all_words c091_A c091_O c091_evidence c091_result c091_checked_data x y
theorem c091_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c091_R) c091_R) :
    taggedRealize (linearSystem c091_A c091_O) (guardedCodeFormula c091_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c091_A c091_O) :=
  replaySource_standard_formula c091_A c091_O c091_evidence c091_result c091_checked_data e
abbrev c092_R := ZMod 625
def c092_A : Fin 3 → Mat c092_R 5 5 := ![![![229, 287, 50, 317, 544], ![192, 326, 502, 259, 466], ![239, 6, 59, 596, 134], ![283, 460, 37, 549, 29], ![545, 154, 354, 501, 561]], ![![228, 153, 350, 589, 583], ![308, 252, 467, 249, 140], ![445, 375, 621, 543, 346], ![512, 323, 353, 27, 602], ![400, 76, 346, 528, 58]], ![![82, 101, 106, 233, 309], ![387, 35, 357, 162, 203], ![619, 6, 428, 317, 154], ![236, 163, 175, 392, 141], ![253, 283, 491, 528, 194]]]
def c092_O : Mat c092_R 2 5 := ![![467, 203, 247, 46, 165], ![354, 10, 202, 138, 248]]
def c092_evidence : List (Evidence c092_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![116, 1, 0, 0, 0]),
  .separation (![117, 213, 1, 0, 0]),
  .separation (![389, 375, 153, 1, 0]),
  .separation (![542, 478, 563, 231, 1]),
  .separation (![250, 375, 375, 125, 125]),
  .combination [72, 341, 430, 474, 0, 614],
  .combination [399, 60, 379, 193, 0, 13],
  .combination [232, 324, 548, 326, 0, 367],
  .combination [591, 357, 495, 315, 0, 512],
  .combination [623, 42, 25, 103, 0, 271],
  .combination [571, 365, 22, 419, 0, 547],
  .combination [275, 146, 157, 345, 0, 96],
  .combination [398, 448, 613, 237, 0, 133],
  .combination [321, 439, 417, 267, 0, 446],
  .combination [288, 482, 18, 570, 0, 260],
  .combination [30, 230, 372, 523, 0, 146],
  .combination [279, 222, 351, 504, 0, 132],
  .combination [514, 109, 525, 363, 0, 5],
  .combination [100, 202, 550, 267, 0, 183]]
def c092_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c092_checked_data : replaySource c092_A c092_O c092_evidence = some c092_result := by decide +kernel
theorem c092_reference_result :
    finitePrimeDiscover 5 4 5 (fun a => rowRight (c092_A a)) c092_O = some c092_result :=
  replaySource_reference 5 4 5 (by decide +kernel) c092_A c092_O c092_evidence c092_result c092_checked_data
theorem c092_all_words (x y : Fin 5 → c092_R) :
    CodeEqual (linearSystem c092_A c092_O) c092_result x y ↔ ObsEq (linearSystem c092_A c092_O) x y :=
  replaySource_all_words c092_A c092_O c092_evidence c092_result c092_checked_data x y
theorem c092_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c092_R) c092_R) :
    taggedRealize (linearSystem c092_A c092_O) (guardedCodeFormula c092_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c092_A c092_O) :=
  replaySource_standard_formula c092_A c092_O c092_evidence c092_result c092_checked_data e
abbrev c093_R := ZMod 32
def c093_A : Fin 1 → Mat c093_R 5 5 := ![![![10, 4, 17, 24, 20], ![21, 6, 5, 17, 26], ![18, 25, 23, 19, 26], ![16, 4, 3, 11, 6], ![28, 30, 21, 1, 17]]]
def c093_O : Mat c093_R 1 5 := ![![22, 7, 30, 3, 2]]
def c093_evidence : List (Evidence c093_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1, 6, 0, 0, 0]),
  .separation (![6, 18, 1, 0, 0]),
  .separation (![10, 18, 30, 0, 1]),
  .separation (![0, 15, 22, 1, 0]),
  .combination [9, 4, 16, 25, 11]]
def c093_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c093_checked_data : replaySource c093_A c093_O c093_evidence = some c093_result := by decide +kernel
theorem c093_reference_result :
    finitePrimeDiscover 2 5 5 (fun a => rowRight (c093_A a)) c093_O = some c093_result :=
  replaySource_reference 2 5 5 (by decide +kernel) c093_A c093_O c093_evidence c093_result c093_checked_data
theorem c093_all_words (x y : Fin 5 → c093_R) :
    CodeEqual (linearSystem c093_A c093_O) c093_result x y ↔ ObsEq (linearSystem c093_A c093_O) x y :=
  replaySource_all_words c093_A c093_O c093_evidence c093_result c093_checked_data x y
theorem c093_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c093_R) c093_R) :
    taggedRealize (linearSystem c093_A c093_O) (guardedCodeFormula c093_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c093_A c093_O) :=
  replaySource_standard_formula c093_A c093_O c093_evidence c093_result c093_checked_data e
abbrev c094_R := ZMod 243
def c094_A : Fin 2 → Mat c094_R 5 5 := ![![![215, 94, 41, 186, 191], ![193, 37, 116, 120, 48], ![59, 178, 156, 167, 0], ![226, 238, 110, 50, 146], ![215, 156, 204, 183, 44]], ![![86, 90, 135, 221, 87], ![79, 36, 108, 37, 108], ![235, 76, 133, 65, 53], ![71, 37, 8, 16, 13], ![108, 177, 123, 40, 155]]]
def c094_O : Mat c094_R 2 5 := ![![164, 193, 21, 41, 103], ![56, 46, 141, 64, 91]]
def c094_evidence : List (Evidence c094_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![187, 1, 0, 0, 0]),
  .separation (![144, 0, 1, 111, 0]),
  .separation (![109, 1, 163, 27, 0]),
  .separation (![81, 0, 162, 0, 81]),
  .separation (![0, 162, 81, 0, 81]),
  .combination [36, 22, 187, 0, 232, 15],
  .combination [142, 217, 59, 0, 218, 141],
  .combination [48, 220, 89, 0, 234, 171],
  .combination [176, 102, 81, 0, 134, 221],
  .combination [17, 147, 170, 0, 181, 135],
  .combination [108, 43, 96, 0, 150, 216],
  .combination [36, 116, 27, 0, 1, 134],
  .combination [105, 85, 83, 0, 151, 81]]
def c094_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem c094_checked_data : replaySource c094_A c094_O c094_evidence = some c094_result := by decide +kernel
theorem c094_reference_result :
    finitePrimeDiscover 3 5 5 (fun a => rowRight (c094_A a)) c094_O = some c094_result :=
  replaySource_reference 3 5 5 (by decide +kernel) c094_A c094_O c094_evidence c094_result c094_checked_data
theorem c094_all_words (x y : Fin 5 → c094_R) :
    CodeEqual (linearSystem c094_A c094_O) c094_result x y ↔ ObsEq (linearSystem c094_A c094_O) x y :=
  replaySource_all_words c094_A c094_O c094_evidence c094_result c094_checked_data x y
theorem c094_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c094_R) c094_R) :
    taggedRealize (linearSystem c094_A c094_O) (guardedCodeFormula c094_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c094_A c094_O) :=
  replaySource_standard_formula c094_A c094_O c094_evidence c094_result c094_checked_data e
abbrev c095_R := ZMod 3125
def c095_A : Fin 3 → Mat c095_R 5 5 := ![![![2277, 1422, 1294, 646, 2433], ![2328, 158, 2137, 1258, 220], ![2566, 35, 2691, 704, 653], ![1372, 1235, 1365, 1613, 1122], ![3069, 2726, 2491, 985, 238]], ![![1049, 2380, 2211, 396, 1852], ![2244, 1796, 2669, 191, 2187], ![2182, 868, 2844, 2850, 1365], ![2060, 246, 2826, 889, 2211], ![2322, 2013, 405, 2041, 3073]], ![![1533, 460, 2443, 2423, 485], ![3028, 2990, 2875, 2341, 629], ![835, 1611, 561, 347, 1391], ![1471, 3055, 1398, 554, 663], ![600, 1904, 517, 206, 847]]]
def c095_O : Mat c095_R 1 5 := ![![1842, 2605, 1237, 1803, 619]]
def c095_evidence : List (Evidence c095_R 5) := [
  .separation (![1, 0, 0, 0, 0]),
  .separation (![1310, 1, 0, 0, 0]),
  .separation (![69, 2873, 1, 0, 0]),
  .separation (![1270, 649, 2301, 1, 0]),
  .separation (![1734, 588, 665, 2486, 1]),
  .combination [795, 2333, 1905, 2235, 849],
  .combination [859, 2957, 2535, 1391, 1472],
  .combination [1800, 2126, 302, 984, 1322],
  .combination [1574, 193, 2416, 225, 1488],
  .combination [2939, 189, 1406, 2662, 1289],
  .combination [1273, 2702, 2774, 382, 2690],
  .combination [1188, 435, 1139, 1099, 867],
  .combination [2796, 798, 1544, 2931, 441],
  .combination [2817, 939, 2556, 1000, 43],
  .combination [2693, 2254, 2574, 1639, 678],
  .combination [545, 308, 1469, 2775, 2316]]
def c095_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem c095_checked_data : replaySource c095_A c095_O c095_evidence = some c095_result := by decide +kernel
theorem c095_reference_result :
    finitePrimeDiscover 5 5 5 (fun a => rowRight (c095_A a)) c095_O = some c095_result :=
  replaySource_reference 5 5 5 (by decide +kernel) c095_A c095_O c095_evidence c095_result c095_checked_data
theorem c095_all_words (x y : Fin 5 → c095_R) :
    CodeEqual (linearSystem c095_A c095_O) c095_result x y ↔ ObsEq (linearSystem c095_A c095_O) x y :=
  replaySource_all_words c095_A c095_O c095_evidence c095_result c095_checked_data x y
theorem c095_standard_definition (e : Fin 2 → TaggedCarrier (Fin 5 → c095_R) c095_R) :
    taggedRealize (linearSystem c095_A c095_O) (guardedCodeFormula c095_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c095_A c095_O) :=
  replaySource_standard_formula c095_A c095_O c095_evidence c095_result c095_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch07
