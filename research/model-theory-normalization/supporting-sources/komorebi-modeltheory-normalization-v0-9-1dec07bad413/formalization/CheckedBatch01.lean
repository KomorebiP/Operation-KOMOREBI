module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch01
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c012_R := ZMod 243
def c012_A : Fin 2 → Mat c012_R 6 6 := ![![![184, 123, 124, 190, 155, 27], ![111, 172, 118, 22, 5, 225], ![211, 96, 121, 72, 191, 42], ![227, 174, 126, 126, 229, 215], ![22, 143, 124, 135, 45, 174], ![205, 149, 202, 67, 239, 140]], ![![176, 8, 65, 21, 105, 238], ![18, 175, 199, 155, 46, 78], ![201, 131, 46, 190, 141, 105], ![184, 198, 157, 93, 52, 129], ![164, 49, 20, 134, 71, 205], ![175, 56, 166, 209, 87, 11]]]
def c012_O : Mat c012_R 1 6 := ![![13, 209, 121, 160, 68, 232]]
def c012_evidence : List (Evidence c012_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![40, 1, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [161, 83],
  .combination [1, 1]]
def c012_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c012_checked_data : replaySource c012_A c012_O c012_evidence = some c012_result := by decide +kernel
theorem c012_reference_result :
    finitePrimeDiscover 3 5 6 (fun a => rowRight (c012_A a)) c012_O = some c012_result :=
  replaySource_reference 3 5 6 (by decide +kernel) c012_A c012_O c012_evidence c012_result c012_checked_data
theorem c012_all_words (x y : Fin 6 → c012_R) :
    CodeEqual (linearSystem c012_A c012_O) c012_result x y ↔ ObsEq (linearSystem c012_A c012_O) x y :=
  replaySource_all_words c012_A c012_O c012_evidence c012_result c012_checked_data x y
theorem c012_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c012_R) c012_R) :
    taggedRealize (linearSystem c012_A c012_O) (guardedCodeFormula c012_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c012_A c012_O) :=
  replaySource_standard_formula c012_A c012_O c012_evidence c012_result c012_checked_data e
abbrev c013_R := ZMod 25
def c013_A : Fin 2 → Mat c013_R 4 4 := ![![![11, 18, 15, 13], ![22, 13, 2, 10], ![0, 12, 6, 12], ![7, 9, 17, 23]], ![![15, 24, 10, 8], ![7, 10, 21, 20], ![7, 6, 7, 17], ![9, 10, 17, 13]]]
def c013_O : Mat c013_R 1 4 := ![![7, 10, 17, 5]]
def c013_evidence : List (Evidence c013_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![20, 1, 0, 0]),
  .combination [2, 0],
  .combination [19, 7],
  .combination [1, 1]]
def c013_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c013_checked_data : replaySource c013_A c013_O c013_evidence = some c013_result := by decide +kernel
theorem c013_reference_result :
    finitePrimeDiscover 5 2 4 (fun a => rowRight (c013_A a)) c013_O = some c013_result :=
  replaySource_reference 5 2 4 (by decide +kernel) c013_A c013_O c013_evidence c013_result c013_checked_data
theorem c013_all_words (x y : Fin 4 → c013_R) :
    CodeEqual (linearSystem c013_A c013_O) c013_result x y ↔ ObsEq (linearSystem c013_A c013_O) x y :=
  replaySource_all_words c013_A c013_O c013_evidence c013_result c013_checked_data x y
theorem c013_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c013_R) c013_R) :
    taggedRealize (linearSystem c013_A c013_O) (guardedCodeFormula c013_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c013_A c013_O) :=
  replaySource_standard_formula c013_A c013_O c013_evidence c013_result c013_checked_data e
abbrev c014_R := ZMod 25
def c014_A : Fin 2 → Mat c014_R 6 6 := ![![![3, 2, 14, 14, 5, 17], ![16, 12, 4, 7, 21, 19], ![1, 15, 21, 16, 23, 1], ![16, 12, 13, 15, 14, 13], ![15, 7, 19, 0, 5, 3], ![18, 19, 22, 0, 4, 23]], ![![7, 15, 9, 10, 10, 4], ![9, 18, 8, 7, 23, 17], ![10, 19, 14, 3, 7, 9], ![14, 22, 24, 1, 8, 12], ![22, 13, 13, 0, 0, 3], ![2, 1, 20, 23, 16, 11]]]
def c014_O : Mat c014_R 1 6 := ![![8, 10, 12, 24, 16, 6]]
def c014_evidence : List (Evidence c014_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![5, 1, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [19, 7],
  .combination [1, 1]]
def c014_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c014_checked_data : replaySource c014_A c014_O c014_evidence = some c014_result := by decide +kernel
theorem c014_reference_result :
    finitePrimeDiscover 5 2 6 (fun a => rowRight (c014_A a)) c014_O = some c014_result :=
  replaySource_reference 5 2 6 (by decide +kernel) c014_A c014_O c014_evidence c014_result c014_checked_data
theorem c014_all_words (x y : Fin 6 → c014_R) :
    CodeEqual (linearSystem c014_A c014_O) c014_result x y ↔ ObsEq (linearSystem c014_A c014_O) x y :=
  replaySource_all_words c014_A c014_O c014_evidence c014_result c014_checked_data x y
theorem c014_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c014_R) c014_R) :
    taggedRealize (linearSystem c014_A c014_O) (guardedCodeFormula c014_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c014_A c014_O) :=
  replaySource_standard_formula c014_A c014_O c014_evidence c014_result c014_checked_data e
abbrev c015_R := ZMod 125
def c015_A : Fin 2 → Mat c015_R 4 4 := ![![![107, 100, 59, 102], ![31, 82, 32, 118], ![44, 59, 114, 122], ![76, 103, 48, 106]], ![![87, 48, 97, 68], ![114, 12, 121, 117], ![76, 14, 25, 78], ![102, 120, 100, 77]]]
def c015_O : Mat c015_R 1 4 := ![![8, 22, 94, 9]]
def c015_evidence : List (Evidence c015_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![91, 1, 0, 0]),
  .combination [2, 0],
  .combination [124, 2],
  .combination [1, 1]]
def c015_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c015_checked_data : replaySource c015_A c015_O c015_evidence = some c015_result := by decide +kernel
theorem c015_reference_result :
    finitePrimeDiscover 5 3 4 (fun a => rowRight (c015_A a)) c015_O = some c015_result :=
  replaySource_reference 5 3 4 (by decide +kernel) c015_A c015_O c015_evidence c015_result c015_checked_data
theorem c015_all_words (x y : Fin 4 → c015_R) :
    CodeEqual (linearSystem c015_A c015_O) c015_result x y ↔ ObsEq (linearSystem c015_A c015_O) x y :=
  replaySource_all_words c015_A c015_O c015_evidence c015_result c015_checked_data x y
theorem c015_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c015_R) c015_R) :
    taggedRealize (linearSystem c015_A c015_O) (guardedCodeFormula c015_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c015_A c015_O) :=
  replaySource_standard_formula c015_A c015_O c015_evidence c015_result c015_checked_data e
abbrev c016_R := ZMod 125
def c016_A : Fin 2 → Mat c016_R 6 6 := ![![![52, 61, 40, 58, 2, 13], ![35, 79, 5, 53, 52, 31], ![41, 37, 72, 7, 66, 36], ![98, 108, 112, 116, 107, 124], ![117, 41, 102, 91, 18, 27], ![51, 31, 33, 57, 18, 50]], ![![119, 19, 12, 50, 121, 34], ![38, 48, 16, 13, 39, 30], ![101, 6, 114, 106, 49, 58], ![106, 44, 83, 111, 5, 102], ![93, 74, 92, 28, 29, 1], ![120, 61, 7, 104, 58, 80]]]
def c016_O : Mat c016_R 1 6 := ![![68, 57, 19, 124, 65, 71]]
def c016_evidence : List (Evidence c016_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [124, 2],
  .combination [1, 1]]
def c016_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c016_checked_data : replaySource c016_A c016_O c016_evidence = some c016_result := by decide +kernel
theorem c016_reference_result :
    finitePrimeDiscover 5 3 6 (fun a => rowRight (c016_A a)) c016_O = some c016_result :=
  replaySource_reference 5 3 6 (by decide +kernel) c016_A c016_O c016_evidence c016_result c016_checked_data
theorem c016_all_words (x y : Fin 6 → c016_R) :
    CodeEqual (linearSystem c016_A c016_O) c016_result x y ↔ ObsEq (linearSystem c016_A c016_O) x y :=
  replaySource_all_words c016_A c016_O c016_evidence c016_result c016_checked_data x y
theorem c016_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c016_R) c016_R) :
    taggedRealize (linearSystem c016_A c016_O) (guardedCodeFormula c016_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c016_A c016_O) :=
  replaySource_standard_formula c016_A c016_O c016_evidence c016_result c016_checked_data e
abbrev c017_R := ZMod 3125
def c017_A : Fin 2 → Mat c017_R 4 4 := ![![![1754, 2237, 1761, 2455], ![784, 2076, 1344, 294], ![2125, 336, 2000, 576], ![1445, 2441, 209, 2587]], ![![1650, 544, 2801, 2817], ![2137, 492, 1519, 1975], ![3022, 1702, 2591, 1281], ![1226, 2769, 1402, 472]]]
def c017_O : Mat c017_R 1 4 := ![![1034, 2592, 2787, 1425]]
def c017_evidence : List (Evidence c017_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![2512, 1, 0, 0]),
  .combination [2, 0],
  .combination [2499, 627],
  .combination [1, 1]]
def c017_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c017_checked_data : replaySource c017_A c017_O c017_evidence = some c017_result := by decide +kernel
theorem c017_reference_result :
    finitePrimeDiscover 5 5 4 (fun a => rowRight (c017_A a)) c017_O = some c017_result :=
  replaySource_reference 5 5 4 (by decide +kernel) c017_A c017_O c017_evidence c017_result c017_checked_data
theorem c017_all_words (x y : Fin 4 → c017_R) :
    CodeEqual (linearSystem c017_A c017_O) c017_result x y ↔ ObsEq (linearSystem c017_A c017_O) x y :=
  replaySource_all_words c017_A c017_O c017_evidence c017_result c017_checked_data x y
theorem c017_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c017_R) c017_R) :
    taggedRealize (linearSystem c017_A c017_O) (guardedCodeFormula c017_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c017_A c017_O) :=
  replaySource_standard_formula c017_A c017_O c017_evidence c017_result c017_checked_data e
abbrev c018_R := ZMod 3125
def c018_A : Fin 2 → Mat c018_R 6 6 := ![![![2782, 2556, 2688, 2508, 140, 2737], ![1694, 794, 2974, 1322, 2897, 1181], ![1768, 1733, 862, 603, 1549, 373], ![1794, 2608, 1809, 253, 1036, 1130], ![2129, 2543, 2842, 1023, 814, 104], ![1453, 1043, 2716, 43, 2408, 313]], ![![2022, 2885, 504, 683, 135, 177], ![1542, 1644, 963, 2260, 966, 741], ![142, 1551, 2273, 1017, 819, 1891], ![2644, 10, 1040, 2822, 2981, 476], ![2226, 725, 2070, 2845, 702, 2323], ![3077, 2131, 1181, 111, 2953, 64]]]
def c018_O : Mat c018_R 1 6 := ![![784, 269, 276, 794, 137, 1916]]
def c018_evidence : List (Evidence c018_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![2459, 1, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [3124, 2],
  .combination [1, 1]]
def c018_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c018_checked_data : replaySource c018_A c018_O c018_evidence = some c018_result := by decide +kernel
theorem c018_reference_result :
    finitePrimeDiscover 5 5 6 (fun a => rowRight (c018_A a)) c018_O = some c018_result :=
  replaySource_reference 5 5 6 (by decide +kernel) c018_A c018_O c018_evidence c018_result c018_checked_data
theorem c018_all_words (x y : Fin 6 → c018_R) :
    CodeEqual (linearSystem c018_A c018_O) c018_result x y ↔ ObsEq (linearSystem c018_A c018_O) x y :=
  replaySource_all_words c018_A c018_O c018_evidence c018_result c018_checked_data x y
theorem c018_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c018_R) c018_R) :
    taggedRealize (linearSystem c018_A c018_O) (guardedCodeFormula c018_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c018_A c018_O) :=
  replaySource_standard_formula c018_A c018_O c018_evidence c018_result c018_checked_data e
abbrev c019_R := ZMod 2
def c019_A : Fin 1 → Mat c019_R 1 1 := ![![![1]]]
def c019_O : Mat c019_R 1 1 := ![![0]]
def c019_evidence : List (Evidence c019_R 1) := [
  .combination []]
def c019_result : List (Test 1 1) := []
theorem c019_checked_data : replaySource c019_A c019_O c019_evidence = some c019_result := by decide +kernel
theorem c019_reference_result :
    finitePrimeDiscover 2 1 1 (fun a => rowRight (c019_A a)) c019_O = some c019_result :=
  replaySource_reference 2 1 1 (by decide +kernel) c019_A c019_O c019_evidence c019_result c019_checked_data
theorem c019_all_words (x y : Fin 1 → c019_R) :
    CodeEqual (linearSystem c019_A c019_O) c019_result x y ↔ ObsEq (linearSystem c019_A c019_O) x y :=
  replaySource_all_words c019_A c019_O c019_evidence c019_result c019_checked_data x y
theorem c019_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c019_R) c019_R) :
    taggedRealize (linearSystem c019_A c019_O) (guardedCodeFormula c019_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c019_A c019_O) :=
  replaySource_standard_formula c019_A c019_O c019_evidence c019_result c019_checked_data e
abbrev c020_R := ZMod 4
def c020_A : Fin 1 → Mat c020_R 1 1 := ![![![1]]]
def c020_O : Mat c020_R 1 1 := ![![2]]
def c020_evidence : List (Evidence c020_R 1) := [
  .separation (![1]),
  .combination [1]]
def c020_result : List (Test 1 1) := [([], 0)]
theorem c020_checked_data : replaySource c020_A c020_O c020_evidence = some c020_result := by decide +kernel
theorem c020_reference_result :
    finitePrimeDiscover 2 2 1 (fun a => rowRight (c020_A a)) c020_O = some c020_result :=
  replaySource_reference 2 2 1 (by decide +kernel) c020_A c020_O c020_evidence c020_result c020_checked_data
theorem c020_all_words (x y : Fin 1 → c020_R) :
    CodeEqual (linearSystem c020_A c020_O) c020_result x y ↔ ObsEq (linearSystem c020_A c020_O) x y :=
  replaySource_all_words c020_A c020_O c020_evidence c020_result c020_checked_data x y
theorem c020_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c020_R) c020_R) :
    taggedRealize (linearSystem c020_A c020_O) (guardedCodeFormula c020_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c020_A c020_O) :=
  replaySource_standard_formula c020_A c020_O c020_evidence c020_result c020_checked_data e
abbrev c021_R := ZMod 2
def c021_A : Fin 1 → Mat c021_R 1 1 := ![![![1]]]
def c021_O : Mat c021_R 1 1 := ![![0]]
def c021_evidence : List (Evidence c021_R 1) := [
  .combination []]
def c021_result : List (Test 1 1) := []
theorem c021_checked_data : replaySource c021_A c021_O c021_evidence = some c021_result := by decide +kernel
theorem c021_reference_result :
    finitePrimeDiscover 2 1 1 (fun a => rowRight (c021_A a)) c021_O = some c021_result :=
  replaySource_reference 2 1 1 (by decide +kernel) c021_A c021_O c021_evidence c021_result c021_checked_data
theorem c021_all_words (x y : Fin 1 → c021_R) :
    CodeEqual (linearSystem c021_A c021_O) c021_result x y ↔ ObsEq (linearSystem c021_A c021_O) x y :=
  replaySource_all_words c021_A c021_O c021_evidence c021_result c021_checked_data x y
theorem c021_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c021_R) c021_R) :
    taggedRealize (linearSystem c021_A c021_O) (guardedCodeFormula c021_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c021_A c021_O) :=
  replaySource_standard_formula c021_A c021_O c021_evidence c021_result c021_checked_data e
abbrev c022_R := ZMod 3
def c022_A : Fin 2 → Mat c022_R 1 1 := ![![![0]], ![![1]]]
def c022_O : Mat c022_R 2 1 := ![![2], ![1]]
def c022_evidence : List (Evidence c022_R 1) := [
  .separation (![1]),
  .combination [2],
  .combination [0],
  .combination [1]]
def c022_result : List (Test 2 2) := [([], 0)]
theorem c022_checked_data : replaySource c022_A c022_O c022_evidence = some c022_result := by decide +kernel
theorem c022_reference_result :
    finitePrimeDiscover 3 1 1 (fun a => rowRight (c022_A a)) c022_O = some c022_result :=
  replaySource_reference 3 1 1 (by decide +kernel) c022_A c022_O c022_evidence c022_result c022_checked_data
theorem c022_all_words (x y : Fin 1 → c022_R) :
    CodeEqual (linearSystem c022_A c022_O) c022_result x y ↔ ObsEq (linearSystem c022_A c022_O) x y :=
  replaySource_all_words c022_A c022_O c022_evidence c022_result c022_checked_data x y
theorem c022_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c022_R) c022_R) :
    taggedRealize (linearSystem c022_A c022_O) (guardedCodeFormula c022_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c022_A c022_O) :=
  replaySource_standard_formula c022_A c022_O c022_evidence c022_result c022_checked_data e
abbrev c023_R := ZMod 5
def c023_A : Fin 3 → Mat c023_R 1 1 := ![![![3]], ![![1]], ![![3]]]
def c023_O : Mat c023_R 1 1 := ![![1]]
def c023_evidence : List (Evidence c023_R 1) := [
  .separation (![1]),
  .combination [3],
  .combination [1],
  .combination [3]]
def c023_result : List (Test 3 1) := [([], 0)]
theorem c023_checked_data : replaySource c023_A c023_O c023_evidence = some c023_result := by decide +kernel
theorem c023_reference_result :
    finitePrimeDiscover 5 1 1 (fun a => rowRight (c023_A a)) c023_O = some c023_result :=
  replaySource_reference 5 1 1 (by decide +kernel) c023_A c023_O c023_evidence c023_result c023_checked_data
theorem c023_all_words (x y : Fin 1 → c023_R) :
    CodeEqual (linearSystem c023_A c023_O) c023_result x y ↔ ObsEq (linearSystem c023_A c023_O) x y :=
  replaySource_all_words c023_A c023_O c023_evidence c023_result c023_checked_data x y
theorem c023_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c023_R) c023_R) :
    taggedRealize (linearSystem c023_A c023_O) (guardedCodeFormula c023_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c023_A c023_O) :=
  replaySource_standard_formula c023_A c023_O c023_evidence c023_result c023_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch01
