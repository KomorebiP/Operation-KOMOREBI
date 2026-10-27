module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch13
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c156_R := ZMod 2
def c156_A : Fin 1 → Mat c156_R 4 4 := ![![![0, 1, 1, 0], ![1, 0, 1, 1], ![0, 1, 1, 1], ![1, 0, 1, 0]]]
def c156_O : Mat c156_R 2 4 := ![![1, 1, 1, 1], ![0, 1, 0, 1]]
def c156_evidence : List (Evidence c156_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![1, 1, 0, 0]),
  .combination [0, 0],
  .separation (![0, 1, 0, 1]),
  .combination [1, 1, 0]]
def c156_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 1)]
theorem c156_checked_data : replaySource c156_A c156_O c156_evidence = some c156_result := by decide +kernel
theorem c156_reference_result :
    finitePrimeDiscover 2 1 4 (fun a => rowRight (c156_A a)) c156_O = some c156_result :=
  replaySource_reference 2 1 4 (by decide +kernel) c156_A c156_O c156_evidence c156_result c156_checked_data
theorem c156_all_words (x y : Fin 4 → c156_R) :
    CodeEqual (linearSystem c156_A c156_O) c156_result x y ↔ ObsEq (linearSystem c156_A c156_O) x y :=
  replaySource_all_words c156_A c156_O c156_evidence c156_result c156_checked_data x y
theorem c156_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c156_R) c156_R) :
    taggedRealize (linearSystem c156_A c156_O) (guardedCodeFormula c156_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c156_A c156_O) :=
  replaySource_standard_formula c156_A c156_O c156_evidence c156_result c156_checked_data e
abbrev c157_R := ZMod 3
def c157_A : Fin 2 → Mat c157_R 4 4 := ![![![1, 1, 0, 0], ![1, 0, 2, 0], ![1, 0, 0, 2], ![2, 1, 1, 0]], ![![2, 2, 0, 1], ![1, 0, 0, 1], ![1, 1, 2, 1], ![2, 0, 2, 1]]]
def c157_O : Mat c157_R 1 4 := ![![0, 1, 0, 1]]
def c157_evidence : List (Evidence c157_R 4) := [
  .separation (![0, 1, 0, 0]),
  .separation (![0, 2, 0, 1]),
  .separation (![0, 0, 1, 0]),
  .separation (![1, 0, 0, 0]),
  .combination [0, 0, 2, 1],
  .combination [2, 0, 1, 0],
  .combination [2, 0, 1, 0],
  .combination [1, 0, 0, 0],
  .combination [1, 0, 1, 1]]
def c157_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c157_checked_data : replaySource c157_A c157_O c157_evidence = some c157_result := by decide +kernel
theorem c157_reference_result :
    finitePrimeDiscover 3 1 4 (fun a => rowRight (c157_A a)) c157_O = some c157_result :=
  replaySource_reference 3 1 4 (by decide +kernel) c157_A c157_O c157_evidence c157_result c157_checked_data
theorem c157_all_words (x y : Fin 4 → c157_R) :
    CodeEqual (linearSystem c157_A c157_O) c157_result x y ↔ ObsEq (linearSystem c157_A c157_O) x y :=
  replaySource_all_words c157_A c157_O c157_evidence c157_result c157_checked_data x y
theorem c157_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c157_R) c157_R) :
    taggedRealize (linearSystem c157_A c157_O) (guardedCodeFormula c157_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c157_A c157_O) :=
  replaySource_standard_formula c157_A c157_O c157_evidence c157_result c157_checked_data e
abbrev c158_R := ZMod 5
def c158_A : Fin 3 → Mat c158_R 4 4 := ![![![1, 2, 3, 3], ![3, 0, 4, 4], ![0, 0, 2, 3], ![0, 4, 0, 1]], ![![0, 0, 3, 0], ![3, 4, 1, 3], ![4, 3, 4, 4], ![3, 1, 3, 0]], ![![1, 0, 3, 0], ![4, 2, 1, 2], ![3, 1, 0, 2], ![1, 3, 1, 4]]]
def c158_O : Mat c158_R 2 4 := ![![1, 2, 0, 3], ![0, 0, 0, 0]]
def c158_evidence : List (Evidence c158_R 4) := [
  .separation (![1, 0, 0, 0]),
  .combination [0],
  .separation (![0, 0, 1, 0]),
  .separation (![3, 1, 0, 0]),
  .combination [3, 2, 4],
  .separation (![0, 1, 2, 1]),
  .combination [1, 0, 1, 3],
  .combination [0, 0, 1, 0],
  .combination [3, 0, 3, 0],
  .combination [0, 0, 2, 3],
  .combination [1, 1, 3, 1],
  .combination [0, 0, 4, 1],
  .combination [1, 4, 3, 1],
  .combination [4, 1, 4, 1]]
def c158_result : List (Test 3 2) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c158_checked_data : replaySource c158_A c158_O c158_evidence = some c158_result := by decide +kernel
theorem c158_reference_result :
    finitePrimeDiscover 5 1 4 (fun a => rowRight (c158_A a)) c158_O = some c158_result :=
  replaySource_reference 5 1 4 (by decide +kernel) c158_A c158_O c158_evidence c158_result c158_checked_data
theorem c158_all_words (x y : Fin 4 → c158_R) :
    CodeEqual (linearSystem c158_A c158_O) c158_result x y ↔ ObsEq (linearSystem c158_A c158_O) x y :=
  replaySource_all_words c158_A c158_O c158_evidence c158_result c158_checked_data x y
theorem c158_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c158_R) c158_R) :
    taggedRealize (linearSystem c158_A c158_O) (guardedCodeFormula c158_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c158_A c158_O) :=
  replaySource_standard_formula c158_A c158_O c158_evidence c158_result c158_checked_data e
abbrev c159_R := ZMod 4
def c159_A : Fin 1 → Mat c159_R 4 4 := ![![![1, 0, 0, 1], ![2, 1, 3, 1], ![3, 3, 2, 3], ![3, 3, 0, 2]]]
def c159_O : Mat c159_R 1 4 := ![![3, 0, 1, 3]]
def c159_evidence : List (Evidence c159_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![1, 0, 1, 0]),
  .separation (![0, 1, 0, 0]),
  .separation (![0, 1, 2, 2]),
  .combination [3, 0, 2, 2]]
def c159_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem c159_checked_data : replaySource c159_A c159_O c159_evidence = some c159_result := by decide +kernel
theorem c159_reference_result :
    finitePrimeDiscover 2 2 4 (fun a => rowRight (c159_A a)) c159_O = some c159_result :=
  replaySource_reference 2 2 4 (by decide +kernel) c159_A c159_O c159_evidence c159_result c159_checked_data
theorem c159_all_words (x y : Fin 4 → c159_R) :
    CodeEqual (linearSystem c159_A c159_O) c159_result x y ↔ ObsEq (linearSystem c159_A c159_O) x y :=
  replaySource_all_words c159_A c159_O c159_evidence c159_result c159_checked_data x y
theorem c159_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c159_R) c159_R) :
    taggedRealize (linearSystem c159_A c159_O) (guardedCodeFormula c159_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c159_A c159_O) :=
  replaySource_standard_formula c159_A c159_O c159_evidence c159_result c159_checked_data e
abbrev c160_R := ZMod 9
def c160_A : Fin 2 → Mat c160_R 4 4 := ![![![4, 3, 3, 8], ![5, 2, 0, 6], ![4, 8, 3, 3], ![3, 0, 1, 0]], ![![0, 5, 4, 6], ![3, 3, 7, 5], ![0, 8, 7, 4], ![5, 0, 7, 6]]]
def c160_O : Mat c160_R 2 4 := ![![5, 5, 3, 2], ![3, 8, 2, 6]]
def c160_evidence : List (Evidence c160_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![8, 1, 0, 0]),
  .separation (![7, 5, 1, 0]),
  .separation (![4, 7, 8, 1]),
  .separation (![3, 3, 6, 3]),
  .combination [6, 2, 6, 0, 6],
  .combination [2, 6, 5, 0, 6],
  .combination [4, 3, 2, 0, 3],
  .combination [0, 3, 5, 0, 3],
  .combination [4, 0, 0, 0, 0],
  .combination [5, 7, 8, 0, 4],
  .combination [6, 3, 4, 0, 7]]
def c160_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem c160_checked_data : replaySource c160_A c160_O c160_evidence = some c160_result := by decide +kernel
theorem c160_reference_result :
    finitePrimeDiscover 3 2 4 (fun a => rowRight (c160_A a)) c160_O = some c160_result :=
  replaySource_reference 3 2 4 (by decide +kernel) c160_A c160_O c160_evidence c160_result c160_checked_data
theorem c160_all_words (x y : Fin 4 → c160_R) :
    CodeEqual (linearSystem c160_A c160_O) c160_result x y ↔ ObsEq (linearSystem c160_A c160_O) x y :=
  replaySource_all_words c160_A c160_O c160_evidence c160_result c160_checked_data x y
theorem c160_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c160_R) c160_R) :
    taggedRealize (linearSystem c160_A c160_O) (guardedCodeFormula c160_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c160_A c160_O) :=
  replaySource_standard_formula c160_A c160_O c160_evidence c160_result c160_checked_data e
abbrev c161_R := ZMod 25
def c161_A : Fin 3 → Mat c161_R 4 4 := ![![![2, 17, 14, 23], ![24, 22, 13, 7], ![21, 1, 9, 10], ![10, 13, 19, 21]], ![![8, 8, 0, 21], ![17, 7, 10, 12], ![21, 19, 8, 22], ![19, 10, 4, 24]], ![![11, 20, 8, 1], ![2, 11, 19, 0], ![10, 13, 21, 22], ![2, 3, 6, 23]]]
def c161_O : Mat c161_R 1 4 := ![![20, 0, 5, 5]]
def c161_evidence : List (Evidence c161_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 1, 0, 0]),
  .separation (![21, 24, 0, 1]),
  .separation (![21, 21, 1, 0]),
  .combination [0, 23, 4, 0],
  .combination [19, 4, 16, 3],
  .combination [13, 19, 11, 4],
  .combination [24, 17, 17, 2],
  .combination [0, 15, 19, 2],
  .combination [7, 4, 16, 3],
  .combination [1, 4, 13, 4],
  .combination [13, 6, 10, 4],
  .combination [13, 13, 23, 1]]
def c161_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c161_checked_data : replaySource c161_A c161_O c161_evidence = some c161_result := by decide +kernel
theorem c161_reference_result :
    finitePrimeDiscover 5 2 4 (fun a => rowRight (c161_A a)) c161_O = some c161_result :=
  replaySource_reference 5 2 4 (by decide +kernel) c161_A c161_O c161_evidence c161_result c161_checked_data
theorem c161_all_words (x y : Fin 4 → c161_R) :
    CodeEqual (linearSystem c161_A c161_O) c161_result x y ↔ ObsEq (linearSystem c161_A c161_O) x y :=
  replaySource_all_words c161_A c161_O c161_evidence c161_result c161_checked_data x y
theorem c161_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c161_R) c161_R) :
    taggedRealize (linearSystem c161_A c161_O) (guardedCodeFormula c161_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c161_A c161_O) :=
  replaySource_standard_formula c161_A c161_O c161_evidence c161_result c161_checked_data e
abbrev c162_R := ZMod 8
def c162_A : Fin 1 → Mat c162_R 4 4 := ![![![7, 1, 1, 6], ![5, 3, 0, 6], ![2, 5, 1, 1], ![4, 6, 0, 0]]]
def c162_O : Mat c162_R 2 4 := ![![5, 7, 0, 7], ![1, 1, 4, 0]]
def c162_evidence : List (Evidence c162_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![5, 1, 0, 0]),
  .separation (![4, 0, 1, 4]),
  .separation (![7, 1, 6, 2]),
  .separation (![4, 4, 0, 0]),
  .combination [4, 2, 2, 0, 1],
  .combination [2, 7, 2, 0, 3]]
def c162_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem c162_checked_data : replaySource c162_A c162_O c162_evidence = some c162_result := by decide +kernel
theorem c162_reference_result :
    finitePrimeDiscover 2 3 4 (fun a => rowRight (c162_A a)) c162_O = some c162_result :=
  replaySource_reference 2 3 4 (by decide +kernel) c162_A c162_O c162_evidence c162_result c162_checked_data
theorem c162_all_words (x y : Fin 4 → c162_R) :
    CodeEqual (linearSystem c162_A c162_O) c162_result x y ↔ ObsEq (linearSystem c162_A c162_O) x y :=
  replaySource_all_words c162_A c162_O c162_evidence c162_result c162_checked_data x y
theorem c162_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c162_R) c162_R) :
    taggedRealize (linearSystem c162_A c162_O) (guardedCodeFormula c162_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c162_A c162_O) :=
  replaySource_standard_formula c162_A c162_O c162_evidence c162_result c162_checked_data e
abbrev c163_R := ZMod 27
def c163_A : Fin 2 → Mat c163_R 4 4 := ![![![23, 9, 26, 7], ![18, 0, 3, 2], ![15, 11, 16, 25], ![13, 8, 23, 20]], ![![25, 15, 0, 20], ![0, 23, 25, 16], ![7, 20, 18, 0], ![14, 22, 6, 13]]]
def c163_O : Mat c163_R 1 4 := ![![19, 23, 4, 1]]
def c163_evidence : List (Evidence c163_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![13, 1, 0, 0]),
  .separation (![18, 19, 1, 0]),
  .separation (![0, 9, 9, 0]),
  .separation (![9, 24, 21, 3]),
  .combination [0, 19, 0, 11, 6],
  .combination [1, 11, 0, 21, 5],
  .combination [18, 11, 0, 18, 13],
  .combination [19, 16, 0, 7, 2],
  .combination [6, 7, 0, 9, 14],
  .combination [11, 26, 0, 16, 2]]
def c163_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem c163_checked_data : replaySource c163_A c163_O c163_evidence = some c163_result := by decide +kernel
theorem c163_reference_result :
    finitePrimeDiscover 3 3 4 (fun a => rowRight (c163_A a)) c163_O = some c163_result :=
  replaySource_reference 3 3 4 (by decide +kernel) c163_A c163_O c163_evidence c163_result c163_checked_data
theorem c163_all_words (x y : Fin 4 → c163_R) :
    CodeEqual (linearSystem c163_A c163_O) c163_result x y ↔ ObsEq (linearSystem c163_A c163_O) x y :=
  replaySource_all_words c163_A c163_O c163_evidence c163_result c163_checked_data x y
theorem c163_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c163_R) c163_R) :
    taggedRealize (linearSystem c163_A c163_O) (guardedCodeFormula c163_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c163_A c163_O) :=
  replaySource_standard_formula c163_A c163_O c163_evidence c163_result c163_checked_data e
abbrev c164_R := ZMod 125
def c164_A : Fin 3 → Mat c164_R 4 4 := ![![![104, 15, 50, 10], ![108, 2, 122, 119], ![81, 63, 119, 1], ![113, 38, 57, 94]], ![![48, 13, 120, 73], ![115, 93, 26, 118], ![81, 55, 42, 53], ![22, 46, 85, 35]], ![![12, 83, 51, 50], ![10, 28, 115, 78], ![1, 16, 51, 59], ![66, 21, 99, 117]]]
def c164_O : Mat c164_R 2 4 := ![![0, 0, 0, 0], ![0, 0, 0, 0]]
def c164_evidence : List (Evidence c164_R 4) := [
  .combination [],
  .combination []]
def c164_result : List (Test 3 2) := []
theorem c164_checked_data : replaySource c164_A c164_O c164_evidence = some c164_result := by decide +kernel
theorem c164_reference_result :
    finitePrimeDiscover 5 3 4 (fun a => rowRight (c164_A a)) c164_O = some c164_result :=
  replaySource_reference 5 3 4 (by decide +kernel) c164_A c164_O c164_evidence c164_result c164_checked_data
theorem c164_all_words (x y : Fin 4 → c164_R) :
    CodeEqual (linearSystem c164_A c164_O) c164_result x y ↔ ObsEq (linearSystem c164_A c164_O) x y :=
  replaySource_all_words c164_A c164_O c164_evidence c164_result c164_checked_data x y
theorem c164_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c164_R) c164_R) :
    taggedRealize (linearSystem c164_A c164_O) (guardedCodeFormula c164_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c164_A c164_O) :=
  replaySource_standard_formula c164_A c164_O c164_evidence c164_result c164_checked_data e
abbrev c165_R := ZMod 16
def c165_A : Fin 1 → Mat c165_R 4 4 := ![![![3, 15, 3, 12], ![7, 1, 15, 6], ![15, 15, 4, 10], ![4, 11, 14, 11]]]
def c165_O : Mat c165_R 1 4 := ![![4, 12, 13, 5]]
def c165_evidence : List (Evidence c165_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 1, 4, 0]),
  .separation (![10, 1, 12, 0]),
  .separation (![12, 1, 6, 14]),
  .combination [12, 10, 10, 3]]
def c165_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem c165_checked_data : replaySource c165_A c165_O c165_evidence = some c165_result := by decide +kernel
theorem c165_reference_result :
    finitePrimeDiscover 2 4 4 (fun a => rowRight (c165_A a)) c165_O = some c165_result :=
  replaySource_reference 2 4 4 (by decide +kernel) c165_A c165_O c165_evidence c165_result c165_checked_data
theorem c165_all_words (x y : Fin 4 → c165_R) :
    CodeEqual (linearSystem c165_A c165_O) c165_result x y ↔ ObsEq (linearSystem c165_A c165_O) x y :=
  replaySource_all_words c165_A c165_O c165_evidence c165_result c165_checked_data x y
theorem c165_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c165_R) c165_R) :
    taggedRealize (linearSystem c165_A c165_O) (guardedCodeFormula c165_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c165_A c165_O) :=
  replaySource_standard_formula c165_A c165_O c165_evidence c165_result c165_checked_data e
abbrev c166_R := ZMod 81
def c166_A : Fin 2 → Mat c166_R 4 4 := ![![![53, 14, 32, 38], ![30, 53, 41, 14], ![50, 37, 3, 10], ![28, 72, 25, 62]], ![![14, 34, 71, 31], ![29, 65, 63, 80], ![22, 73, 73, 42], ![47, 28, 46, 10]]]
def c166_O : Mat c166_R 2 4 := ![![60, 61, 8, 68], ![56, 44, 19, 65]]
def c166_evidence : List (Evidence c166_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![1, 3, 0, 0]),
  .separation (![69, 13, 1, 0]),
  .separation (![13, 70, 69, 1]),
  .combination [46, 68, 76, 59],
  .combination [49, 28, 0, 52],
  .separation (![27, 27, 0, 27]),
  .combination [3, 61, 72, 0, 44],
  .combination [5, 37, 76, 0, 26],
  .combination [73, 72, 3, 0, 28],
  .combination [61, 21, 41, 0, 71],
  .combination [62, 72, 70, 0, 50]]
def c166_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0,0], 0)]
theorem c166_checked_data : replaySource c166_A c166_O c166_evidence = some c166_result := by decide +kernel
theorem c166_reference_result :
    finitePrimeDiscover 3 4 4 (fun a => rowRight (c166_A a)) c166_O = some c166_result :=
  replaySource_reference 3 4 4 (by decide +kernel) c166_A c166_O c166_evidence c166_result c166_checked_data
theorem c166_all_words (x y : Fin 4 → c166_R) :
    CodeEqual (linearSystem c166_A c166_O) c166_result x y ↔ ObsEq (linearSystem c166_A c166_O) x y :=
  replaySource_all_words c166_A c166_O c166_evidence c166_result c166_checked_data x y
theorem c166_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c166_R) c166_R) :
    taggedRealize (linearSystem c166_A c166_O) (guardedCodeFormula c166_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c166_A c166_O) :=
  replaySource_standard_formula c166_A c166_O c166_evidence c166_result c166_checked_data e
abbrev c167_R := ZMod 625
def c167_A : Fin 3 → Mat c167_R 4 4 := ![![![228, 259, 128, 311], ![28, 321, 151, 149], ![301, 573, 80, 432], ![245, 608, 616, 353]], ![![411, 190, 566, 104], ![489, 471, 221, 479], ![304, 267, 101, 93], ![50, 353, 375, 486]], ![![526, 452, 527, 315], ![489, 49, 584, 583], ![334, 588, 234, 169], ![49, 539, 422, 325]]]
def c167_O : Mat c167_R 1 4 := ![![457, 324, 495, 238]]
def c167_evidence : List (Evidence c167_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![493, 1, 0, 0]),
  .separation (![518, 1, 410, 0]),
  .separation (![381, 480, 475, 1]),
  .combination [483, 346, 47, 72],
  .combination [143, 374, 137, 123],
  .combination [208, 104, 508, 126],
  .combination [331, 252, 372, 466],
  .combination [283, 401, 610, 444],
  .combination [348, 237, 45, 180],
  .combination [89, 11, 472, 264],
  .combination [239, 350, 208, 485],
  .combination [335, 108, 512, 360]]
def c167_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem c167_checked_data : replaySource c167_A c167_O c167_evidence = some c167_result := by decide +kernel
theorem c167_reference_result :
    finitePrimeDiscover 5 4 4 (fun a => rowRight (c167_A a)) c167_O = some c167_result :=
  replaySource_reference 5 4 4 (by decide +kernel) c167_A c167_O c167_evidence c167_result c167_checked_data
theorem c167_all_words (x y : Fin 4 → c167_R) :
    CodeEqual (linearSystem c167_A c167_O) c167_result x y ↔ ObsEq (linearSystem c167_A c167_O) x y :=
  replaySource_all_words c167_A c167_O c167_evidence c167_result c167_checked_data x y
theorem c167_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c167_R) c167_R) :
    taggedRealize (linearSystem c167_A c167_O) (guardedCodeFormula c167_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c167_A c167_O) :=
  replaySource_standard_formula c167_A c167_O c167_evidence c167_result c167_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch13
