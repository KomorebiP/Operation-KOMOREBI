module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch11
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c132_R := ZMod 8
def c132_A : Fin 1 → Mat c132_R 2 2 := ![![![2, 6], ![1, 2]]]
def c132_O : Mat c132_R 2 2 := ![![0, 7], ![1, 2]]
def c132_evidence : List (Evidence c132_R 2) := [
  .separation (![0, 1]),
  .separation (![1, 0]),
  .combination [0, 7],
  .combination [6, 4]]
def c132_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c132_checked_data : replaySource c132_A c132_O c132_evidence = some c132_result := by decide +kernel
theorem c132_reference_result :
    finitePrimeDiscover 2 3 2 (fun a => rowRight (c132_A a)) c132_O = some c132_result :=
  replaySource_reference 2 3 2 (by decide +kernel) c132_A c132_O c132_evidence c132_result c132_checked_data
theorem c132_all_words (x y : Fin 2 → c132_R) :
    CodeEqual (linearSystem c132_A c132_O) c132_result x y ↔ ObsEq (linearSystem c132_A c132_O) x y :=
  replaySource_all_words c132_A c132_O c132_evidence c132_result c132_checked_data x y
theorem c132_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c132_R) c132_R) :
    taggedRealize (linearSystem c132_A c132_O) (guardedCodeFormula c132_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c132_A c132_O) :=
  replaySource_standard_formula c132_A c132_O c132_evidence c132_result c132_checked_data e
abbrev c133_R := ZMod 27
def c133_A : Fin 2 → Mat c133_R 2 2 := ![![![8, 19], ![16, 11]], ![![23, 7], ![3, 6]]]
def c133_O : Mat c133_R 1 2 := ![![0, 18]]
def c133_evidence : List (Evidence c133_R 2) := [
  .separation (![0, 1]),
  .separation (![1, 0]),
  .combination [0, 0],
  .combination [0, 1],
  .combination [21, 14]]
def c133_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c133_checked_data : replaySource c133_A c133_O c133_evidence = some c133_result := by decide +kernel
theorem c133_reference_result :
    finitePrimeDiscover 3 3 2 (fun a => rowRight (c133_A a)) c133_O = some c133_result :=
  replaySource_reference 3 3 2 (by decide +kernel) c133_A c133_O c133_evidence c133_result c133_checked_data
theorem c133_all_words (x y : Fin 2 → c133_R) :
    CodeEqual (linearSystem c133_A c133_O) c133_result x y ↔ ObsEq (linearSystem c133_A c133_O) x y :=
  replaySource_all_words c133_A c133_O c133_evidence c133_result c133_checked_data x y
theorem c133_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c133_R) c133_R) :
    taggedRealize (linearSystem c133_A c133_O) (guardedCodeFormula c133_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c133_A c133_O) :=
  replaySource_standard_formula c133_A c133_O c133_evidence c133_result c133_checked_data e
abbrev c134_R := ZMod 125
def c134_A : Fin 3 → Mat c134_R 2 2 := ![![![117, 9], ![41, 14]], ![![20, 38], ![115, 7]], ![![68, 12], ![18, 83]]]
def c134_O : Mat c134_R 2 2 := ![![77, 74], ![33, 2]]
def c134_evidence : List (Evidence c134_R 2) := [
  .separation (![1, 0]),
  .separation (![38, 1]),
  .combination [42, 123],
  .combination [54, 99],
  .combination [34, 25],
  .combination [78, 89],
  .combination [28, 98],
  .combination [72, 117]]
def c134_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c134_checked_data : replaySource c134_A c134_O c134_evidence = some c134_result := by decide +kernel
theorem c134_reference_result :
    finitePrimeDiscover 5 3 2 (fun a => rowRight (c134_A a)) c134_O = some c134_result :=
  replaySource_reference 5 3 2 (by decide +kernel) c134_A c134_O c134_evidence c134_result c134_checked_data
theorem c134_all_words (x y : Fin 2 → c134_R) :
    CodeEqual (linearSystem c134_A c134_O) c134_result x y ↔ ObsEq (linearSystem c134_A c134_O) x y :=
  replaySource_all_words c134_A c134_O c134_evidence c134_result c134_checked_data x y
theorem c134_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c134_R) c134_R) :
    taggedRealize (linearSystem c134_A c134_O) (guardedCodeFormula c134_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c134_A c134_O) :=
  replaySource_standard_formula c134_A c134_O c134_evidence c134_result c134_checked_data e
abbrev c135_R := ZMod 16
def c135_A : Fin 1 → Mat c135_R 2 2 := ![![![9, 13], ![3, 8]]]
def c135_O : Mat c135_R 1 2 := ![![14, 10]]
def c135_evidence : List (Evidence c135_R 2) := [
  .separation (![1, 0]),
  .separation (![13, 1]),
  .combination [7, 1]]
def c135_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c135_checked_data : replaySource c135_A c135_O c135_evidence = some c135_result := by decide +kernel
theorem c135_reference_result :
    finitePrimeDiscover 2 4 2 (fun a => rowRight (c135_A a)) c135_O = some c135_result :=
  replaySource_reference 2 4 2 (by decide +kernel) c135_A c135_O c135_evidence c135_result c135_checked_data
theorem c135_all_words (x y : Fin 2 → c135_R) :
    CodeEqual (linearSystem c135_A c135_O) c135_result x y ↔ ObsEq (linearSystem c135_A c135_O) x y :=
  replaySource_all_words c135_A c135_O c135_evidence c135_result c135_checked_data x y
theorem c135_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c135_R) c135_R) :
    taggedRealize (linearSystem c135_A c135_O) (guardedCodeFormula c135_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c135_A c135_O) :=
  replaySource_standard_formula c135_A c135_O c135_evidence c135_result c135_checked_data e
abbrev c136_R := ZMod 81
def c136_A : Fin 2 → Mat c136_R 2 2 := ![![![2, 68], ![7, 64]], ![![56, 27], ![31, 42]]]
def c136_O : Mat c136_R 2 2 := ![![75, 9], ![78, 50]]
def c136_evidence : List (Evidence c136_R 2) := [
  .separation (![1, 0]),
  .separation (![69, 1]),
  .combination [44, 57],
  .combination [14, 18],
  .separation (![27, 0]),
  .combination [0, 44, 19],
  .combination [0, 24, 66],
  .combination [0, 24, 54]]
def c136_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 1)]
theorem c136_checked_data : replaySource c136_A c136_O c136_evidence = some c136_result := by decide +kernel
theorem c136_reference_result :
    finitePrimeDiscover 3 4 2 (fun a => rowRight (c136_A a)) c136_O = some c136_result :=
  replaySource_reference 3 4 2 (by decide +kernel) c136_A c136_O c136_evidence c136_result c136_checked_data
theorem c136_all_words (x y : Fin 2 → c136_R) :
    CodeEqual (linearSystem c136_A c136_O) c136_result x y ↔ ObsEq (linearSystem c136_A c136_O) x y :=
  replaySource_all_words c136_A c136_O c136_evidence c136_result c136_checked_data x y
theorem c136_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c136_R) c136_R) :
    taggedRealize (linearSystem c136_A c136_O) (guardedCodeFormula c136_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c136_A c136_O) :=
  replaySource_standard_formula c136_A c136_O c136_evidence c136_result c136_checked_data e
abbrev c137_R := ZMod 625
def c137_A : Fin 3 → Mat c137_R 2 2 := ![![![160, 259], ![36, 470]], ![![112, 271], ![302, 184]], ![![600, 11], ![332, 216]]]
def c137_O : Mat c137_R 1 2 := ![![323, 376]]
def c137_evidence : List (Evidence c137_R 2) := [
  .separation (![1, 0]),
  .separation (![113, 1]),
  .separation (![375, 125]),
  .combination [349, 0, 385],
  .combination [409, 0, 550],
  .combination [115, 0, 192],
  .combination [578, 0, 315],
  .combination [476, 0, 498],
  .combination [609, 0, 296],
  .combination [41, 0, 467]]
def c137_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c137_checked_data : replaySource c137_A c137_O c137_evidence = some c137_result := by decide +kernel
theorem c137_reference_result :
    finitePrimeDiscover 5 4 2 (fun a => rowRight (c137_A a)) c137_O = some c137_result :=
  replaySource_reference 5 4 2 (by decide +kernel) c137_A c137_O c137_evidence c137_result c137_checked_data
theorem c137_all_words (x y : Fin 2 → c137_R) :
    CodeEqual (linearSystem c137_A c137_O) c137_result x y ↔ ObsEq (linearSystem c137_A c137_O) x y :=
  replaySource_all_words c137_A c137_O c137_evidence c137_result c137_checked_data x y
theorem c137_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c137_R) c137_R) :
    taggedRealize (linearSystem c137_A c137_O) (guardedCodeFormula c137_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c137_A c137_O) :=
  replaySource_standard_formula c137_A c137_O c137_evidence c137_result c137_checked_data e
abbrev c138_R := ZMod 32
def c138_A : Fin 1 → Mat c138_R 2 2 := ![![![18, 26], ![8, 27]]]
def c138_O : Mat c138_R 2 2 := ![![0, 0], ![0, 0]]
def c138_evidence : List (Evidence c138_R 2) := [
  .combination [],
  .combination []]
def c138_result : List (Test 1 2) := []
theorem c138_checked_data : replaySource c138_A c138_O c138_evidence = some c138_result := by decide +kernel
theorem c138_reference_result :
    finitePrimeDiscover 2 5 2 (fun a => rowRight (c138_A a)) c138_O = some c138_result :=
  replaySource_reference 2 5 2 (by decide +kernel) c138_A c138_O c138_evidence c138_result c138_checked_data
theorem c138_all_words (x y : Fin 2 → c138_R) :
    CodeEqual (linearSystem c138_A c138_O) c138_result x y ↔ ObsEq (linearSystem c138_A c138_O) x y :=
  replaySource_all_words c138_A c138_O c138_evidence c138_result c138_checked_data x y
theorem c138_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c138_R) c138_R) :
    taggedRealize (linearSystem c138_A c138_O) (guardedCodeFormula c138_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c138_A c138_O) :=
  replaySource_standard_formula c138_A c138_O c138_evidence c138_result c138_checked_data e
abbrev c139_R := ZMod 243
def c139_A : Fin 2 → Mat c139_R 2 2 := ![![![109, 100], ![137, 233]], ![![17, 239], ![10, 206]]]
def c139_O : Mat c139_R 1 2 := ![![65, 238]]
def c139_evidence : List (Evidence c139_R 2) := [
  .separation (![1, 0]),
  .separation (![187, 1]),
  .combination [233, 166],
  .combination [210, 99],
  .combination [152, 233]]
def c139_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c139_checked_data : replaySource c139_A c139_O c139_evidence = some c139_result := by decide +kernel
theorem c139_reference_result :
    finitePrimeDiscover 3 5 2 (fun a => rowRight (c139_A a)) c139_O = some c139_result :=
  replaySource_reference 3 5 2 (by decide +kernel) c139_A c139_O c139_evidence c139_result c139_checked_data
theorem c139_all_words (x y : Fin 2 → c139_R) :
    CodeEqual (linearSystem c139_A c139_O) c139_result x y ↔ ObsEq (linearSystem c139_A c139_O) x y :=
  replaySource_all_words c139_A c139_O c139_evidence c139_result c139_checked_data x y
theorem c139_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c139_R) c139_R) :
    taggedRealize (linearSystem c139_A c139_O) (guardedCodeFormula c139_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c139_A c139_O) :=
  replaySource_standard_formula c139_A c139_O c139_evidence c139_result c139_checked_data e
abbrev c140_R := ZMod 3125
def c140_A : Fin 3 → Mat c140_R 2 2 := ![![![2270, 2895], ![999, 1360]], ![![2693, 1881], ![1839, 1588]], ![![1611, 1262], ![2592, 864]]]
def c140_O : Mat c140_R 2 2 := ![![1250, 1250], ![2500, 0]]
def c140_evidence : List (Evidence c140_R 2) := [
  .separation (![1, 0]),
  .separation (![3124, 1]),
  .combination [1560, 2],
  .combination [3119, 4],
  .combination [1561, 1],
  .combination [0, 0],
  .combination [3122, 2],
  .combination [3119, 4]]
def c140_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c140_checked_data : replaySource c140_A c140_O c140_evidence = some c140_result := by decide +kernel
theorem c140_reference_result :
    finitePrimeDiscover 5 5 2 (fun a => rowRight (c140_A a)) c140_O = some c140_result :=
  replaySource_reference 5 5 2 (by decide +kernel) c140_A c140_O c140_evidence c140_result c140_checked_data
theorem c140_all_words (x y : Fin 2 → c140_R) :
    CodeEqual (linearSystem c140_A c140_O) c140_result x y ↔ ObsEq (linearSystem c140_A c140_O) x y :=
  replaySource_all_words c140_A c140_O c140_evidence c140_result c140_checked_data x y
theorem c140_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c140_R) c140_R) :
    taggedRealize (linearSystem c140_A c140_O) (guardedCodeFormula c140_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c140_A c140_O) :=
  replaySource_standard_formula c140_A c140_O c140_evidence c140_result c140_checked_data e
abbrev c141_R := ZMod 2
def c141_A : Fin 1 → Mat c141_R 3 3 := ![![![0, 0, 1], ![1, 1, 1], ![1, 1, 1]]]
def c141_O : Mat c141_R 1 3 := ![![0, 1, 1]]
def c141_evidence : List (Evidence c141_R 3) := [
  .separation (![0, 1, 0]),
  .combination [0]]
def c141_result : List (Test 1 1) := [([], 0)]
theorem c141_checked_data : replaySource c141_A c141_O c141_evidence = some c141_result := by decide +kernel
theorem c141_reference_result :
    finitePrimeDiscover 2 1 3 (fun a => rowRight (c141_A a)) c141_O = some c141_result :=
  replaySource_reference 2 1 3 (by decide +kernel) c141_A c141_O c141_evidence c141_result c141_checked_data
theorem c141_all_words (x y : Fin 3 → c141_R) :
    CodeEqual (linearSystem c141_A c141_O) c141_result x y ↔ ObsEq (linearSystem c141_A c141_O) x y :=
  replaySource_all_words c141_A c141_O c141_evidence c141_result c141_checked_data x y
theorem c141_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c141_R) c141_R) :
    taggedRealize (linearSystem c141_A c141_O) (guardedCodeFormula c141_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c141_A c141_O) :=
  replaySource_standard_formula c141_A c141_O c141_evidence c141_result c141_checked_data e
abbrev c142_R := ZMod 3
def c142_A : Fin 2 → Mat c142_R 3 3 := ![![![1, 1, 0], ![2, 1, 2], ![2, 2, 2]], ![![0, 0, 1], ![2, 1, 1], ![1, 2, 1]]]
def c142_O : Mat c142_R 2 3 := ![![1, 2, 1], ![2, 0, 2]]
def c142_evidence : List (Evidence c142_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![1, 1, 0]),
  .separation (![2, 0, 1]),
  .combination [1, 0, 1],
  .combination [1, 0, 2],
  .combination [1, 0, 1],
  .combination [2, 1, 1],
  .combination [0, 0, 1]]
def c142_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c142_checked_data : replaySource c142_A c142_O c142_evidence = some c142_result := by decide +kernel
theorem c142_reference_result :
    finitePrimeDiscover 3 1 3 (fun a => rowRight (c142_A a)) c142_O = some c142_result :=
  replaySource_reference 3 1 3 (by decide +kernel) c142_A c142_O c142_evidence c142_result c142_checked_data
theorem c142_all_words (x y : Fin 3 → c142_R) :
    CodeEqual (linearSystem c142_A c142_O) c142_result x y ↔ ObsEq (linearSystem c142_A c142_O) x y :=
  replaySource_all_words c142_A c142_O c142_evidence c142_result c142_checked_data x y
theorem c142_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c142_R) c142_R) :
    taggedRealize (linearSystem c142_A c142_O) (guardedCodeFormula c142_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c142_A c142_O) :=
  replaySource_standard_formula c142_A c142_O c142_evidence c142_result c142_checked_data e
abbrev c143_R := ZMod 5
def c143_A : Fin 3 → Mat c143_R 3 3 := ![![![3, 0, 3], ![0, 1, 4], ![3, 3, 4]], ![![0, 0, 4], ![4, 4, 2], ![0, 4, 4]], ![![2, 1, 4], ![0, 1, 1], ![0, 3, 0]]]
def c143_O : Mat c143_R 1 3 := ![![2, 4, 1]]
def c143_evidence : List (Evidence c143_R 3) := [
  .separation (![1, 0, 0]),
  .separation (![3, 1, 0]),
  .separation (![4, 4, 1]),
  .combination [0, 2, 1],
  .combination [1, 3, 1],
  .combination [2, 2, 1],
  .combination [4, 4, 4],
  .combination [2, 1, 0],
  .combination [1, 3, 1],
  .combination [4, 0, 4]]
def c143_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c143_checked_data : replaySource c143_A c143_O c143_evidence = some c143_result := by decide +kernel
theorem c143_reference_result :
    finitePrimeDiscover 5 1 3 (fun a => rowRight (c143_A a)) c143_O = some c143_result :=
  replaySource_reference 5 1 3 (by decide +kernel) c143_A c143_O c143_evidence c143_result c143_checked_data
theorem c143_all_words (x y : Fin 3 → c143_R) :
    CodeEqual (linearSystem c143_A c143_O) c143_result x y ↔ ObsEq (linearSystem c143_A c143_O) x y :=
  replaySource_all_words c143_A c143_O c143_evidence c143_result c143_checked_data x y
theorem c143_standard_definition (e : Fin 2 → TaggedCarrier (Fin 3 → c143_R) c143_R) :
    taggedRealize (linearSystem c143_A c143_O) (guardedCodeFormula c143_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c143_A c143_O) :=
  replaySource_standard_formula c143_A c143_O c143_evidence c143_result c143_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch11
