module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch03
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c036_R := ZMod 2
def c036_A : Fin 1 → Mat c036_R 2 2 := ![![![0, 0], ![1, 1]]]
def c036_O : Mat c036_R 2 2 := ![![1, 1], ![1, 0]]
def c036_evidence : List (Evidence c036_R 2) := [
  .separation (![1, 0]),
  .separation (![1, 1]),
  .combination [1, 0],
  .combination [0, 0]]
def c036_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c036_checked_data : replaySource c036_A c036_O c036_evidence = some c036_result := by decide +kernel
theorem c036_reference_result :
    finitePrimeDiscover 2 1 2 (fun a => rowRight (c036_A a)) c036_O = some c036_result :=
  replaySource_reference 2 1 2 (by decide +kernel) c036_A c036_O c036_evidence c036_result c036_checked_data
theorem c036_all_words (x y : Fin 2 → c036_R) :
    CodeEqual (linearSystem c036_A c036_O) c036_result x y ↔ ObsEq (linearSystem c036_A c036_O) x y :=
  replaySource_all_words c036_A c036_O c036_evidence c036_result c036_checked_data x y
theorem c036_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c036_R) c036_R) :
    taggedRealize (linearSystem c036_A c036_O) (guardedCodeFormula c036_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c036_A c036_O) :=
  replaySource_standard_formula c036_A c036_O c036_evidence c036_result c036_checked_data e
abbrev c037_R := ZMod 3
def c037_A : Fin 2 → Mat c037_R 2 2 := ![![![2, 2], ![0, 1]], ![![2, 0], ![0, 0]]]
def c037_O : Mat c037_R 1 2 := ![![1, 2]]
def c037_evidence : List (Evidence c037_R 2) := [
  .separation (![1, 0]),
  .combination [2],
  .separation (![1, 1]),
  .combination [2, 1],
  .combination [0, 2]]
def c037_result : List (Test 2 1) := [([], 0), ([1], 0)]
theorem c037_checked_data : replaySource c037_A c037_O c037_evidence = some c037_result := by decide +kernel
theorem c037_reference_result :
    finitePrimeDiscover 3 1 2 (fun a => rowRight (c037_A a)) c037_O = some c037_result :=
  replaySource_reference 3 1 2 (by decide +kernel) c037_A c037_O c037_evidence c037_result c037_checked_data
theorem c037_all_words (x y : Fin 2 → c037_R) :
    CodeEqual (linearSystem c037_A c037_O) c037_result x y ↔ ObsEq (linearSystem c037_A c037_O) x y :=
  replaySource_all_words c037_A c037_O c037_evidence c037_result c037_checked_data x y
theorem c037_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c037_R) c037_R) :
    taggedRealize (linearSystem c037_A c037_O) (guardedCodeFormula c037_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c037_A c037_O) :=
  replaySource_standard_formula c037_A c037_O c037_evidence c037_result c037_checked_data e
abbrev c038_R := ZMod 5
def c038_A : Fin 3 → Mat c038_R 2 2 := ![![![4, 2], ![0, 3]], ![![1, 2], ![2, 3]], ![![0, 0], ![3, 0]]]
def c038_O : Mat c038_R 2 2 := ![![2, 2], ![2, 4]]
def c038_evidence : List (Evidence c038_R 2) := [
  .separation (![1, 0]),
  .separation (![4, 1]),
  .combination [3, 1],
  .combination [1, 2],
  .combination [1, 2],
  .combination [0, 4],
  .combination [2, 3],
  .combination [2, 4]]
def c038_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c038_checked_data : replaySource c038_A c038_O c038_evidence = some c038_result := by decide +kernel
theorem c038_reference_result :
    finitePrimeDiscover 5 1 2 (fun a => rowRight (c038_A a)) c038_O = some c038_result :=
  replaySource_reference 5 1 2 (by decide +kernel) c038_A c038_O c038_evidence c038_result c038_checked_data
theorem c038_all_words (x y : Fin 2 → c038_R) :
    CodeEqual (linearSystem c038_A c038_O) c038_result x y ↔ ObsEq (linearSystem c038_A c038_O) x y :=
  replaySource_all_words c038_A c038_O c038_evidence c038_result c038_checked_data x y
theorem c038_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c038_R) c038_R) :
    taggedRealize (linearSystem c038_A c038_O) (guardedCodeFormula c038_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c038_A c038_O) :=
  replaySource_standard_formula c038_A c038_O c038_evidence c038_result c038_checked_data e
abbrev c039_R := ZMod 4
def c039_A : Fin 1 → Mat c039_R 2 2 := ![![![0, 0], ![3, 0]]]
def c039_O : Mat c039_R 1 2 := ![![2, 1]]
def c039_evidence : List (Evidence c039_R 2) := [
  .separation (![1, 0]),
  .separation (![1, 2]),
  .combination [0, 0]]
def c039_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c039_checked_data : replaySource c039_A c039_O c039_evidence = some c039_result := by decide +kernel
theorem c039_reference_result :
    finitePrimeDiscover 2 2 2 (fun a => rowRight (c039_A a)) c039_O = some c039_result :=
  replaySource_reference 2 2 2 (by decide +kernel) c039_A c039_O c039_evidence c039_result c039_checked_data
theorem c039_all_words (x y : Fin 2 → c039_R) :
    CodeEqual (linearSystem c039_A c039_O) c039_result x y ↔ ObsEq (linearSystem c039_A c039_O) x y :=
  replaySource_all_words c039_A c039_O c039_evidence c039_result c039_checked_data x y
theorem c039_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c039_R) c039_R) :
    taggedRealize (linearSystem c039_A c039_O) (guardedCodeFormula c039_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c039_A c039_O) :=
  replaySource_standard_formula c039_A c039_O c039_evidence c039_result c039_checked_data e
abbrev c040_R := ZMod 9
def c040_A : Fin 2 → Mat c040_R 2 2 := ![![![8, 0], ![6, 2]], ![![7, 3], ![5, 5]]]
def c040_O : Mat c040_R 2 2 := ![![6, 1], ![5, 5]]
def c040_evidence : List (Evidence c040_R 2) := [
  .separation (![1, 0]),
  .separation (![1, 3]),
  .combination [5, 3],
  .combination [3, 4],
  .combination [3, 5],
  .combination [4, 0]]
def c040_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c040_checked_data : replaySource c040_A c040_O c040_evidence = some c040_result := by decide +kernel
theorem c040_reference_result :
    finitePrimeDiscover 3 2 2 (fun a => rowRight (c040_A a)) c040_O = some c040_result :=
  replaySource_reference 3 2 2 (by decide +kernel) c040_A c040_O c040_evidence c040_result c040_checked_data
theorem c040_all_words (x y : Fin 2 → c040_R) :
    CodeEqual (linearSystem c040_A c040_O) c040_result x y ↔ ObsEq (linearSystem c040_A c040_O) x y :=
  replaySource_all_words c040_A c040_O c040_evidence c040_result c040_checked_data x y
theorem c040_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c040_R) c040_R) :
    taggedRealize (linearSystem c040_A c040_O) (guardedCodeFormula c040_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c040_A c040_O) :=
  replaySource_standard_formula c040_A c040_O c040_evidence c040_result c040_checked_data e
abbrev c041_R := ZMod 25
def c041_A : Fin 3 → Mat c041_R 2 2 := ![![![21, 3], ![13, 1]], ![![21, 22], ![11, 16]], ![![18, 4], ![17, 19]]]
def c041_O : Mat c041_R 1 2 := ![![8, 1]]
def c041_evidence : List (Evidence c041_R 2) := [
  .separation (![1, 0]),
  .separation (![3, 1]),
  .combination [17, 3],
  .combination [1, 13],
  .combination [18, 22],
  .combination [7, 20],
  .combination [24, 11]]
def c041_result : List (Test 3 1) := [([], 0), ([0], 0)]
theorem c041_checked_data : replaySource c041_A c041_O c041_evidence = some c041_result := by decide +kernel
theorem c041_reference_result :
    finitePrimeDiscover 5 2 2 (fun a => rowRight (c041_A a)) c041_O = some c041_result :=
  replaySource_reference 5 2 2 (by decide +kernel) c041_A c041_O c041_evidence c041_result c041_checked_data
theorem c041_all_words (x y : Fin 2 → c041_R) :
    CodeEqual (linearSystem c041_A c041_O) c041_result x y ↔ ObsEq (linearSystem c041_A c041_O) x y :=
  replaySource_all_words c041_A c041_O c041_evidence c041_result c041_checked_data x y
theorem c041_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c041_R) c041_R) :
    taggedRealize (linearSystem c041_A c041_O) (guardedCodeFormula c041_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c041_A c041_O) :=
  replaySource_standard_formula c041_A c041_O c041_evidence c041_result c041_checked_data e
abbrev c042_R := ZMod 8
def c042_A : Fin 1 → Mat c042_R 2 2 := ![![![7, 4], ![5, 2]]]
def c042_O : Mat c042_R 2 2 := ![![0, 4], ![4, 0]]
def c042_evidence : List (Evidence c042_R 2) := [
  .separation (![0, 1]),
  .separation (![1, 0]),
  .combination [0, 1],
  .combination [0, 1]]
def c042_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c042_checked_data : replaySource c042_A c042_O c042_evidence = some c042_result := by decide +kernel
theorem c042_reference_result :
    finitePrimeDiscover 2 3 2 (fun a => rowRight (c042_A a)) c042_O = some c042_result :=
  replaySource_reference 2 3 2 (by decide +kernel) c042_A c042_O c042_evidence c042_result c042_checked_data
theorem c042_all_words (x y : Fin 2 → c042_R) :
    CodeEqual (linearSystem c042_A c042_O) c042_result x y ↔ ObsEq (linearSystem c042_A c042_O) x y :=
  replaySource_all_words c042_A c042_O c042_evidence c042_result c042_checked_data x y
theorem c042_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c042_R) c042_R) :
    taggedRealize (linearSystem c042_A c042_O) (guardedCodeFormula c042_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c042_A c042_O) :=
  replaySource_standard_formula c042_A c042_O c042_evidence c042_result c042_checked_data e
abbrev c043_R := ZMod 27
def c043_A : Fin 2 → Mat c043_R 2 2 := ![![![6, 1], ![8, 26]], ![![1, 11], ![8, 0]]]
def c043_O : Mat c043_R 1 2 := ![![14, 8]]
def c043_evidence : List (Evidence c043_R 2) := [
  .separation (![1, 0]),
  .separation (![11, 1]),
  .combination [20, 26],
  .combination [14, 5],
  .combination [22, 8]]
def c043_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c043_checked_data : replaySource c043_A c043_O c043_evidence = some c043_result := by decide +kernel
theorem c043_reference_result :
    finitePrimeDiscover 3 3 2 (fun a => rowRight (c043_A a)) c043_O = some c043_result :=
  replaySource_reference 3 3 2 (by decide +kernel) c043_A c043_O c043_evidence c043_result c043_checked_data
theorem c043_all_words (x y : Fin 2 → c043_R) :
    CodeEqual (linearSystem c043_A c043_O) c043_result x y ↔ ObsEq (linearSystem c043_A c043_O) x y :=
  replaySource_all_words c043_A c043_O c043_evidence c043_result c043_checked_data x y
theorem c043_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c043_R) c043_R) :
    taggedRealize (linearSystem c043_A c043_O) (guardedCodeFormula c043_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c043_A c043_O) :=
  replaySource_standard_formula c043_A c043_O c043_evidence c043_result c043_checked_data e
abbrev c044_R := ZMod 125
def c044_A : Fin 3 → Mat c044_R 2 2 := ![![![27, 1], ![74, 15]], ![![67, 57], ![34, 72]], ![![25, 49], ![41, 54]]]
def c044_O : Mat c044_R 2 2 := ![![114, 44], ![56, 15]]
def c044_evidence : List (Evidence c044_R 2) := [
  .separation (![1, 0]),
  .separation (![4, 1]),
  .combination [21, 115],
  .combination [9, 118],
  .combination [78, 27],
  .combination [39, 21],
  .combination [13, 5],
  .combination [106, 1]]
def c044_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c044_checked_data : replaySource c044_A c044_O c044_evidence = some c044_result := by decide +kernel
theorem c044_reference_result :
    finitePrimeDiscover 5 3 2 (fun a => rowRight (c044_A a)) c044_O = some c044_result :=
  replaySource_reference 5 3 2 (by decide +kernel) c044_A c044_O c044_evidence c044_result c044_checked_data
theorem c044_all_words (x y : Fin 2 → c044_R) :
    CodeEqual (linearSystem c044_A c044_O) c044_result x y ↔ ObsEq (linearSystem c044_A c044_O) x y :=
  replaySource_all_words c044_A c044_O c044_evidence c044_result c044_checked_data x y
theorem c044_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c044_R) c044_R) :
    taggedRealize (linearSystem c044_A c044_O) (guardedCodeFormula c044_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c044_A c044_O) :=
  replaySource_standard_formula c044_A c044_O c044_evidence c044_result c044_checked_data e
abbrev c045_R := ZMod 16
def c045_A : Fin 1 → Mat c045_R 2 2 := ![![![2, 4], ![8, 4]]]
def c045_O : Mat c045_R 1 2 := ![![6, 11]]
def c045_evidence : List (Evidence c045_R 2) := [
  .separation (![1, 0]),
  .separation (![1, 14]),
  .combination [8, 6]]
def c045_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c045_checked_data : replaySource c045_A c045_O c045_evidence = some c045_result := by decide +kernel
theorem c045_reference_result :
    finitePrimeDiscover 2 4 2 (fun a => rowRight (c045_A a)) c045_O = some c045_result :=
  replaySource_reference 2 4 2 (by decide +kernel) c045_A c045_O c045_evidence c045_result c045_checked_data
theorem c045_all_words (x y : Fin 2 → c045_R) :
    CodeEqual (linearSystem c045_A c045_O) c045_result x y ↔ ObsEq (linearSystem c045_A c045_O) x y :=
  replaySource_all_words c045_A c045_O c045_evidence c045_result c045_checked_data x y
theorem c045_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c045_R) c045_R) :
    taggedRealize (linearSystem c045_A c045_O) (guardedCodeFormula c045_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c045_A c045_O) :=
  replaySource_standard_formula c045_A c045_O c045_evidence c045_result c045_checked_data e
abbrev c046_R := ZMod 81
def c046_A : Fin 2 → Mat c046_R 2 2 := ![![![51, 16], ![32, 34]], ![![41, 76], ![31, 9]]]
def c046_O : Mat c046_R 2 2 := ![![33, 46], ![31, 40]]
def c046_evidence : List (Evidence c046_R 2) := [
  .separation (![1, 0]),
  .separation (![1, 75]),
  .combination [2, 50],
  .combination [29, 64],
  .combination [21, 2],
  .combination [76, 21]]
def c046_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c046_checked_data : replaySource c046_A c046_O c046_evidence = some c046_result := by decide +kernel
theorem c046_reference_result :
    finitePrimeDiscover 3 4 2 (fun a => rowRight (c046_A a)) c046_O = some c046_result :=
  replaySource_reference 3 4 2 (by decide +kernel) c046_A c046_O c046_evidence c046_result c046_checked_data
theorem c046_all_words (x y : Fin 2 → c046_R) :
    CodeEqual (linearSystem c046_A c046_O) c046_result x y ↔ ObsEq (linearSystem c046_A c046_O) x y :=
  replaySource_all_words c046_A c046_O c046_evidence c046_result c046_checked_data x y
theorem c046_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c046_R) c046_R) :
    taggedRealize (linearSystem c046_A c046_O) (guardedCodeFormula c046_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c046_A c046_O) :=
  replaySource_standard_formula c046_A c046_O c046_evidence c046_result c046_checked_data e
abbrev c047_R := ZMod 625
def c047_A : Fin 3 → Mat c047_R 2 2 := ![![![200, 67], ![241, 486]], ![![100, 72], ![366, 595]], ![![613, 261], ![168, 390]]]
def c047_O : Mat c047_R 1 2 := ![![0, 0]]
def c047_evidence : List (Evidence c047_R 2) := [
  .combination []]
def c047_result : List (Test 3 1) := []
theorem c047_checked_data : replaySource c047_A c047_O c047_evidence = some c047_result := by decide +kernel
theorem c047_reference_result :
    finitePrimeDiscover 5 4 2 (fun a => rowRight (c047_A a)) c047_O = some c047_result :=
  replaySource_reference 5 4 2 (by decide +kernel) c047_A c047_O c047_evidence c047_result c047_checked_data
theorem c047_all_words (x y : Fin 2 → c047_R) :
    CodeEqual (linearSystem c047_A c047_O) c047_result x y ↔ ObsEq (linearSystem c047_A c047_O) x y :=
  replaySource_all_words c047_A c047_O c047_evidence c047_result c047_checked_data x y
theorem c047_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c047_R) c047_R) :
    taggedRealize (linearSystem c047_A c047_O) (guardedCodeFormula c047_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c047_A c047_O) :=
  replaySource_standard_formula c047_A c047_O c047_evidence c047_result c047_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch03
