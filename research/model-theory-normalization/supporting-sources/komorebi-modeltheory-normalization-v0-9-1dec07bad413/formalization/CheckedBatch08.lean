module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch08
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c096_R := ZMod 2
def c096_A : Fin 1 → Mat c096_R 6 6 := ![![![1, 1, 0, 1, 1, 0], ![0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 1, 1], ![0, 1, 0, 1, 1, 1], ![1, 0, 0, 1, 1, 0], ![1, 1, 0, 0, 1, 0]]]
def c096_O : Mat c096_R 2 6 := ![![0, 0, 0, 1, 0, 0], ![0, 0, 1, 0, 0, 1]]
def c096_evidence : List (Evidence c096_R 6) := [
  .separation (![0, 0, 0, 1, 0, 0]),
  .separation (![0, 0, 1, 0, 0, 0]),
  .separation (![0, 1, 0, 0, 0, 0]),
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![0, 1, 1, 0, 0, 1]),
  .separation (![1, 1, 0, 0, 1, 0]),
  .combination [1, 0, 0, 1, 1, 1],
  .combination [0, 0, 0, 1, 0, 0]]
def c096_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem c096_checked_data : replaySource c096_A c096_O c096_evidence = some c096_result := by decide +kernel
theorem c096_reference_result :
    finitePrimeDiscover 2 1 6 (fun a => rowRight (c096_A a)) c096_O = some c096_result :=
  replaySource_reference 2 1 6 (by decide +kernel) c096_A c096_O c096_evidence c096_result c096_checked_data
theorem c096_all_words (x y : Fin 6 → c096_R) :
    CodeEqual (linearSystem c096_A c096_O) c096_result x y ↔ ObsEq (linearSystem c096_A c096_O) x y :=
  replaySource_all_words c096_A c096_O c096_evidence c096_result c096_checked_data x y
theorem c096_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c096_R) c096_R) :
    taggedRealize (linearSystem c096_A c096_O) (guardedCodeFormula c096_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c096_A c096_O) :=
  replaySource_standard_formula c096_A c096_O c096_evidence c096_result c096_checked_data e
abbrev c097_R := ZMod 3
def c097_A : Fin 2 → Mat c097_R 6 6 := ![![![1, 2, 0, 2, 1, 2], ![0, 0, 1, 2, 2, 0], ![2, 1, 2, 0, 0, 1], ![1, 2, 1, 0, 1, 1], ![2, 2, 0, 0, 2, 2], ![1, 1, 1, 2, 1, 2]], ![![1, 0, 2, 0, 2, 1], ![0, 1, 0, 1, 1, 2], ![2, 1, 2, 1, 2, 1], ![1, 1, 0, 1, 2, 0], ![0, 0, 0, 0, 1, 0], ![2, 1, 1, 2, 0, 0]]]
def c097_O : Mat c097_R 1 6 := ![![1, 2, 0, 1, 1, 0]]
def c097_evidence : List (Evidence c097_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0, 0]),
  .separation (![0, 0, 1, 0, 0, 0]),
  .separation (![0, 1, 0, 1, 0, 0]),
  .separation (![1, 2, 0, 0, 1, 0]),
  .separation (![1, 1, 1, 0, 0, 1]),
  .combination [2, 1, 0, 2, 0, 2],
  .combination [2, 2, 2, 0, 0, 0],
  .combination [2, 2, 0, 1, 2, 1],
  .combination [1, 1, 1, 1, 2, 2],
  .combination [0, 2, 2, 1, 1, 1],
  .combination [1, 0, 0, 2, 2, 2],
  .combination [0, 2, 2, 0, 1, 1]]
def c097_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c097_checked_data : replaySource c097_A c097_O c097_evidence = some c097_result := by decide +kernel
theorem c097_reference_result :
    finitePrimeDiscover 3 1 6 (fun a => rowRight (c097_A a)) c097_O = some c097_result :=
  replaySource_reference 3 1 6 (by decide +kernel) c097_A c097_O c097_evidence c097_result c097_checked_data
theorem c097_all_words (x y : Fin 6 → c097_R) :
    CodeEqual (linearSystem c097_A c097_O) c097_result x y ↔ ObsEq (linearSystem c097_A c097_O) x y :=
  replaySource_all_words c097_A c097_O c097_evidence c097_result c097_checked_data x y
theorem c097_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c097_R) c097_R) :
    taggedRealize (linearSystem c097_A c097_O) (guardedCodeFormula c097_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c097_A c097_O) :=
  replaySource_standard_formula c097_A c097_O c097_evidence c097_result c097_checked_data e
abbrev c098_R := ZMod 5
def c098_A : Fin 3 → Mat c098_R 6 6 := ![![![4, 1, 4, 4, 3, 3], ![4, 2, 0, 1, 3, 0], ![0, 0, 4, 4, 1, 1], ![1, 0, 4, 2, 1, 4], ![3, 2, 2, 0, 2, 0], ![0, 3, 3, 2, 3, 3]], ![![3, 2, 1, 3, 1, 2], ![0, 4, 4, 2, 0, 2], ![0, 3, 2, 2, 4, 4], ![3, 1, 3, 0, 3, 3], ![1, 4, 1, 2, 4, 4], ![4, 4, 2, 0, 4, 2]], ![![1, 2, 2, 0, 2, 0], ![3, 3, 4, 4, 2, 2], ![3, 4, 2, 1, 1, 3], ![4, 1, 2, 1, 0, 0], ![1, 3, 4, 3, 2, 0], ![0, 3, 3, 1, 0, 0]]]
def c098_O : Mat c098_R 2 6 := ![![0, 3, 1, 0, 1, 4], ![2, 3, 3, 2, 4, 1]]
def c098_evidence : List (Evidence c098_R 6) := [
  .separation (![0, 1, 0, 0, 0, 0]),
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![4, 3, 1, 0, 0, 0]),
  .separation (![4, 0, 0, 1, 0, 0]),
  .separation (![0, 4, 2, 4, 1, 0]),
  .separation (![3, 4, 4, 2, 0, 1]),
  .combination [0, 4, 3, 1, 4, 2],
  .combination [0, 1, 0, 3, 2, 2],
  .combination [2, 1, 0, 1, 4, 4],
  .combination [1, 0, 1, 1, 0, 1],
  .combination [0, 4, 1, 2, 2, 0],
  .combination [4, 4, 4, 0, 2, 4],
  .combination [1, 3, 3, 1, 2, 1],
  .combination [4, 4, 3, 1, 2, 1],
  .combination [4, 0, 3, 2, 3, 2],
  .combination [0, 2, 1, 3, 0, 1],
  .combination [4, 4, 1, 4, 0, 0],
  .combination [0, 4, 2, 2, 2, 4],
  .combination [4, 2, 0, 0, 0, 4],
  .combination [0, 4, 3, 3, 4, 1]]
def c098_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c098_checked_data : replaySource c098_A c098_O c098_evidence = some c098_result := by decide +kernel
theorem c098_reference_result :
    finitePrimeDiscover 5 1 6 (fun a => rowRight (c098_A a)) c098_O = some c098_result :=
  replaySource_reference 5 1 6 (by decide +kernel) c098_A c098_O c098_evidence c098_result c098_checked_data
theorem c098_all_words (x y : Fin 6 → c098_R) :
    CodeEqual (linearSystem c098_A c098_O) c098_result x y ↔ ObsEq (linearSystem c098_A c098_O) x y :=
  replaySource_all_words c098_A c098_O c098_evidence c098_result c098_checked_data x y
theorem c098_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c098_R) c098_R) :
    taggedRealize (linearSystem c098_A c098_O) (guardedCodeFormula c098_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c098_A c098_O) :=
  replaySource_standard_formula c098_A c098_O c098_evidence c098_result c098_checked_data e
abbrev c099_R := ZMod 4
def c099_A : Fin 1 → Mat c099_R 6 6 := ![![![0, 2, 3, 2, 0, 2], ![3, 1, 3, 0, 0, 3], ![0, 2, 3, 0, 3, 1], ![3, 2, 2, 1, 2, 3], ![2, 2, 1, 2, 3, 2], ![2, 3, 0, 0, 2, 0]]]
def c099_O : Mat c099_R 1 6 := ![![0, 0, 0, 0, 0, 0]]
def c099_evidence : List (Evidence c099_R 6) := [
  .combination []]
def c099_result : List (Test 1 1) := []
theorem c099_checked_data : replaySource c099_A c099_O c099_evidence = some c099_result := by decide +kernel
theorem c099_reference_result :
    finitePrimeDiscover 2 2 6 (fun a => rowRight (c099_A a)) c099_O = some c099_result :=
  replaySource_reference 2 2 6 (by decide +kernel) c099_A c099_O c099_evidence c099_result c099_checked_data
theorem c099_all_words (x y : Fin 6 → c099_R) :
    CodeEqual (linearSystem c099_A c099_O) c099_result x y ↔ ObsEq (linearSystem c099_A c099_O) x y :=
  replaySource_all_words c099_A c099_O c099_evidence c099_result c099_checked_data x y
theorem c099_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c099_R) c099_R) :
    taggedRealize (linearSystem c099_A c099_O) (guardedCodeFormula c099_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c099_A c099_O) :=
  replaySource_standard_formula c099_A c099_O c099_evidence c099_result c099_checked_data e
abbrev c100_R := ZMod 9
def c100_A : Fin 2 → Mat c100_R 6 6 := ![![![7, 6, 7, 5, 4, 4], ![2, 4, 4, 7, 8, 1], ![2, 4, 1, 3, 2, 4], ![5, 5, 4, 4, 2, 6], ![2, 7, 2, 2, 6, 1], ![1, 0, 4, 7, 7, 3]], ![![0, 6, 2, 0, 0, 2], ![0, 3, 7, 8, 1, 3], ![5, 0, 3, 8, 0, 5], ![7, 7, 3, 1, 5, 7], ![4, 6, 7, 4, 1, 4], ![7, 7, 3, 5, 2, 0]]]
def c100_O : Mat c100_R 2 6 := ![![2, 6, 4, 0, 3, 4], ![6, 6, 3, 3, 5, 2]]
def c100_evidence : List (Evidence c100_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![6, 1, 0, 0, 0, 0]),
  .separation (![7, 0, 1, 0, 0, 0]),
  .separation (![7, 0, 1, 3, 0, 0]),
  .separation (![1, 1, 7, 7, 0, 0]),
  .combination [5, 5, 3, 3, 7],
  .separation (![6, 3, 8, 0, 2, 1]),
  .combination [7, 0, 6, 7, 6, 2],
  .combination [3, 7, 5, 8, 7, 0],
  .combination [0, 2, 4, 8, 5, 3],
  .combination [4, 1, 2, 3, 2, 8],
  .combination [4, 5, 5, 8, 3, 2],
  .combination [3, 5, 4, 8, 7, 6],
  .combination [4, 8, 2, 3, 5, 4]]
def c100_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([0,0], 0)]
theorem c100_checked_data : replaySource c100_A c100_O c100_evidence = some c100_result := by decide +kernel
theorem c100_reference_result :
    finitePrimeDiscover 3 2 6 (fun a => rowRight (c100_A a)) c100_O = some c100_result :=
  replaySource_reference 3 2 6 (by decide +kernel) c100_A c100_O c100_evidence c100_result c100_checked_data
theorem c100_all_words (x y : Fin 6 → c100_R) :
    CodeEqual (linearSystem c100_A c100_O) c100_result x y ↔ ObsEq (linearSystem c100_A c100_O) x y :=
  replaySource_all_words c100_A c100_O c100_evidence c100_result c100_checked_data x y
theorem c100_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c100_R) c100_R) :
    taggedRealize (linearSystem c100_A c100_O) (guardedCodeFormula c100_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c100_A c100_O) :=
  replaySource_standard_formula c100_A c100_O c100_evidence c100_result c100_checked_data e
abbrev c101_R := ZMod 25
def c101_A : Fin 3 → Mat c101_R 6 6 := ![![![4, 6, 24, 15, 5, 20], ![1, 21, 10, 18, 8, 14], ![20, 23, 16, 16, 23, 5], ![7, 12, 4, 22, 23, 14], ![10, 12, 0, 8, 24, 1], ![6, 13, 7, 13, 22, 12]], ![![11, 21, 18, 18, 23, 11], ![4, 15, 14, 16, 14, 18], ![0, 16, 2, 7, 10, 17], ![7, 10, 15, 9, 1, 0], ![6, 18, 5, 2, 5, 21], ![19, 24, 2, 18, 2, 21]], ![![8, 2, 11, 10, 17, 24], ![10, 24, 16, 12, 19, 19], ![19, 10, 19, 19, 21, 13], ![14, 9, 19, 10, 15, 0], ![16, 11, 14, 13, 12, 15], ![9, 2, 14, 0, 15, 7]]]
def c101_O : Mat c101_R 1 6 := ![![17, 11, 9, 11, 15, 20]]
def c101_evidence : List (Evidence c101_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![17, 1, 0, 0, 0, 0]),
  .separation (![21, 19, 1, 0, 0, 0]),
  .separation (![16, 24, 1, 5, 0, 0]),
  .separation (![17, 17, 0, 19, 1, 0]),
  .separation (![16, 12, 6, 12, 1, 1]),
  .combination [1, 4, 0, 8, 14, 18],
  .combination [23, 24, 15, 19, 13, 12],
  .combination [10, 2, 6, 6, 11, 15],
  .combination [17, 1, 6, 11, 12, 21],
  .combination [0, 22, 17, 15, 6, 23],
  .combination [3, 6, 5, 17, 6, 21],
  .combination [1, 1, 3, 12, 13, 15],
  .combination [20, 13, 8, 9, 8, 22],
  .combination [9, 17, 24, 17, 8, 20],
  .combination [13, 22, 8, 20, 22, 23],
  .combination [16, 7, 0, 14, 1, 11],
  .combination [22, 18, 6, 6, 13, 7],
  .combination [15, 15, 15, 5, 14, 11]]
def c101_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem c101_checked_data : replaySource c101_A c101_O c101_evidence = some c101_result := by decide +kernel
theorem c101_reference_result :
    finitePrimeDiscover 5 2 6 (fun a => rowRight (c101_A a)) c101_O = some c101_result :=
  replaySource_reference 5 2 6 (by decide +kernel) c101_A c101_O c101_evidence c101_result c101_checked_data
theorem c101_all_words (x y : Fin 6 → c101_R) :
    CodeEqual (linearSystem c101_A c101_O) c101_result x y ↔ ObsEq (linearSystem c101_A c101_O) x y :=
  replaySource_all_words c101_A c101_O c101_evidence c101_result c101_checked_data x y
theorem c101_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c101_R) c101_R) :
    taggedRealize (linearSystem c101_A c101_O) (guardedCodeFormula c101_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c101_A c101_O) :=
  replaySource_standard_formula c101_A c101_O c101_evidence c101_result c101_checked_data e
abbrev c102_R := ZMod 8
def c102_A : Fin 1 → Mat c102_R 6 6 := ![![![4, 0, 3, 4, 6, 4], ![7, 1, 0, 7, 5, 1], ![5, 5, 5, 3, 2, 0], ![4, 6, 6, 7, 1, 7], ![4, 1, 1, 6, 0, 5], ![4, 0, 6, 4, 4, 7]]]
def c102_O : Mat c102_R 2 6 := ![![3, 5, 7, 7, 7, 2], ![4, 3, 0, 0, 2, 1]]
def c102_evidence : List (Evidence c102_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 1, 0, 0, 0, 0]),
  .separation (![7, 4, 1, 0, 0, 0]),
  .separation (![2, 0, 5, 1, 0, 0]),
  .separation (![5, 6, 2, 2, 1, 0]),
  .separation (![7, 0, 2, 6, 1, 2]),
  .combination [6, 7, 5, 7, 2, 4],
  .combination [3, 7, 1, 1, 3, 6]]
def c102_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem c102_checked_data : replaySource c102_A c102_O c102_evidence = some c102_result := by decide +kernel
theorem c102_reference_result :
    finitePrimeDiscover 2 3 6 (fun a => rowRight (c102_A a)) c102_O = some c102_result :=
  replaySource_reference 2 3 6 (by decide +kernel) c102_A c102_O c102_evidence c102_result c102_checked_data
theorem c102_all_words (x y : Fin 6 → c102_R) :
    CodeEqual (linearSystem c102_A c102_O) c102_result x y ↔ ObsEq (linearSystem c102_A c102_O) x y :=
  replaySource_all_words c102_A c102_O c102_evidence c102_result c102_checked_data x y
theorem c102_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c102_R) c102_R) :
    taggedRealize (linearSystem c102_A c102_O) (guardedCodeFormula c102_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c102_A c102_O) :=
  replaySource_standard_formula c102_A c102_O c102_evidence c102_result c102_checked_data e
abbrev c103_R := ZMod 27
def c103_A : Fin 2 → Mat c103_R 6 6 := ![![![20, 9, 23, 5, 1, 2], ![14, 13, 22, 19, 18, 2], ![5, 18, 25, 6, 9, 26], ![5, 13, 15, 2, 22, 8], ![11, 16, 20, 10, 20, 4], ![2, 19, 19, 26, 5, 5]], ![![9, 2, 8, 24, 19, 9], ![1, 23, 5, 26, 0, 15], ![5, 14, 12, 9, 4, 15], ![26, 10, 13, 8, 21, 18], ![17, 16, 11, 2, 12, 0], ![14, 25, 8, 6, 10, 6]]]
def c103_O : Mat c103_R 1 6 := ![![2, 14, 16, 19, 2, 3]]
def c103_evidence : List (Evidence c103_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![20, 1, 0, 0, 0, 0]),
  .separation (![19, 0, 1, 0, 0, 0]),
  .separation (![26, 13, 23, 1, 0, 0]),
  .separation (![2, 26, 15, 2, 1, 0]),
  .separation (![15, 10, 2, 15, 25, 1]),
  .combination [26, 23, 1, 5, 12, 14],
  .combination [17, 22, 23, 17, 20, 18],
  .combination [11, 15, 19, 13, 1, 26],
  .combination [6, 15, 22, 24, 17, 8],
  .combination [5, 26, 5, 16, 5, 18],
  .combination [21, 16, 4, 24, 19, 24],
  .combination [25, 0, 5, 21, 15, 24]]
def c103_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem c103_checked_data : replaySource c103_A c103_O c103_evidence = some c103_result := by decide +kernel
theorem c103_reference_result :
    finitePrimeDiscover 3 3 6 (fun a => rowRight (c103_A a)) c103_O = some c103_result :=
  replaySource_reference 3 3 6 (by decide +kernel) c103_A c103_O c103_evidence c103_result c103_checked_data
theorem c103_all_words (x y : Fin 6 → c103_R) :
    CodeEqual (linearSystem c103_A c103_O) c103_result x y ↔ ObsEq (linearSystem c103_A c103_O) x y :=
  replaySource_all_words c103_A c103_O c103_evidence c103_result c103_checked_data x y
theorem c103_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c103_R) c103_R) :
    taggedRealize (linearSystem c103_A c103_O) (guardedCodeFormula c103_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c103_A c103_O) :=
  replaySource_standard_formula c103_A c103_O c103_evidence c103_result c103_checked_data e
abbrev c104_R := ZMod 125
def c104_A : Fin 3 → Mat c104_R 6 6 := ![![![68, 99, 104, 107, 33, 11], ![97, 106, 110, 103, 17, 96], ![51, 57, 47, 103, 82, 66], ![58, 15, 85, 59, 95, 81], ![3, 67, 122, 121, 98, 120], ![91, 39, 122, 45, 6, 50]], ![![119, 124, 124, 6, 103, 71], ![82, 53, 82, 119, 82, 30], ![27, 56, 41, 104, 13, 68], ![69, 112, 12, 58, 21, 78], ![106, 79, 40, 32, 49, 55], ![17, 78, 96, 104, 68, 96]], ![![61, 117, 70, 90, 4, 119], ![112, 51, 77, 83, 59, 72], ![55, 37, 109, 105, 68, 21], ![26, 24, 80, 9, 79, 55], ![9, 52, 88, 62, 41, 55], ![124, 110, 122, 64, 60, 17]]]
def c104_O : Mat c104_R 2 6 := ![![43, 20, 70, 92, 82, 15], ![6, 1, 112, 77, 90, 28]]
def c104_evidence : List (Evidence c104_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![110, 1, 0, 0, 0, 0]),
  .separation (![40, 23, 1, 0, 0, 0]),
  .separation (![111, 89, 64, 1, 0, 0]),
  .separation (![101, 49, 64, 1, 15, 0]),
  .separation (![91, 17, 7, 80, 26, 1]),
  .combination [99, 42, 72, 20, 88, 4],
  .combination [56, 68, 28, 13, 9, 115],
  .combination [84, 88, 26, 10, 33, 99],
  .combination [85, 9, 61, 114, 115, 94],
  .combination [80, 12, 100, 60, 26, 124],
  .combination [118, 68, 78, 81, 6, 85],
  .combination [67, 19, 105, 12, 10, 123],
  .combination [45, 65, 24, 80, 11, 113],
  .combination [5, 106, 20, 22, 82, 59],
  .combination [3, 43, 121, 15, 101, 98],
  .combination [65, 16, 109, 93, 43, 42],
  .combination [116, 22, 71, 23, 84, 114],
  .combination [6, 52, 7, 27, 31, 75],
  .combination [74, 58, 96, 97, 4, 122]]
def c104_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem c104_checked_data : replaySource c104_A c104_O c104_evidence = some c104_result := by decide +kernel
theorem c104_reference_result :
    finitePrimeDiscover 5 3 6 (fun a => rowRight (c104_A a)) c104_O = some c104_result :=
  replaySource_reference 5 3 6 (by decide +kernel) c104_A c104_O c104_evidence c104_result c104_checked_data
theorem c104_all_words (x y : Fin 6 → c104_R) :
    CodeEqual (linearSystem c104_A c104_O) c104_result x y ↔ ObsEq (linearSystem c104_A c104_O) x y :=
  replaySource_all_words c104_A c104_O c104_evidence c104_result c104_checked_data x y
theorem c104_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c104_R) c104_R) :
    taggedRealize (linearSystem c104_A c104_O) (guardedCodeFormula c104_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c104_A c104_O) :=
  replaySource_standard_formula c104_A c104_O c104_evidence c104_result c104_checked_data e
abbrev c105_R := ZMod 16
def c105_A : Fin 1 → Mat c105_R 6 6 := ![![![9, 9, 11, 2, 0, 9], ![9, 14, 0, 15, 7, 12], ![12, 11, 9, 0, 12, 12], ![8, 10, 3, 6, 15, 9], ![6, 12, 4, 5, 3, 9], ![4, 2, 1, 8, 0, 2]]]
def c105_O : Mat c105_R 1 6 := ![![8, 8, 8, 8, 8, 8]]
def c105_evidence : List (Evidence c105_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![15, 0, 0, 0, 1, 0]),
  .separation (![15, 0, 1, 0, 0, 0]),
  .separation (![15, 1, 0, 0, 0, 0]),
  .separation (![0, 0, 15, 1, 0, 0]),
  .combination [0, 0, 0, 1, 0]]
def c105_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem c105_checked_data : replaySource c105_A c105_O c105_evidence = some c105_result := by decide +kernel
theorem c105_reference_result :
    finitePrimeDiscover 2 4 6 (fun a => rowRight (c105_A a)) c105_O = some c105_result :=
  replaySource_reference 2 4 6 (by decide +kernel) c105_A c105_O c105_evidence c105_result c105_checked_data
theorem c105_all_words (x y : Fin 6 → c105_R) :
    CodeEqual (linearSystem c105_A c105_O) c105_result x y ↔ ObsEq (linearSystem c105_A c105_O) x y :=
  replaySource_all_words c105_A c105_O c105_evidence c105_result c105_checked_data x y
theorem c105_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c105_R) c105_R) :
    taggedRealize (linearSystem c105_A c105_O) (guardedCodeFormula c105_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c105_A c105_O) :=
  replaySource_standard_formula c105_A c105_O c105_evidence c105_result c105_checked_data e
abbrev c106_R := ZMod 81
def c106_A : Fin 2 → Mat c106_R 6 6 := ![![![57, 35, 22, 33, 57, 75], ![0, 10, 70, 69, 35, 58], ![77, 52, 8, 19, 62, 65], ![73, 28, 12, 12, 53, 42], ![27, 54, 39, 54, 65, 45], ![36, 45, 80, 11, 60, 55]], ![![70, 22, 13, 58, 73, 9], ![51, 22, 57, 80, 51, 44], ![16, 48, 28, 5, 30, 13], ![5, 32, 39, 39, 8, 55], ![23, 65, 32, 31, 9, 44], ![68, 1, 73, 37, 18, 19]]]
def c106_O : Mat c106_R 2 6 := ![![15, 22, 30, 60, 51, 51], ![78, 3, 10, 57, 17, 53]]
def c106_evidence : List (Evidence c106_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 3, 0, 0, 0, 0]),
  .separation (![1, 48, 75, 0, 0, 0]),
  .separation (![0, 21, 54, 1, 0, 12]),
  .separation (![0, 36, 70, 75, 1, 78]),
  .separation (![57, 18, 79, 48, 1, 24]),
  .combination [52, 54, 4, 11, 28, 16],
  .combination [58, 42, 78, 72, 14, 54],
  .combination [14, 16, 41, 10, 13, 77],
  .combination [28, 79, 16, 79, 13, 3],
  .combination [41, 38, 73, 60, 37, 74],
  .combination [14, 28, 44, 18, 43, 51],
  .combination [66, 72, 43, 38, 61, 75],
  .combination [76, 0, 72, 15, 78, 68]]
def c106_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem c106_checked_data : replaySource c106_A c106_O c106_evidence = some c106_result := by decide +kernel
theorem c106_reference_result :
    finitePrimeDiscover 3 4 6 (fun a => rowRight (c106_A a)) c106_O = some c106_result :=
  replaySource_reference 3 4 6 (by decide +kernel) c106_A c106_O c106_evidence c106_result c106_checked_data
theorem c106_all_words (x y : Fin 6 → c106_R) :
    CodeEqual (linearSystem c106_A c106_O) c106_result x y ↔ ObsEq (linearSystem c106_A c106_O) x y :=
  replaySource_all_words c106_A c106_O c106_evidence c106_result c106_checked_data x y
theorem c106_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c106_R) c106_R) :
    taggedRealize (linearSystem c106_A c106_O) (guardedCodeFormula c106_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c106_A c106_O) :=
  replaySource_standard_formula c106_A c106_O c106_evidence c106_result c106_checked_data e
abbrev c107_R := ZMod 625
def c107_A : Fin 3 → Mat c107_R 6 6 := ![![![77, 439, 412, 410, 606, 239], ![396, 89, 51, 94, 573, 290], ![340, 167, 288, 569, 315, 448], ![550, 80, 25, 398, 150, 495], ![577, 338, 287, 225, 337, 207], ![441, 308, 184, 119, 141, 111]], ![![348, 157, 144, 109, 325, 590], ![380, 464, 610, 482, 377, 38], ![545, 515, 225, 59, 505, 80], ![614, 560, 497, 438, 127, 19], ![274, 333, 100, 90, 593, 222], ![21, 434, 596, 341, 218, 16]], ![![165, 427, 489, 136, 195, 230], ![115, 173, 394, 535, 150, 342], ![194, 330, 208, 577, 582, 402], ![423, 71, 414, 177, 607, 177], ![433, 135, 182, 55, 287, 595], ![550, 498, 592, 170, 73, 69]]]
def c107_O : Mat c107_R 1 6 := ![![377, 601, 552, 440, 45, 153]]
def c107_evidence : List (Evidence c107_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![262, 1, 0, 0, 0, 0]),
  .separation (![374, 325, 1, 0, 0, 0]),
  .separation (![504, 156, 323, 1, 0, 0]),
  .separation (![226, 176, 146, 154, 1, 0]),
  .separation (![125, 125, 125, 500, 125, 0]),
  .separation (![250, 500, 250, 500, 0, 125]),
  .combination [489, 581, 405, 352, 0, 52, 62],
  .combination [465, 464, 571, 45, 0, 511, 172],
  .combination [606, 172, 371, 278, 0, 460, 43],
  .combination [410, 220, 485, 324, 0, 95, 38],
  .combination [506, 248, 478, 385, 0, 263, 406],
  .combination [538, 216, 519, 341, 0, 307, 194],
  .combination [159, 435, 112, 540, 0, 242, 31],
  .combination [128, 548, 95, 435, 0, 432, 250],
  .combination [375, 35, 318, 226, 0, 456, 132],
  .combination [414, 458, 303, 451, 0, 124, 351],
  .combination [349, 258, 410, 139, 0, 284, 300],
  .combination [567, 482, 189, 554, 0, 138, 57],
  .combination [171, 589, 197, 459, 0, 13, 15],
  .combination [364, 154, 143, 234, 0, 53, 219],
  .combination [453, 291, 69, 575, 0, 595, 229]]
def c107_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0), ([2,0], 0)]
theorem c107_checked_data : replaySource c107_A c107_O c107_evidence = some c107_result := by decide +kernel
theorem c107_reference_result :
    finitePrimeDiscover 5 4 6 (fun a => rowRight (c107_A a)) c107_O = some c107_result :=
  replaySource_reference 5 4 6 (by decide +kernel) c107_A c107_O c107_evidence c107_result c107_checked_data
theorem c107_all_words (x y : Fin 6 → c107_R) :
    CodeEqual (linearSystem c107_A c107_O) c107_result x y ↔ ObsEq (linearSystem c107_A c107_O) x y :=
  replaySource_all_words c107_A c107_O c107_evidence c107_result c107_checked_data x y
theorem c107_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c107_R) c107_R) :
    taggedRealize (linearSystem c107_A c107_O) (guardedCodeFormula c107_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c107_A c107_O) :=
  replaySource_standard_formula c107_A c107_O c107_evidence c107_result c107_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch08
