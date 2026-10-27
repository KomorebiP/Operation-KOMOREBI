module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch12
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c144_R := ZMod 4
def c144_A : Fin 1 → Mat c144_R 3 3 := ![![![1, 1, 2], ![3, 3, 0], ![2, 2, 2]]]
def c144_O : Mat c144_R 2 3 := ![![2, 1, 2], ![1, 1, 1]]
def c144_evidence : List (Evidence c144_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![1, 2, 0]),
  .separation (![3, 0, 1]),
  .combination [0, 0, 2],
  .combination [0, 2, 2]]
def c144_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c144_checked_data : replaySource c144_A c144_O c144_evidence = some c144_result := by decide +kernel
theorem c144_reference_result :
    finitePrimeDiscover 2 2 3 (fun a => rowRight (c144_A a)) c144_O = some c144_result :=
  replaySource_reference 2 2 3 (by decide +kernel) c144_A c144_O c144_evidence c144_result c144_checked_data
theorem c144_all_words (x y : Fin 3 → c144_R) :
    CodeEqual (linearSystem c144_A c144_O) c144_result x y ↔ ObsEq (linearSystem c144_A c144_O) x y :=
  replaySource_all_words c144_A c144_O c144_evidence c144_result c144_checked_data x y
theorem c144_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c144_R) c144_R) :
    taggedRealize (linearSystem c144_A c144_O) (guardedCodeFormula c144_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c144_A c144_O) :=
  replaySource_standard_formula c144_A c144_O c144_evidence c144_result c144_checked_data e
abbrev c145_R := ZMod 9
def c145_A : Fin 2 → Mat c145_R 3 3 := ![![![1, 1, 5], ![0, 2, 0], ![1, 0, 0]], ![![0, 7, 4], ![2, 7, 8], ![2, 8, 7]]]
def c145_O : Mat c145_R 1 3 := ![![7, 5, 8]]
def c145_evidence : List (Evidence c145_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![7, 1, 0]),
  .separation (![6, 8, 1]),
  .separation (![0, 6, 3]),
  .combination [2, 7, 0, 6],
  .combination [6, 8, 0, 3],
  .combination [1, 3, 0, 3],
  .combination [8, 3, 0, 3],
  .combination [7, 7, 0, 8]]
def c145_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c145_checked_data : replaySource c145_A c145_O c145_evidence = some c145_result := by decide +kernel
theorem c145_reference_result :
    finitePrimeDiscover 3 2 3 (fun a => rowRight (c145_A a)) c145_O = some c145_result :=
  replaySource_reference 3 2 3 (by decide +kernel) c145_A c145_O c145_evidence c145_result c145_checked_data
theorem c145_all_words (x y : Fin 3 → c145_R) :
    CodeEqual (linearSystem c145_A c145_O) c145_result x y ↔ ObsEq (linearSystem c145_A c145_O) x y :=
  replaySource_all_words c145_A c145_O c145_evidence c145_result c145_checked_data x y
theorem c145_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c145_R) c145_R) :
    taggedRealize (linearSystem c145_A c145_O) (guardedCodeFormula c145_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c145_A c145_O) :=
  replaySource_standard_formula c145_A c145_O c145_evidence c145_result c145_checked_data e
abbrev c146_R := ZMod 25
def c146_A : Fin 3 → Mat c146_R 3 3 := ![![![9, 0, 3], ![10, 13, 19], ![8, 19, 2]], ![![0, 24, 18], ![3, 17, 7], ![10, 10, 22]], ![![24, 22, 21], ![8, 14, 20], ![5, 8, 0]]]
def c146_O : Mat c146_R 2 3 := ![![2, 6, 5], ![9, 1, 7]]
def c146_evidence : List (Evidence c146_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![22, 1, 0]),
  .separation (![19, 22, 1]),
  .combination [21, 19, 10],
  .combination [0, 6, 19],
  .combination [11, 15, 5],
  .combination [8, 14, 17],
  .combination [20, 7, 17],
  .combination [19, 23, 9],
  .combination [16, 10, 4],
  .combination [11, 4, 6]]
def c146_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c146_checked_data : replaySource c146_A c146_O c146_evidence = some c146_result := by decide +kernel
theorem c146_reference_result :
    finitePrimeDiscover 5 2 3 (fun a => rowRight (c146_A a)) c146_O = some c146_result :=
  replaySource_reference 5 2 3 (by decide +kernel) c146_A c146_O c146_evidence c146_result c146_checked_data
theorem c146_all_words (x y : Fin 3 → c146_R) :
    CodeEqual (linearSystem c146_A c146_O) c146_result x y ↔ ObsEq (linearSystem c146_A c146_O) x y :=
  replaySource_all_words c146_A c146_O c146_evidence c146_result c146_checked_data x y
theorem c146_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c146_R) c146_R) :
    taggedRealize (linearSystem c146_A c146_O) (guardedCodeFormula c146_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c146_A c146_O) :=
  replaySource_standard_formula c146_A c146_O c146_evidence c146_result c146_checked_data e
abbrev c147_R := ZMod 8
def c147_A : Fin 1 → Mat c147_R 3 3 := ![![![6, 2, 0], ![5, 5, 6], ![6, 0, 4]]]
def c147_O : Mat c147_R 1 3 := ![![4, 4, 0]]
def c147_evidence : List (Evidence c147_R 3) := [
  .separation (![1, 0, 0]),
  .combination [1]]
def c147_result : List (Test 1 1) := [([], 0)]
theorem c147_checked_data : replaySource c147_A c147_O c147_evidence = some c147_result := by decide +kernel
theorem c147_reference_result :
    finitePrimeDiscover 2 3 3 (fun a => rowRight (c147_A a)) c147_O = some c147_result :=
  replaySource_reference 2 3 3 (by decide +kernel) c147_A c147_O c147_evidence c147_result c147_checked_data
theorem c147_all_words (x y : Fin 3 → c147_R) :
    CodeEqual (linearSystem c147_A c147_O) c147_result x y ↔ ObsEq (linearSystem c147_A c147_O) x y :=
  replaySource_all_words c147_A c147_O c147_evidence c147_result c147_checked_data x y
theorem c147_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c147_R) c147_R) :
    taggedRealize (linearSystem c147_A c147_O) (guardedCodeFormula c147_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c147_A c147_O) :=
  replaySource_standard_formula c147_A c147_O c147_evidence c147_result c147_checked_data e
abbrev c148_R := ZMod 27
def c148_A : Fin 2 → Mat c148_R 3 3 := ![![![18, 9, 26], ![9, 1, 24], ![26, 22, 4]], ![![8, 10, 13], ![23, 18, 15], ![16, 8, 26]]]
def c148_O : Mat c148_R 2 3 := ![![25, 23, 3], ![20, 4, 4]]
def c148_evidence : List (Evidence c148_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![25, 1, 0]),
  .separation (![25, 1, 9]),
  .combination [6, 15, 5],
  .combination [18, 10, 2],
  .combination [12, 14, 19],
  .combination [10, 21, 13],
  .combination [21, 15, 5]]
def c148_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c148_checked_data : replaySource c148_A c148_O c148_evidence = some c148_result := by decide +kernel
theorem c148_reference_result :
    finitePrimeDiscover 3 3 3 (fun a => rowRight (c148_A a)) c148_O = some c148_result :=
  replaySource_reference 3 3 3 (by decide +kernel) c148_A c148_O c148_evidence c148_result c148_checked_data
theorem c148_all_words (x y : Fin 3 → c148_R) :
    CodeEqual (linearSystem c148_A c148_O) c148_result x y ↔ ObsEq (linearSystem c148_A c148_O) x y :=
  replaySource_all_words c148_A c148_O c148_evidence c148_result c148_checked_data x y
theorem c148_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c148_R) c148_R) :
    taggedRealize (linearSystem c148_A c148_O) (guardedCodeFormula c148_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c148_A c148_O) :=
  replaySource_standard_formula c148_A c148_O c148_evidence c148_result c148_checked_data e
abbrev c149_R := ZMod 125
def c149_A : Fin 3 → Mat c149_R 3 3 := ![![![77, 101, 14], ![27, 120, 50], ![49, 1, 54]], ![![78, 67, 118], ![48, 117, 101], ![84, 92, 110]], ![![27, 38, 37], ![68, 75, 63], ![77, 49, 18]]]
def c149_O : Mat c149_R 1 3 := ![![96, 51, 95]]
def c149_evidence : List (Evidence c149_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![19, 1, 0]),
  .separation (![22, 18, 1]),
  .combination [94, 57, 38],
  .combination [62, 17, 46],
  .combination [12, 114, 8],
  .combination [121, 52, 5],
  .combination [8, 106, 109],
  .combination [22, 12, 66],
  .combination [8, 110, 99]]
def c149_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c149_checked_data : replaySource c149_A c149_O c149_evidence = some c149_result := by decide +kernel
theorem c149_reference_result :
    finitePrimeDiscover 5 3 3 (fun a => rowRight (c149_A a)) c149_O = some c149_result :=
  replaySource_reference 5 3 3 (by decide +kernel) c149_A c149_O c149_evidence c149_result c149_checked_data
theorem c149_all_words (x y : Fin 3 → c149_R) :
    CodeEqual (linearSystem c149_A c149_O) c149_result x y ↔ ObsEq (linearSystem c149_A c149_O) x y :=
  replaySource_all_words c149_A c149_O c149_evidence c149_result c149_checked_data x y
theorem c149_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c149_R) c149_R) :
    taggedRealize (linearSystem c149_A c149_O) (guardedCodeFormula c149_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c149_A c149_O) :=
  replaySource_standard_formula c149_A c149_O c149_evidence c149_result c149_checked_data e
abbrev c150_R := ZMod 16
def c150_A : Fin 1 → Mat c150_R 3 3 := ![![![12, 3, 2], ![15, 2, 3], ![10, 15, 12]]]
def c150_O : Mat c150_R 2 3 := ![![2, 1, 6], ![5, 11, 2]]
def c150_evidence : List (Evidence c150_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![1, 14, 0]),
  .separation (![0, 10, 1]),
  .combination [11, 6, 11],
  .combination [6, 0, 4]]
def c150_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c150_checked_data : replaySource c150_A c150_O c150_evidence = some c150_result := by decide +kernel
theorem c150_reference_result :
    finitePrimeDiscover 2 4 3 (fun a => rowRight (c150_A a)) c150_O = some c150_result :=
  replaySource_reference 2 4 3 (by decide +kernel) c150_A c150_O c150_evidence c150_result c150_checked_data
theorem c150_all_words (x y : Fin 3 → c150_R) :
    CodeEqual (linearSystem c150_A c150_O) c150_result x y ↔ ObsEq (linearSystem c150_A c150_O) x y :=
  replaySource_all_words c150_A c150_O c150_evidence c150_result c150_checked_data x y
theorem c150_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c150_R) c150_R) :
    taggedRealize (linearSystem c150_A c150_O) (guardedCodeFormula c150_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c150_A c150_O) :=
  replaySource_standard_formula c150_A c150_O c150_evidence c150_result c150_checked_data e
abbrev c151_R := ZMod 81
def c151_A : Fin 2 → Mat c151_R 3 3 := ![![![16, 31, 53], ![25, 49, 2], ![47, 75, 50]], ![![9, 31, 44], ![80, 80, 67], ![11, 26, 6]]]
def c151_O : Mat c151_R 1 3 := ![![0, 0, 0]]
def c151_evidence : List (Evidence c151_R 3) := [
  .combination []]
def c151_result : List (Test 2 1) := []
theorem c151_checked_data : replaySource c151_A c151_O c151_evidence = some c151_result := by decide +kernel
theorem c151_reference_result :
    finitePrimeDiscover 3 4 3 (fun a => rowRight (c151_A a)) c151_O = some c151_result :=
  replaySource_reference 3 4 3 (by decide +kernel) c151_A c151_O c151_evidence c151_result c151_checked_data
theorem c151_all_words (x y : Fin 3 → c151_R) :
    CodeEqual (linearSystem c151_A c151_O) c151_result x y ↔ ObsEq (linearSystem c151_A c151_O) x y :=
  replaySource_all_words c151_A c151_O c151_evidence c151_result c151_checked_data x y
theorem c151_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c151_R) c151_R) :
    taggedRealize (linearSystem c151_A c151_O) (guardedCodeFormula c151_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c151_A c151_O) :=
  replaySource_standard_formula c151_A c151_O c151_evidence c151_result c151_checked_data e
abbrev c152_R := ZMod 625
def c152_A : Fin 3 → Mat c152_R 3 3 := ![![![451, 436, 276], ![479, 93, 432], ![589, 339, 233]], ![![484, 347, 456], ![427, 476, 265], ![207, 564, 148]], ![![456, 254, 330], ![443, 360, 400], ![63, 151, 0]]]
def c152_O : Mat c152_R 2 3 := ![![37, 453, 286], ![34, 229, 482]]
def c152_evidence : List (Evidence c152_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![106, 1, 0]),
  .separation (![387, 590, 1]),
  .combination [143, 238, 11],
  .combination [507, 102, 364],
  .combination [437, 407, 97],
  .combination [16, 283, 183],
  .combination [97, 303, 142],
  .combination [390, 438, 370],
  .combination [12, 446, 57],
  .combination [10, 397, 6]]
def c152_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c152_checked_data : replaySource c152_A c152_O c152_evidence = some c152_result := by decide +kernel
theorem c152_reference_result :
    finitePrimeDiscover 5 4 3 (fun a => rowRight (c152_A a)) c152_O = some c152_result :=
  replaySource_reference 5 4 3 (by decide +kernel) c152_A c152_O c152_evidence c152_result c152_checked_data
theorem c152_all_words (x y : Fin 3 → c152_R) :
    CodeEqual (linearSystem c152_A c152_O) c152_result x y ↔ ObsEq (linearSystem c152_A c152_O) x y :=
  replaySource_all_words c152_A c152_O c152_evidence c152_result c152_checked_data x y
theorem c152_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c152_R) c152_R) :
    taggedRealize (linearSystem c152_A c152_O) (guardedCodeFormula c152_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c152_A c152_O) :=
  replaySource_standard_formula c152_A c152_O c152_evidence c152_result c152_checked_data e
abbrev c153_R := ZMod 32
def c153_A : Fin 1 → Mat c153_R 3 3 := ![![![27, 29, 9], ![7, 17, 9], ![16, 8, 6]]]
def c153_O : Mat c153_R 1 3 := ![![16, 8, 24]]
def c153_evidence : List (Evidence c153_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![1, 30, 0]),
  .separation (![0, 29, 1]),
  .combination [0, 0, 0]]
def c153_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c153_checked_data : replaySource c153_A c153_O c153_evidence = some c153_result := by decide +kernel
theorem c153_reference_result :
    finitePrimeDiscover 2 5 3 (fun a => rowRight (c153_A a)) c153_O = some c153_result :=
  replaySource_reference 2 5 3 (by decide +kernel) c153_A c153_O c153_evidence c153_result c153_checked_data
theorem c153_all_words (x y : Fin 3 → c153_R) :
    CodeEqual (linearSystem c153_A c153_O) c153_result x y ↔ ObsEq (linearSystem c153_A c153_O) x y :=
  replaySource_all_words c153_A c153_O c153_evidence c153_result c153_checked_data x y
theorem c153_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c153_R) c153_R) :
    taggedRealize (linearSystem c153_A c153_O) (guardedCodeFormula c153_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c153_A c153_O) :=
  replaySource_standard_formula c153_A c153_O c153_evidence c153_result c153_checked_data e
abbrev c154_R := ZMod 243
def c154_A : Fin 2 → Mat c154_R 3 3 := ![![![116, 198, 222], ![107, 204, 174], ![233, 118, 207]], ![![175, 226, 161], ![216, 153, 179], ![158, 1, 62]]]
def c154_O : Mat c154_R 2 3 := ![![162, 0, 162], ![162, 0, 0]]
def c154_evidence : List (Evidence c154_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![242, 0, 1]),
  .separation (![0, 1, 0]),
  .combination [241, 123, 122],
  .combination [120, 2, 0],
  .combination [242, 1, 1],
  .combination [0, 1, 0],
  .combination [1, 242, 1]]
def c154_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c154_checked_data : replaySource c154_A c154_O c154_evidence = some c154_result := by decide +kernel
theorem c154_reference_result :
    finitePrimeDiscover 3 5 3 (fun a => rowRight (c154_A a)) c154_O = some c154_result :=
  replaySource_reference 3 5 3 (by decide +kernel) c154_A c154_O c154_evidence c154_result c154_checked_data
theorem c154_all_words (x y : Fin 3 → c154_R) :
    CodeEqual (linearSystem c154_A c154_O) c154_result x y ↔ ObsEq (linearSystem c154_A c154_O) x y :=
  replaySource_all_words c154_A c154_O c154_evidence c154_result c154_checked_data x y
theorem c154_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c154_R) c154_R) :
    taggedRealize (linearSystem c154_A c154_O) (guardedCodeFormula c154_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c154_A c154_O) :=
  replaySource_standard_formula c154_A c154_O c154_evidence c154_result c154_checked_data e
abbrev c155_R := ZMod 3125
def c155_A : Fin 3 → Mat c155_R 3 3 := ![![![2481, 458, 154], ![1844, 1174, 1557], ![498, 1764, 589]], ![![1001, 1571, 2305], ![1475, 48, 1870], ![1439, 2881, 1601]], ![![2436, 873, 1668], ![405, 1803, 791], ![2667, 589, 1326]]]
def c155_O : Mat c155_R 1 3 := ![![2013, 514, 992]]
def c155_evidence : List (Evidence c155_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![422, 1, 0]),
  .separation (![1619, 1774, 1]),
  .combination [3092, 2148, 1451],
  .combination [1498, 2861, 757],
  .combination [937, 2259, 1796],
  .combination [2900, 1348, 3041],
  .combination [1654, 2974, 1383],
  .combination [1836, 1006, 391],
  .combination [645, 2309, 1125]]
def c155_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c155_checked_data : replaySource c155_A c155_O c155_evidence = some c155_result := by decide +kernel
theorem c155_reference_result :
    finitePrimeDiscover 5 5 3 (fun a => rowRight (c155_A a)) c155_O = some c155_result :=
  replaySource_reference 5 5 3 (by decide +kernel) c155_A c155_O c155_evidence c155_result c155_checked_data
theorem c155_all_words (x y : Fin 3 → c155_R) :
    CodeEqual (linearSystem c155_A c155_O) c155_result x y ↔ ObsEq (linearSystem c155_A c155_O) x y :=
  replaySource_all_words c155_A c155_O c155_evidence c155_result c155_checked_data x y
theorem c155_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c155_R) c155_R) :
    taggedRealize (linearSystem c155_A c155_O) (guardedCodeFormula c155_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c155_A c155_O) :=
  replaySource_standard_formula c155_A c155_O c155_evidence c155_result c155_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch12
