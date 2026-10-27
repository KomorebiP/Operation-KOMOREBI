module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch16
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c192_R := ZMod 8
def c192_A : Fin 1 → Mat c192_R 6 6 := ![![![6, 3, 5, 4, 6, 2], ![4, 1, 2, 6, 0, 1], ![7, 2, 5, 7, 4, 0], ![6, 3, 4, 1, 3, 0], ![7, 1, 4, 0, 0, 5], ![6, 4, 4, 1, 2, 7]]]
def c192_O : Mat c192_R 2 6 := ![![0, 3, 3, 3, 6, 7], ![0, 6, 0, 6, 2, 2]]
def c192_evidence : List (Evidence c192_R 6) := [
  .separation (![0, 1, 0, 0, 0, 0]),
  .separation (![0, 7, 1, 0, 0, 0]),
  .separation (![0, 4, 4, 0, 0, 0]),
  .separation (![0, 1, 5, 0, 1, 0]),
  .separation (![4, 4, 4, 0, 0, 0]),
  .combination [6, 0, 0, 1, 2],
  .separation (![0, 0, 4, 4, 0, 0]),
  .separation (![4, 2, 2, 4, 2, 4]),
  .combination [6, 1, 5, 0, 7, 7, 6]]
def c192_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c192_checked_data : replaySource c192_A c192_O c192_evidence = some c192_result := by decide +kernel
theorem c192_reference_result :
    finitePrimeDiscover 2 3 6 (fun a => rowRight (c192_A a)) c192_O = some c192_result :=
  replaySource_reference 2 3 6 (by decide +kernel) c192_A c192_O c192_evidence c192_result c192_checked_data
theorem c192_all_words (x y : Fin 6 → c192_R) :
    CodeEqual (linearSystem c192_A c192_O) c192_result x y ↔ ObsEq (linearSystem c192_A c192_O) x y :=
  replaySource_all_words c192_A c192_O c192_evidence c192_result c192_checked_data x y
theorem c192_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c192_R) c192_R) :
    taggedRealize (linearSystem c192_A c192_O) (guardedCodeFormula c192_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c192_A c192_O) :=
  replaySource_standard_formula c192_A c192_O c192_evidence c192_result c192_checked_data e
abbrev c193_R := ZMod 27
def c193_A : Fin 2 → Mat c193_R 6 6 := ![![![1, 2, 20, 21, 24, 15], ![11, 4, 18, 5, 19, 5], ![15, 26, 25, 5, 7, 14], ![19, 12, 8, 3, 24, 21], ![20, 21, 16, 11, 13, 20], ![11, 16, 19, 9, 23, 5]], ![![2, 24, 11, 22, 16, 22], ![13, 15, 14, 21, 1, 1], ![21, 8, 17, 12, 23, 15], ![16, 22, 25, 25, 4, 6], ![4, 12, 11, 24, 5, 21], ![12, 13, 21, 5, 6, 16]]]
def c193_O : Mat c193_R 1 6 := ![![18, 4, 10, 3, 13, 23]]
def c193_evidence : List (Evidence c193_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 9, 0, 0, 0, 0]),
  .separation (![8, 2, 1, 0, 0, 0]),
  .separation (![8, 2, 1, 18, 0, 0]),
  .separation (![14, 26, 1, 21, 21, 0]),
  .combination [19, 9, 22, 1, 24],
  .separation (![20, 0, 3, 24, 25, 1]),
  .separation (![6, 0, 9, 18, 21, 3]),
  .combination [14, 24, 18, 19, 3, 0, 0],
  .combination [13, 13, 15, 23, 2, 0, 23],
  .combination [10, 12, 16, 14, 3, 0, 26],
  .combination [15, 15, 2, 7, 20, 0, 26],
  .combination [8, 15, 10, 20, 23, 0, 5],
  .combination [3, 20, 25, 15, 4, 0, 0],
  .combination [23, 15, 13, 17, 0, 0, 23]]
def c193_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([1,1], 0), ([0,0,0], 0)]
theorem c193_checked_data : replaySource c193_A c193_O c193_evidence = some c193_result := by decide +kernel
theorem c193_reference_result :
    finitePrimeDiscover 3 3 6 (fun a => rowRight (c193_A a)) c193_O = some c193_result :=
  replaySource_reference 3 3 6 (by decide +kernel) c193_A c193_O c193_evidence c193_result c193_checked_data
theorem c193_all_words (x y : Fin 6 → c193_R) :
    CodeEqual (linearSystem c193_A c193_O) c193_result x y ↔ ObsEq (linearSystem c193_A c193_O) x y :=
  replaySource_all_words c193_A c193_O c193_evidence c193_result c193_checked_data x y
theorem c193_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c193_R) c193_R) :
    taggedRealize (linearSystem c193_A c193_O) (guardedCodeFormula c193_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c193_A c193_O) :=
  replaySource_standard_formula c193_A c193_O c193_evidence c193_result c193_checked_data e
abbrev c194_R := ZMod 125
def c194_A : Fin 3 → Mat c194_R 6 6 := ![![![24, 66, 28, 73, 108, 90], ![88, 90, 116, 100, 34, 69], ![4, 63, 8, 79, 3, 42], ![19, 81, 62, 56, 16, 50], ![105, 67, 122, 7, 104, 0], ![112, 18, 67, 52, 10, 41]], ![![64, 109, 99, 36, 122, 10], ![5, 97, 70, 31, 41, 118], ![116, 58, 122, 55, 93, 104], ![52, 4, 30, 30, 8, 93], ![48, 94, 6, 6, 10, 91], ![80, 43, 58, 0, 16, 118]], ![![54, 18, 65, 34, 111, 78], ![47, 7, 119, 5, 48, 88], ![24, 110, 95, 37, 29, 82], ![98, 124, 89, 103, 55, 2], ![49, 113, 120, 15, 88, 55], ![102, 15, 3, 109, 77, 50]]]
def c194_O : Mat c194_R 2 6 := ![![86, 71, 44, 98, 62, 37], ![97, 24, 77, 0, 105, 85]]
def c194_evidence : List (Evidence c194_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![114, 1, 0, 0, 0, 0]),
  .separation (![68, 123, 1, 0, 0, 0]),
  .separation (![48, 58, 1, 20, 0, 0]),
  .separation (![120, 0, 65, 46, 1, 0]),
  .separation (![115, 16, 28, 119, 39, 1]),
  .combination [119, 68, 78, 110, 69, 32],
  .combination [96, 115, 30, 50, 71, 95],
  .combination [76, 82, 116, 27, 32, 34],
  .combination [18, 61, 1, 20, 55, 54],
  .combination [21, 93, 10, 28, 103, 80],
  .combination [96, 18, 123, 53, 24, 58],
  .combination [88, 63, 66, 88, 30, 61],
  .combination [122, 69, 14, 85, 64, 16],
  .combination [43, 114, 70, 20, 103, 100],
  .combination [45, 21, 25, 49, 59, 51],
  .combination [16, 85, 96, 64, 108, 78],
  .combination [37, 101, 58, 113, 84, 51],
  .combination [121, 52, 121, 72, 2, 100],
  .combination [4, 37, 95, 85, 12, 79]]
def c194_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c194_checked_data : replaySource c194_A c194_O c194_evidence = some c194_result := by decide +kernel
theorem c194_reference_result :
    finitePrimeDiscover 5 3 6 (fun a => rowRight (c194_A a)) c194_O = some c194_result :=
  replaySource_reference 5 3 6 (by decide +kernel) c194_A c194_O c194_evidence c194_result c194_checked_data
theorem c194_all_words (x y : Fin 6 → c194_R) :
    CodeEqual (linearSystem c194_A c194_O) c194_result x y ↔ ObsEq (linearSystem c194_A c194_O) x y :=
  replaySource_all_words c194_A c194_O c194_evidence c194_result c194_checked_data x y
theorem c194_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c194_R) c194_R) :
    taggedRealize (linearSystem c194_A c194_O) (guardedCodeFormula c194_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c194_A c194_O) :=
  replaySource_standard_formula c194_A c194_O c194_evidence c194_result c194_checked_data e
abbrev c195_R := ZMod 16
def c195_A : Fin 1 → Mat c195_R 6 6 := ![![![5, 9, 3, 7, 10, 3], ![1, 14, 1, 8, 1, 10], ![14, 9, 14, 10, 13, 1], ![8, 1, 8, 14, 12, 12], ![14, 14, 2, 12, 7, 13], ![15, 15, 8, 7, 13, 3]]]
def c195_O : Mat c195_R 1 6 := ![![15, 4, 1, 3, 9, 2]]
def c195_evidence : List (Evidence c195_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![4, 1, 0, 0, 0, 0]),
  .separation (![9, 2, 1, 0, 0, 0]),
  .separation (![10, 0, 7, 1, 0, 0]),
  .separation (![7, 13, 6, 12, 1, 0]),
  .separation (![6, 8, 3, 10, 11, 1]),
  .combination [14, 6, 8, 4, 7, 1]]
def c195_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0)]
theorem c195_checked_data : replaySource c195_A c195_O c195_evidence = some c195_result := by decide +kernel
theorem c195_reference_result :
    finitePrimeDiscover 2 4 6 (fun a => rowRight (c195_A a)) c195_O = some c195_result :=
  replaySource_reference 2 4 6 (by decide +kernel) c195_A c195_O c195_evidence c195_result c195_checked_data
theorem c195_all_words (x y : Fin 6 → c195_R) :
    CodeEqual (linearSystem c195_A c195_O) c195_result x y ↔ ObsEq (linearSystem c195_A c195_O) x y :=
  replaySource_all_words c195_A c195_O c195_evidence c195_result c195_checked_data x y
theorem c195_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c195_R) c195_R) :
    taggedRealize (linearSystem c195_A c195_O) (guardedCodeFormula c195_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c195_A c195_O) :=
  replaySource_standard_formula c195_A c195_O c195_evidence c195_result c195_checked_data e
abbrev c196_R := ZMod 81
def c196_A : Fin 2 → Mat c196_R 6 6 := ![![![8, 19, 44, 66, 42, 8], ![21, 68, 61, 80, 63, 50], ![42, 67, 13, 43, 30, 70], ![79, 23, 37, 29, 17, 80], ![30, 33, 27, 67, 73, 47], ![68, 3, 45, 46, 22, 50]], ![![53, 76, 44, 41, 10, 52], ![34, 31, 8, 12, 32, 71], ![76, 54, 7, 69, 25, 39], ![28, 40, 40, 26, 72, 1], ![26, 76, 44, 65, 35, 28], ![47, 68, 67, 26, 57, 33]]]
def c196_O : Mat c196_R 2 6 := ![![27, 27, 0, 27, 0, 27], ![0, 0, 0, 27, 27, 0]]
def c196_evidence : List (Evidence c196_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![80, 0, 0, 1, 0, 0]),
  .separation (![0, 0, 1, 0, 0, 0]),
  .separation (![80, 1, 0, 0, 0, 0]),
  .separation (![1, 0, 0, 80, 1, 0]),
  .combination [1, 80, 80, 41, 1],
  .combination [3, 78, 79, 40, 2],
  .separation (![0, 79, 0, 1, 80, 1]),
  .combination [79, 0, 2, 42, 80, 1],
  .combination [78, 1, 2, 0, 0, 0],
  .combination [79, 0, 1, 1, 0, 1],
  .combination [77, 2, 3, 42, 79, 1],
  .combination [79, 0, 1, 41, 0, 0],
  .combination [43, 79, 39, 40, 1, 41]]
def c196_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1,0], 0)]
theorem c196_checked_data : replaySource c196_A c196_O c196_evidence = some c196_result := by decide +kernel
theorem c196_reference_result :
    finitePrimeDiscover 3 4 6 (fun a => rowRight (c196_A a)) c196_O = some c196_result :=
  replaySource_reference 3 4 6 (by decide +kernel) c196_A c196_O c196_evidence c196_result c196_checked_data
theorem c196_all_words (x y : Fin 6 → c196_R) :
    CodeEqual (linearSystem c196_A c196_O) c196_result x y ↔ ObsEq (linearSystem c196_A c196_O) x y :=
  replaySource_all_words c196_A c196_O c196_evidence c196_result c196_checked_data x y
theorem c196_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c196_R) c196_R) :
    taggedRealize (linearSystem c196_A c196_O) (guardedCodeFormula c196_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c196_A c196_O) :=
  replaySource_standard_formula c196_A c196_O c196_evidence c196_result c196_checked_data e
abbrev c197_R := ZMod 625
def c197_A : Fin 3 → Mat c197_R 6 6 := ![![![429, 206, 273, 402, 204, 349], ![282, 379, 580, 539, 276, 265], ![382, 104, 517, 231, 468, 18], ![484, 523, 367, 118, 187, 596], ![437, 365, 540, 560, 341, 274], ![433, 86, 196, 433, 551, 393]], ![![366, 34, 563, 282, 62, 163], ![583, 449, 60, 491, 356, 580], ![464, 239, 440, 181, 116, 138], ![226, 306, 457, 151, 390, 418], ![104, 295, 24, 536, 485, 70], ![424, 248, 363, 585, 102, 357]], ![![263, 161, 442, 343, 105, 225], ![333, 425, 11, 474, 170, 561], ![411, 355, 334, 334, 125, 145], ![445, 145, 515, 334, 471, 455], ![358, 432, 289, 359, 525, 174], ![596, 128, 71, 584, 271, 63]]]
def c197_O : Mat c197_R 1 6 := ![![134, 345, 136, 619, 577, 579]]
def c197_evidence : List (Evidence c197_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![170, 1, 0, 0, 0, 0]),
  .separation (![141, 251, 1, 0, 0, 0]),
  .separation (![128, 272, 149, 1, 0, 0]),
  .separation (![235, 163, 16, 288, 1, 0]),
  .separation (![303, 484, 608, 462, 624, 1]),
  .combination [263, 273, 614, 585, 127, 340],
  .combination [507, 457, 232, 34, 397, 8],
  .combination [115, 460, 373, 612, 562, 78],
  .combination [411, 479, 290, 325, 358, 334],
  .combination [436, 293, 623, 268, 99, 22],
  .combination [498, 299, 187, 16, 34, 459],
  .combination [595, 426, 257, 422, 348, 531],
  .combination [50, 555, 33, 294, 314, 475],
  .combination [155, 11, 587, 608, 485, 235],
  .combination [271, 499, 347, 426, 4, 40],
  .combination [231, 180, 255, 136, 487, 113],
  .combination [351, 483, 544, 440, 622, 124],
  .combination [376, 71, 407, 113, 519, 330]]
def c197_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c197_checked_data : replaySource c197_A c197_O c197_evidence = some c197_result := by decide +kernel
theorem c197_reference_result :
    finitePrimeDiscover 5 4 6 (fun a => rowRight (c197_A a)) c197_O = some c197_result :=
  replaySource_reference 5 4 6 (by decide +kernel) c197_A c197_O c197_evidence c197_result c197_checked_data
theorem c197_all_words (x y : Fin 6 → c197_R) :
    CodeEqual (linearSystem c197_A c197_O) c197_result x y ↔ ObsEq (linearSystem c197_A c197_O) x y :=
  replaySource_all_words c197_A c197_O c197_evidence c197_result c197_checked_data x y
theorem c197_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c197_R) c197_R) :
    taggedRealize (linearSystem c197_A c197_O) (guardedCodeFormula c197_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c197_A c197_O) :=
  replaySource_standard_formula c197_A c197_O c197_evidence c197_result c197_checked_data e
abbrev c198_R := ZMod 32
def c198_A : Fin 1 → Mat c198_R 6 6 := ![![![27, 8, 24, 27, 3, 0], ![29, 18, 26, 18, 29, 18], ![3, 21, 12, 22, 10, 6], ![31, 15, 4, 28, 11, 23], ![19, 24, 14, 31, 26, 31], ![25, 11, 17, 25, 15, 7]]]
def c198_O : Mat c198_R 2 6 := ![![11, 13, 19, 21, 3, 26], ![10, 14, 5, 3, 31, 16]]
def c198_evidence : List (Evidence c198_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![25, 1, 0, 0, 0, 0]),
  .separation (![17, 1, 8, 0, 0, 0]),
  .separation (![22, 6, 9, 1, 0, 0]),
  .separation (![5, 7, 11, 18, 1, 0]),
  .separation (![29, 29, 11, 0, 31, 1]),
  .separation (![8, 8, 24, 0, 24, 8]),
  .combination [24, 16, 31, 21, 2, 0, 20],
  .combination [25, 17, 9, 11, 5, 0, 2]]
def c198_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1), ([0,0,0], 0)]
theorem c198_checked_data : replaySource c198_A c198_O c198_evidence = some c198_result := by decide +kernel
theorem c198_reference_result :
    finitePrimeDiscover 2 5 6 (fun a => rowRight (c198_A a)) c198_O = some c198_result :=
  replaySource_reference 2 5 6 (by decide +kernel) c198_A c198_O c198_evidence c198_result c198_checked_data
theorem c198_all_words (x y : Fin 6 → c198_R) :
    CodeEqual (linearSystem c198_A c198_O) c198_result x y ↔ ObsEq (linearSystem c198_A c198_O) x y :=
  replaySource_all_words c198_A c198_O c198_evidence c198_result c198_checked_data x y
theorem c198_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c198_R) c198_R) :
    taggedRealize (linearSystem c198_A c198_O) (guardedCodeFormula c198_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c198_A c198_O) :=
  replaySource_standard_formula c198_A c198_O c198_evidence c198_result c198_checked_data e
abbrev c199_R := ZMod 243
def c199_A : Fin 2 → Mat c199_R 6 6 := ![![![242, 109, 5, 6, 147, 34], ![147, 58, 207, 197, 156, 219], ![142, 172, 72, 188, 195, 173], ![99, 209, 29, 163, 85, 3], ![123, 122, 208, 228, 2, 39], ![241, 118, 23, 199, 115, 20]], ![![226, 231, 182, 184, 127, 210], ![135, 157, 143, 221, 174, 164], ![174, 87, 27, 36, 135, 32], ![48, 182, 0, 231, 100, 12], ![114, 22, 46, 185, 157, 91], ![118, 211, 135, 156, 131, 76]]]
def c199_O : Mat c199_R 1 6 := ![![171, 184, 158, 224, 142, 55]]
def c199_evidence : List (Evidence c199_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 180, 0, 0, 0, 0]),
  .separation (![1, 204, 132, 0, 0, 0]),
  .separation (![9, 29, 175, 1, 0, 0]),
  .separation (![165, 101, 7, 1, 183, 0]),
  .separation (![192, 0, 240, 10, 141, 1]),
  .combination [42, 93, 180, 227, 91, 115],
  .combination [21, 233, 18, 233, 146, 175],
  .combination [148, 77, 82, 148, 113, 229],
  .combination [150, 14, 14, 184, 69, 112],
  .combination [199, 164, 204, 64, 237, 125],
  .combination [219, 49, 184, 226, 212, 12],
  .combination [37, 212, 116, 148, 182, 66]]
def c199_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c199_checked_data : replaySource c199_A c199_O c199_evidence = some c199_result := by decide +kernel
theorem c199_reference_result :
    finitePrimeDiscover 3 5 6 (fun a => rowRight (c199_A a)) c199_O = some c199_result :=
  replaySource_reference 3 5 6 (by decide +kernel) c199_A c199_O c199_evidence c199_result c199_checked_data
theorem c199_all_words (x y : Fin 6 → c199_R) :
    CodeEqual (linearSystem c199_A c199_O) c199_result x y ↔ ObsEq (linearSystem c199_A c199_O) x y :=
  replaySource_all_words c199_A c199_O c199_evidence c199_result c199_checked_data x y
theorem c199_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c199_R) c199_R) :
    taggedRealize (linearSystem c199_A c199_O) (guardedCodeFormula c199_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c199_A c199_O) :=
  replaySource_standard_formula c199_A c199_O c199_evidence c199_result c199_checked_data e
abbrev c200_R := ZMod 3125
def c200_A : Fin 3 → Mat c200_R 6 6 := ![![![359, 2215, 2375, 2102, 1953, 1435], ![309, 1145, 1384, 530, 1804, 2344], ![2729, 173, 2574, 1085, 1277, 771], ![66, 1152, 2718, 2419, 244, 1813], ![320, 2980, 2464, 472, 2510, 2751], ![2846, 1564, 1215, 1239, 630, 579]], ![![1627, 1438, 1488, 2392, 2593, 692], ![2659, 410, 1711, 1555, 3021, 2288], ![1281, 656, 1767, 807, 242, 664], ![2354, 166, 2721, 499, 1561, 239], ![2792, 1104, 1433, 1048, 3060, 253], ![2670, 2348, 1762, 2224, 2157, 2234]], ![![1317, 697, 2576, 644, 2240, 1708], ![2485, 2313, 2357, 1837, 1253, 462], ![1454, 1472, 3058, 1872, 1942, 2856], ![2517, 1084, 1644, 222, 183, 3085], ![1615, 562, 3105, 1042, 993, 1400], ![174, 2072, 2132, 2904, 1655, 1600]]]
def c200_O : Mat c200_R 2 6 := ![![2358, 1712, 158, 579, 2077, 2544], ![2315, 331, 2650, 2342, 2649, 1444]]
def c200_evidence : List (Evidence c200_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1086, 1, 0, 0, 0, 0]),
  .separation (![414, 2865, 1, 0, 0, 0]),
  .separation (![889, 2920, 1, 1260, 0, 0]),
  .separation (![303, 2640, 2769, 2323, 1, 0]),
  .separation (![3120, 1839, 630, 1389, 1016, 1]),
  .separation (![0, 2500, 0, 2500, 625, 625]),
  .combination [1017, 768, 2786, 2108, 44, 0, 1649],
  .combination [1066, 2068, 2689, 1667, 1624, 0, 702],
  .combination [2853, 885, 516, 198, 514, 0, 525],
  .combination [1221, 959, 1157, 1350, 1460, 0, 626],
  .combination [673, 1041, 2337, 205, 2455, 0, 1697],
  .combination [2382, 2477, 2474, 11, 2289, 0, 2969],
  .combination [569, 1338, 2956, 2851, 2494, 0, 3097],
  .combination [2879, 602, 1192, 2713, 130, 0, 2984],
  .combination [1341, 623, 753, 1719, 521, 0, 1692],
  .combination [25, 989, 2287, 1948, 2631, 0, 852],
  .combination [1796, 2853, 1356, 163, 216, 0, 680],
  .combination [2690, 2256, 1197, 658, 2186, 0, 1975],
  .combination [2473, 1235, 2662, 2679, 53, 0, 39],
  .combination [767, 1751, 258, 1271, 1737, 0, 796],
  .combination [1287, 2318, 278, 2762, 542, 0, 2299],
  .combination [2371, 1041, 1527, 1753, 2248, 0, 2096]]
def c200_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([1], 1)]
theorem c200_checked_data : replaySource c200_A c200_O c200_evidence = some c200_result := by decide +kernel
theorem c200_reference_result :
    finitePrimeDiscover 5 5 6 (fun a => rowRight (c200_A a)) c200_O = some c200_result :=
  replaySource_reference 5 5 6 (by decide +kernel) c200_A c200_O c200_evidence c200_result c200_checked_data
theorem c200_all_words (x y : Fin 6 → c200_R) :
    CodeEqual (linearSystem c200_A c200_O) c200_result x y ↔ ObsEq (linearSystem c200_A c200_O) x y :=
  replaySource_all_words c200_A c200_O c200_evidence c200_result c200_checked_data x y
theorem c200_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c200_R) c200_R) :
    taggedRealize (linearSystem c200_A c200_O) (guardedCodeFormula c200_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c200_A c200_O) :=
  replaySource_standard_formula c200_A c200_O c200_evidence c200_result c200_checked_data e
abbrev c201_R := ZMod 65536
def c201_A : Fin 2 → Mat c201_R 8 8 := ![![![17698, 7962, 49699, 37320, 23412, 6538, 39824, 34395], ![23464, 37603, 20556, 32118, 60325, 50701, 6345, 63146], ![7061, 60025, 48800, 57289, 7901, 57423, 17450, 21611], ![57954, 1463, 43061, 61981, 12327, 24535, 55220, 20222], ![9538, 34330, 18991, 25859, 64489, 51532, 7482, 17514], ![8262, 4689, 20524, 11331, 58729, 9597, 8879, 16991], ![38245, 65480, 12079, 48575, 41217, 13059, 11905, 14025], ![40555, 32470, 51819, 35275, 34452, 61245, 54300, 32399]], ![![45667, 60993, 42044, 24680, 13027, 39737, 34859, 3988], ![10393, 29683, 38554, 51204, 39690, 4755, 35121, 61378], ![63427, 47581, 32082, 32486, 44031, 34935, 29965, 8363], ![27479, 23039, 1777, 57316, 32532, 42871, 30241, 7992], ![35244, 37369, 1342, 167, 21177, 50423, 62217, 51013], ![29874, 59333, 42924, 46108, 58455, 35340, 60778, 27268], ![52594, 11868, 27092, 9501, 44582, 25499, 5486, 41184], ![1304, 20195, 44643, 12867, 63107, 13759, 28318, 26332]]]
def c201_O : Mat c201_R 1 8 := ![![7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995]]
def c201_evidence : List (Evidence c201_R 8) := [
  .separation (![1, 0, 0, 0, 0, 0, 0, 0]),
  .separation (![1, 62136, 0, 0, 0, 0, 0, 0]),
  .combination [3, 0],
  .combination [49151, 16386],
  .combination [32766, 32773]]
def c201_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c201_checked_data : replaySource c201_A c201_O c201_evidence = some c201_result := by decide +kernel
theorem c201_reference_result :
    finitePrimeDiscover 2 16 8 (fun a => rowRight (c201_A a)) c201_O = some c201_result :=
  replaySource_reference 2 16 8 (by decide +kernel) c201_A c201_O c201_evidence c201_result c201_checked_data
theorem c201_all_words (x y : Fin 8 → c201_R) :
    CodeEqual (linearSystem c201_A c201_O) c201_result x y ↔ ObsEq (linearSystem c201_A c201_O) x y :=
  replaySource_all_words c201_A c201_O c201_evidence c201_result c201_checked_data x y
theorem c201_standard_definition (e : Fin 2 → TaggedCarrier (Fin 8 → c201_R) c201_R) :
    taggedRealize (linearSystem c201_A c201_O) (guardedCodeFormula c201_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c201_A c201_O) :=
  replaySource_standard_formula c201_A c201_O c201_evidence c201_result c201_checked_data e
abbrev c202_R := ZMod 16777216
def c202_A : Fin 1 → Mat c202_R 1 1 := ![![![1]]]
def c202_O : Mat c202_R 24 1 := ![![8388608], ![4194304], ![2097152], ![1048576], ![524288], ![262144], ![131072], ![65536], ![32768], ![16384], ![8192], ![4096], ![2048], ![1024], ![512], ![256], ![128], ![64], ![32], ![16], ![8], ![4], ![2], ![1]]
def c202_evidence : List (Evidence c202_R 1) := [
  .separation (![1]),
  .separation (![2]),
  .separation (![4]),
  .separation (![8]),
  .separation (![16]),
  .separation (![32]),
  .separation (![64]),
  .separation (![128]),
  .separation (![256]),
  .separation (![512]),
  .separation (![1024]),
  .separation (![2048]),
  .separation (![4096]),
  .separation (![8192]),
  .separation (![16384]),
  .separation (![32768]),
  .separation (![65536]),
  .separation (![131072]),
  .separation (![262144]),
  .separation (![524288]),
  .separation (![1048576]),
  .separation (![2097152]),
  .separation (![4194304]),
  .separation (![8388608]),
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8388608],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4194304],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2097152],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1048576],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 524288],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 262144],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131072],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 65536],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32768],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16384],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8192],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4096],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2048],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1024],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 512],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 256],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
  .combination [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]
def c202_result : List (Test 1 24) := [([], 0), ([], 1), ([], 2), ([], 3), ([], 4), ([], 5), ([], 6), ([], 7), ([], 8), ([], 9), ([], 10), ([], 11), ([], 12), ([], 13), ([], 14), ([], 15), ([], 16), ([], 17), ([], 18), ([], 19), ([], 20), ([], 21), ([], 22), ([], 23)]
theorem c202_checked_data : replaySource c202_A c202_O c202_evidence = some c202_result := by decide +kernel
theorem c202_reference_result :
    finitePrimeDiscover 2 24 1 (fun a => rowRight (c202_A a)) c202_O = some c202_result :=
  replaySource_reference 2 24 1 (by decide +kernel) c202_A c202_O c202_evidence c202_result c202_checked_data
theorem c202_all_words (x y : Fin 1 → c202_R) :
    CodeEqual (linearSystem c202_A c202_O) c202_result x y ↔ ObsEq (linearSystem c202_A c202_O) x y :=
  replaySource_all_words c202_A c202_O c202_evidence c202_result c202_checked_data x y
theorem c202_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c202_R) c202_R) :
    taggedRealize (linearSystem c202_A c202_O) (guardedCodeFormula c202_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c202_A c202_O) :=
  replaySource_standard_formula c202_A c202_O c202_evidence c202_result c202_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch16
