module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch04
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c048_R := ZMod 32
def c048_A : Fin 1 → Mat c048_R 2 2 := ![![![23, 0], ![13, 18]]]
def c048_O : Mat c048_R 2 2 := ![![0, 1], ![15, 19]]
def c048_evidence : List (Evidence c048_R 2) := [
  .separation (![0, 1]),
  .separation (![1, 0]),
  .combination [25, 3],
  .combination [6, 16]]
def c048_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c048_checked_data : replaySource c048_A c048_O c048_evidence = some c048_result := by decide +kernel
theorem c048_reference_result :
    finitePrimeDiscover 2 5 2 (fun a => rowRight (c048_A a)) c048_O = some c048_result :=
  replaySource_reference 2 5 2 (by decide +kernel) c048_A c048_O c048_evidence c048_result c048_checked_data
theorem c048_all_words (x y : Fin 2 → c048_R) :
    CodeEqual (linearSystem c048_A c048_O) c048_result x y ↔ ObsEq (linearSystem c048_A c048_O) x y :=
  replaySource_all_words c048_A c048_O c048_evidence c048_result c048_checked_data x y
theorem c048_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c048_R) c048_R) :
    taggedRealize (linearSystem c048_A c048_O) (guardedCodeFormula c048_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c048_A c048_O) :=
  replaySource_standard_formula c048_A c048_O c048_evidence c048_result c048_checked_data e
abbrev c049_R := ZMod 243
def c049_A : Fin 2 → Mat c049_R 2 2 := ![![![227, 25], ![108, 55]], ![![206, 55], ![85, 197]]]
def c049_O : Mat c049_R 1 2 := ![![162, 0]]
def c049_evidence : List (Evidence c049_R 2) := [
  .separation (![1, 0]),
  .separation (![0, 1]),
  .combination [0, 1],
  .combination [1, 0],
  .combination [0, 1]]
def c049_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c049_checked_data : replaySource c049_A c049_O c049_evidence = some c049_result := by decide +kernel
theorem c049_reference_result :
    finitePrimeDiscover 3 5 2 (fun a => rowRight (c049_A a)) c049_O = some c049_result :=
  replaySource_reference 3 5 2 (by decide +kernel) c049_A c049_O c049_evidence c049_result c049_checked_data
theorem c049_all_words (x y : Fin 2 → c049_R) :
    CodeEqual (linearSystem c049_A c049_O) c049_result x y ↔ ObsEq (linearSystem c049_A c049_O) x y :=
  replaySource_all_words c049_A c049_O c049_evidence c049_result c049_checked_data x y
theorem c049_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c049_R) c049_R) :
    taggedRealize (linearSystem c049_A c049_O) (guardedCodeFormula c049_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c049_A c049_O) :=
  replaySource_standard_formula c049_A c049_O c049_evidence c049_result c049_checked_data e
abbrev c050_R := ZMod 3125
def c050_A : Fin 3 → Mat c050_R 2 2 := ![![![805, 472], ![3032, 359]], ![![2615, 469], ![2949, 110]], ![![1617, 1101], ![2979, 2199]]]
def c050_O : Mat c050_R 2 2 := ![![2612, 2325], ![435, 42]]
def c050_evidence : List (Evidence c050_R 2) := [
  .separation (![1, 0]),
  .separation (![900, 1]),
  .combination [295, 2242],
  .combination [220, 459],
  .combination [212, 1011],
  .combination [1067, 869],
  .combination [1109, 2505],
  .combination [3104, 479]]
def c050_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c050_checked_data : replaySource c050_A c050_O c050_evidence = some c050_result := by decide +kernel
theorem c050_reference_result :
    finitePrimeDiscover 5 5 2 (fun a => rowRight (c050_A a)) c050_O = some c050_result :=
  replaySource_reference 5 5 2 (by decide +kernel) c050_A c050_O c050_evidence c050_result c050_checked_data
theorem c050_all_words (x y : Fin 2 → c050_R) :
    CodeEqual (linearSystem c050_A c050_O) c050_result x y ↔ ObsEq (linearSystem c050_A c050_O) x y :=
  replaySource_all_words c050_A c050_O c050_evidence c050_result c050_checked_data x y
theorem c050_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c050_R) c050_R) :
    taggedRealize (linearSystem c050_A c050_O) (guardedCodeFormula c050_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c050_A c050_O) :=
  replaySource_standard_formula c050_A c050_O c050_evidence c050_result c050_checked_data e
abbrev c051_R := ZMod 2
def c051_A : Fin 1 → Mat c051_R 3 3 := ![![![1, 0, 1], ![0, 1, 0], ![0, 1, 1]]]
def c051_O : Mat c051_R 1 3 := ![![0, 1, 1]]
def c051_evidence : List (Evidence c051_R 3) := [
  .separation (![0, 1, 0]),
  .separation (![0, 1, 1]),
  .combination [1, 0]]
def c051_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c051_checked_data : replaySource c051_A c051_O c051_evidence = some c051_result := by decide +kernel
theorem c051_reference_result :
    finitePrimeDiscover 2 1 3 (fun a => rowRight (c051_A a)) c051_O = some c051_result :=
  replaySource_reference 2 1 3 (by decide +kernel) c051_A c051_O c051_evidence c051_result c051_checked_data
theorem c051_all_words (x y : Fin 3 → c051_R) :
    CodeEqual (linearSystem c051_A c051_O) c051_result x y ↔ ObsEq (linearSystem c051_A c051_O) x y :=
  replaySource_all_words c051_A c051_O c051_evidence c051_result c051_checked_data x y
theorem c051_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c051_R) c051_R) :
    taggedRealize (linearSystem c051_A c051_O) (guardedCodeFormula c051_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c051_A c051_O) :=
  replaySource_standard_formula c051_A c051_O c051_evidence c051_result c051_checked_data e
abbrev c052_R := ZMod 3
def c052_A : Fin 2 → Mat c052_R 3 3 := ![![![2, 0, 1], ![1, 2, 2], ![2, 1, 0]], ![![0, 0, 0], ![1, 1, 2], ![1, 0, 1]]]
def c052_O : Mat c052_R 2 3 := ![![0, 0, 1], ![1, 0, 2]]
def c052_evidence : List (Evidence c052_R 3) := [
  .separation (![0, 0, 1]),
  .separation (![1, 0, 0]),
  .separation (![0, 1, 0]),
  .combination [2, 1, 0],
  .combination [0, 2, 2],
  .combination [1, 2, 0],
  .combination [2, 1, 2],
  .combination [1, 2, 1]]
def c052_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c052_checked_data : replaySource c052_A c052_O c052_evidence = some c052_result := by decide +kernel
theorem c052_reference_result :
    finitePrimeDiscover 3 1 3 (fun a => rowRight (c052_A a)) c052_O = some c052_result :=
  replaySource_reference 3 1 3 (by decide +kernel) c052_A c052_O c052_evidence c052_result c052_checked_data
theorem c052_all_words (x y : Fin 3 → c052_R) :
    CodeEqual (linearSystem c052_A c052_O) c052_result x y ↔ ObsEq (linearSystem c052_A c052_O) x y :=
  replaySource_all_words c052_A c052_O c052_evidence c052_result c052_checked_data x y
theorem c052_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c052_R) c052_R) :
    taggedRealize (linearSystem c052_A c052_O) (guardedCodeFormula c052_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c052_A c052_O) :=
  replaySource_standard_formula c052_A c052_O c052_evidence c052_result c052_checked_data e
abbrev c053_R := ZMod 5
def c053_A : Fin 3 → Mat c053_R 3 3 := ![![![0, 3, 0], ![3, 1, 2], ![3, 3, 4]], ![![3, 3, 3], ![1, 0, 3], ![3, 4, 0]], ![![1, 4, 3], ![3, 2, 2], ![4, 2, 3]]]
def c053_O : Mat c053_R 1 3 := ![![1, 2, 0]]
def c053_evidence : List (Evidence c053_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![3, 1, 0]),
  .combination [4, 1],
  .combination [4, 3],
  .separation (![1, 2, 1]),
  .combination [2, 4, 2],
  .combination [1, 2, 2],
  .combination [2, 1, 0],
  .combination [0, 4, 0],
  .combination [0, 1, 0]]
def c053_result : List (Test 3 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c053_checked_data : replaySource c053_A c053_O c053_evidence = some c053_result := by decide +kernel
theorem c053_reference_result :
    finitePrimeDiscover 5 1 3 (fun a => rowRight (c053_A a)) c053_O = some c053_result :=
  replaySource_reference 5 1 3 (by decide +kernel) c053_A c053_O c053_evidence c053_result c053_checked_data
theorem c053_all_words (x y : Fin 3 → c053_R) :
    CodeEqual (linearSystem c053_A c053_O) c053_result x y ↔ ObsEq (linearSystem c053_A c053_O) x y :=
  replaySource_all_words c053_A c053_O c053_evidence c053_result c053_checked_data x y
theorem c053_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c053_R) c053_R) :
    taggedRealize (linearSystem c053_A c053_O) (guardedCodeFormula c053_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c053_A c053_O) :=
  replaySource_standard_formula c053_A c053_O c053_evidence c053_result c053_checked_data e
abbrev c054_R := ZMod 4
def c054_A : Fin 1 → Mat c054_R 3 3 := ![![![1, 0, 2], ![1, 1, 1], ![0, 1, 3]]]
def c054_O : Mat c054_R 2 3 := ![![0, 1, 1], ![2, 2, 0]]
def c054_evidence : List (Evidence c054_R 3) := [
  .separation (![0, 1, 0]),
  .separation (![1, 0, 0]),
  .separation (![2, 0, 0]),
  .combination [2, 0, 0],
  .combination [0, 0, 3]]
def c054_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c054_checked_data : replaySource c054_A c054_O c054_evidence = some c054_result := by decide +kernel
theorem c054_reference_result :
    finitePrimeDiscover 2 2 3 (fun a => rowRight (c054_A a)) c054_O = some c054_result :=
  replaySource_reference 2 2 3 (by decide +kernel) c054_A c054_O c054_evidence c054_result c054_checked_data
theorem c054_all_words (x y : Fin 3 → c054_R) :
    CodeEqual (linearSystem c054_A c054_O) c054_result x y ↔ ObsEq (linearSystem c054_A c054_O) x y :=
  replaySource_all_words c054_A c054_O c054_evidence c054_result c054_checked_data x y
theorem c054_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c054_R) c054_R) :
    taggedRealize (linearSystem c054_A c054_O) (guardedCodeFormula c054_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c054_A c054_O) :=
  replaySource_standard_formula c054_A c054_O c054_evidence c054_result c054_checked_data e
abbrev c055_R := ZMod 9
def c055_A : Fin 2 → Mat c055_R 3 3 := ![![![5, 4, 5], ![0, 1, 5], ![7, 0, 3]], ![![3, 2, 5], ![5, 3, 3], ![4, 4, 8]]]
def c055_O : Mat c055_R 1 3 := ![![2, 1, 6]]
def c055_evidence : List (Evidence c055_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![4, 1, 0]),
  .separation (![3, 6, 1]),
  .combination [2, 3, 2],
  .combination [0, 2, 5],
  .combination [3, 5, 6],
  .combination [8, 2, 3]]
def c055_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c055_checked_data : replaySource c055_A c055_O c055_evidence = some c055_result := by decide +kernel
theorem c055_reference_result :
    finitePrimeDiscover 3 2 3 (fun a => rowRight (c055_A a)) c055_O = some c055_result :=
  replaySource_reference 3 2 3 (by decide +kernel) c055_A c055_O c055_evidence c055_result c055_checked_data
theorem c055_all_words (x y : Fin 3 → c055_R) :
    CodeEqual (linearSystem c055_A c055_O) c055_result x y ↔ ObsEq (linearSystem c055_A c055_O) x y :=
  replaySource_all_words c055_A c055_O c055_evidence c055_result c055_checked_data x y
theorem c055_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c055_R) c055_R) :
    taggedRealize (linearSystem c055_A c055_O) (guardedCodeFormula c055_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c055_A c055_O) :=
  replaySource_standard_formula c055_A c055_O c055_evidence c055_result c055_checked_data e
abbrev c056_R := ZMod 25
def c056_A : Fin 3 → Mat c056_R 3 3 := ![![![20, 20, 9], ![17, 9, 4], ![5, 7, 18]], ![![20, 23, 3], ![24, 6, 22], ![8, 8, 1]], ![![14, 13, 8], ![14, 24, 8], ![11, 15, 24]]]
def c056_O : Mat c056_R 2 3 := ![![5, 10, 20], ![0, 20, 5]]
def c056_evidence : List (Evidence c056_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![23, 1, 0]),
  .separation (![4, 21, 1]),
  .combination [13, 17, 3],
  .combination [1, 1, 0],
  .combination [12, 10, 4],
  .combination [21, 12, 2],
  .combination [2, 13, 0],
  .combination [19, 18, 2],
  .combination [18, 18, 2],
  .combination [17, 11, 3]]
def c056_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c056_checked_data : replaySource c056_A c056_O c056_evidence = some c056_result := by decide +kernel
theorem c056_reference_result :
    finitePrimeDiscover 5 2 3 (fun a => rowRight (c056_A a)) c056_O = some c056_result :=
  replaySource_reference 5 2 3 (by decide +kernel) c056_A c056_O c056_evidence c056_result c056_checked_data
theorem c056_all_words (x y : Fin 3 → c056_R) :
    CodeEqual (linearSystem c056_A c056_O) c056_result x y ↔ ObsEq (linearSystem c056_A c056_O) x y :=
  replaySource_all_words c056_A c056_O c056_evidence c056_result c056_checked_data x y
theorem c056_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c056_R) c056_R) :
    taggedRealize (linearSystem c056_A c056_O) (guardedCodeFormula c056_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c056_A c056_O) :=
  replaySource_standard_formula c056_A c056_O c056_evidence c056_result c056_checked_data e
abbrev c057_R := ZMod 8
def c057_A : Fin 1 → Mat c057_R 3 3 := ![![![3, 0, 4], ![3, 7, 3], ![2, 5, 6]]]
def c057_O : Mat c057_R 1 3 := ![![0, 6, 5]]
def c057_evidence : List (Evidence c057_R 3) := [
  .separation (![0, 1, 0]),
  .separation (![0, 1, 2]),
  .separation (![1, 4, 0]),
  .combination [5, 6, 0]]
def c057_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c057_checked_data : replaySource c057_A c057_O c057_evidence = some c057_result := by decide +kernel
theorem c057_reference_result :
    finitePrimeDiscover 2 3 3 (fun a => rowRight (c057_A a)) c057_O = some c057_result :=
  replaySource_reference 2 3 3 (by decide +kernel) c057_A c057_O c057_evidence c057_result c057_checked_data
theorem c057_all_words (x y : Fin 3 → c057_R) :
    CodeEqual (linearSystem c057_A c057_O) c057_result x y ↔ ObsEq (linearSystem c057_A c057_O) x y :=
  replaySource_all_words c057_A c057_O c057_evidence c057_result c057_checked_data x y
theorem c057_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c057_R) c057_R) :
    taggedRealize (linearSystem c057_A c057_O) (guardedCodeFormula c057_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c057_A c057_O) :=
  replaySource_standard_formula c057_A c057_O c057_evidence c057_result c057_checked_data e
abbrev c058_R := ZMod 27
def c058_A : Fin 2 → Mat c058_R 3 3 := ![![![23, 16, 24], ![20, 19, 17], ![11, 21, 2]], ![![26, 6, 21], ![13, 25, 16], ![3, 10, 14]]]
def c058_O : Mat c058_R 2 3 := ![![20, 25, 26], ![2, 15, 14]]
def c058_evidence : List (Evidence c058_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![19, 1, 0]),
  .separation (![2, 6, 1]),
  .combination [18, 10, 21],
  .combination [14, 18, 19],
  .combination [11, 15, 3],
  .combination [10, 5, 26],
  .combination [9, 6, 5]]
def c058_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c058_checked_data : replaySource c058_A c058_O c058_evidence = some c058_result := by decide +kernel
theorem c058_reference_result :
    finitePrimeDiscover 3 3 3 (fun a => rowRight (c058_A a)) c058_O = some c058_result :=
  replaySource_reference 3 3 3 (by decide +kernel) c058_A c058_O c058_evidence c058_result c058_checked_data
theorem c058_all_words (x y : Fin 3 → c058_R) :
    CodeEqual (linearSystem c058_A c058_O) c058_result x y ↔ ObsEq (linearSystem c058_A c058_O) x y :=
  replaySource_all_words c058_A c058_O c058_evidence c058_result c058_checked_data x y
theorem c058_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c058_R) c058_R) :
    taggedRealize (linearSystem c058_A c058_O) (guardedCodeFormula c058_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c058_A c058_O) :=
  replaySource_standard_formula c058_A c058_O c058_evidence c058_result c058_checked_data e
abbrev c059_R := ZMod 125
def c059_A : Fin 3 → Mat c059_R 3 3 := ![![![18, 14, 51], ![35, 91, 21], ![104, 16, 39]], ![![35, 111, 1], ![82, 58, 68], ![22, 85, 107]], ![![86, 36, 8], ![94, 45, 23], ![55, 13, 20]]]
def c059_O : Mat c059_R 1 3 := ![![83, 54, 59]]
def c059_evidence : List (Evidence c059_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![37, 1, 0]),
  .separation (![97, 1, 30]),
  .combination [90, 23, 109],
  .combination [72, 72, 61],
  .combination [45, 81, 51],
  .combination [46, 75, 87],
  .combination [13, 31, 76],
  .combination [44, 118, 119],
  .combination [85, 0, 111]]
def c059_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c059_checked_data : replaySource c059_A c059_O c059_evidence = some c059_result := by decide +kernel
theorem c059_reference_result :
    finitePrimeDiscover 5 3 3 (fun a => rowRight (c059_A a)) c059_O = some c059_result :=
  replaySource_reference 5 3 3 (by decide +kernel) c059_A c059_O c059_evidence c059_result c059_checked_data
theorem c059_all_words (x y : Fin 3 → c059_R) :
    CodeEqual (linearSystem c059_A c059_O) c059_result x y ↔ ObsEq (linearSystem c059_A c059_O) x y :=
  replaySource_all_words c059_A c059_O c059_evidence c059_result c059_checked_data x y
theorem c059_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c059_R) c059_R) :
    taggedRealize (linearSystem c059_A c059_O) (guardedCodeFormula c059_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c059_A c059_O) :=
  replaySource_standard_formula c059_A c059_O c059_evidence c059_result c059_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch04
