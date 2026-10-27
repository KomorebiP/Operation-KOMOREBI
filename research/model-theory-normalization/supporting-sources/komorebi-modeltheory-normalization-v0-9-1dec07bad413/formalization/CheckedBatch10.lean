module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch10
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c120_R := ZMod 16
def c120_A : Fin 1 → Mat c120_R 1 1 := ![![![10]]]
def c120_O : Mat c120_R 2 1 := ![![3], ![7]]
def c120_evidence : List (Evidence c120_R 1) := [
  .separation (![1]),
  .combination [13],
  .combination [10]]
def c120_result : List (Test 1 2) := [([], 0)]
theorem c120_checked_data : replaySource c120_A c120_O c120_evidence = some c120_result := by decide +kernel
theorem c120_reference_result :
    finitePrimeDiscover 2 4 1 (fun a => rowRight (c120_A a)) c120_O = some c120_result :=
  replaySource_reference 2 4 1 (by decide +kernel) c120_A c120_O c120_evidence c120_result c120_checked_data
theorem c120_all_words (x y : Fin 1 → c120_R) :
    CodeEqual (linearSystem c120_A c120_O) c120_result x y ↔ ObsEq (linearSystem c120_A c120_O) x y :=
  replaySource_all_words c120_A c120_O c120_evidence c120_result c120_checked_data x y
theorem c120_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c120_R) c120_R) :
    taggedRealize (linearSystem c120_A c120_O) (guardedCodeFormula c120_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c120_A c120_O) :=
  replaySource_standard_formula c120_A c120_O c120_evidence c120_result c120_checked_data e
abbrev c121_R := ZMod 81
def c121_A : Fin 2 → Mat c121_R 1 1 := ![![![61]], ![![12]]]
def c121_O : Mat c121_R 1 1 := ![![71]]
def c121_evidence : List (Evidence c121_R 1) := [
  .separation (![1]),
  .combination [61],
  .combination [12]]
def c121_result : List (Test 2 1) := [([], 0)]
theorem c121_checked_data : replaySource c121_A c121_O c121_evidence = some c121_result := by decide +kernel
theorem c121_reference_result :
    finitePrimeDiscover 3 4 1 (fun a => rowRight (c121_A a)) c121_O = some c121_result :=
  replaySource_reference 3 4 1 (by decide +kernel) c121_A c121_O c121_evidence c121_result c121_checked_data
theorem c121_all_words (x y : Fin 1 → c121_R) :
    CodeEqual (linearSystem c121_A c121_O) c121_result x y ↔ ObsEq (linearSystem c121_A c121_O) x y :=
  replaySource_all_words c121_A c121_O c121_evidence c121_result c121_checked_data x y
theorem c121_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c121_R) c121_R) :
    taggedRealize (linearSystem c121_A c121_O) (guardedCodeFormula c121_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c121_A c121_O) :=
  replaySource_standard_formula c121_A c121_O c121_evidence c121_result c121_checked_data e
abbrev c122_R := ZMod 625
def c122_A : Fin 3 → Mat c122_R 1 1 := ![![![420]], ![![304]], ![![259]]]
def c122_O : Mat c122_R 2 1 := ![![617], ![181]]
def c122_evidence : List (Evidence c122_R 1) := [
  .separation (![1]),
  .combination [368],
  .combination [420],
  .combination [304],
  .combination [259]]
def c122_result : List (Test 3 2) := [([], 0)]
theorem c122_checked_data : replaySource c122_A c122_O c122_evidence = some c122_result := by decide +kernel
theorem c122_reference_result :
    finitePrimeDiscover 5 4 1 (fun a => rowRight (c122_A a)) c122_O = some c122_result :=
  replaySource_reference 5 4 1 (by decide +kernel) c122_A c122_O c122_evidence c122_result c122_checked_data
theorem c122_all_words (x y : Fin 1 → c122_R) :
    CodeEqual (linearSystem c122_A c122_O) c122_result x y ↔ ObsEq (linearSystem c122_A c122_O) x y :=
  replaySource_all_words c122_A c122_O c122_evidence c122_result c122_checked_data x y
theorem c122_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c122_R) c122_R) :
    taggedRealize (linearSystem c122_A c122_O) (guardedCodeFormula c122_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c122_A c122_O) :=
  replaySource_standard_formula c122_A c122_O c122_evidence c122_result c122_checked_data e
abbrev c123_R := ZMod 32
def c123_A : Fin 1 → Mat c123_R 1 1 := ![![![5]]]
def c123_O : Mat c123_R 1 1 := ![![18]]
def c123_evidence : List (Evidence c123_R 1) := [
  .separation (![1]),
  .combination [5]]
def c123_result : List (Test 1 1) := [([], 0)]
theorem c123_checked_data : replaySource c123_A c123_O c123_evidence = some c123_result := by decide +kernel
theorem c123_reference_result :
    finitePrimeDiscover 2 5 1 (fun a => rowRight (c123_A a)) c123_O = some c123_result :=
  replaySource_reference 2 5 1 (by decide +kernel) c123_A c123_O c123_evidence c123_result c123_checked_data
theorem c123_all_words (x y : Fin 1 → c123_R) :
    CodeEqual (linearSystem c123_A c123_O) c123_result x y ↔ ObsEq (linearSystem c123_A c123_O) x y :=
  replaySource_all_words c123_A c123_O c123_evidence c123_result c123_checked_data x y
theorem c123_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c123_R) c123_R) :
    taggedRealize (linearSystem c123_A c123_O) (guardedCodeFormula c123_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c123_A c123_O) :=
  replaySource_standard_formula c123_A c123_O c123_evidence c123_result c123_checked_data e
abbrev c124_R := ZMod 243
def c124_A : Fin 2 → Mat c124_R 1 1 := ![![![97]], ![![142]]]
def c124_O : Mat c124_R 2 1 := ![![171], ![39]]
def c124_evidence : List (Evidence c124_R 1) := [
  .separation (![1]),
  .separation (![27]),
  .combination [0, 39],
  .combination [0, 174],
  .combination [0, 97],
  .combination [0, 61]]
def c124_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c124_checked_data : replaySource c124_A c124_O c124_evidence = some c124_result := by decide +kernel
theorem c124_reference_result :
    finitePrimeDiscover 3 5 1 (fun a => rowRight (c124_A a)) c124_O = some c124_result :=
  replaySource_reference 3 5 1 (by decide +kernel) c124_A c124_O c124_evidence c124_result c124_checked_data
theorem c124_all_words (x y : Fin 1 → c124_R) :
    CodeEqual (linearSystem c124_A c124_O) c124_result x y ↔ ObsEq (linearSystem c124_A c124_O) x y :=
  replaySource_all_words c124_A c124_O c124_evidence c124_result c124_checked_data x y
theorem c124_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c124_R) c124_R) :
    taggedRealize (linearSystem c124_A c124_O) (guardedCodeFormula c124_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c124_A c124_O) :=
  replaySource_standard_formula c124_A c124_O c124_evidence c124_result c124_checked_data e
abbrev c125_R := ZMod 3125
def c125_A : Fin 3 → Mat c125_R 1 1 := ![![![2943]], ![![2010]], ![![2491]]]
def c125_O : Mat c125_R 1 1 := ![![0]]
def c125_evidence : List (Evidence c125_R 1) := [
  .combination []]
def c125_result : List (Test 3 1) := []
theorem c125_checked_data : replaySource c125_A c125_O c125_evidence = some c125_result := by decide +kernel
theorem c125_reference_result :
    finitePrimeDiscover 5 5 1 (fun a => rowRight (c125_A a)) c125_O = some c125_result :=
  replaySource_reference 5 5 1 (by decide +kernel) c125_A c125_O c125_evidence c125_result c125_checked_data
theorem c125_all_words (x y : Fin 1 → c125_R) :
    CodeEqual (linearSystem c125_A c125_O) c125_result x y ↔ ObsEq (linearSystem c125_A c125_O) x y :=
  replaySource_all_words c125_A c125_O c125_evidence c125_result c125_checked_data x y
theorem c125_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c125_R) c125_R) :
    taggedRealize (linearSystem c125_A c125_O) (guardedCodeFormula c125_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c125_A c125_O) :=
  replaySource_standard_formula c125_A c125_O c125_evidence c125_result c125_checked_data e
abbrev c126_R := ZMod 2
def c126_A : Fin 1 → Mat c126_R 2 2 := ![![![0, 0], ![0, 1]]]
def c126_O : Mat c126_R 2 2 := ![![1, 1], ![1, 1]]
def c126_evidence : List (Evidence c126_R 2) := [
  .separation (![1, 0]),
  .combination [1],
  .separation (![1, 1]),
  .combination [0, 1]]
def c126_result : List (Test 1 2) := [([], 0), ([0], 0)]
theorem c126_checked_data : replaySource c126_A c126_O c126_evidence = some c126_result := by decide +kernel
theorem c126_reference_result :
    finitePrimeDiscover 2 1 2 (fun a => rowRight (c126_A a)) c126_O = some c126_result :=
  replaySource_reference 2 1 2 (by decide +kernel) c126_A c126_O c126_evidence c126_result c126_checked_data
theorem c126_all_words (x y : Fin 2 → c126_R) :
    CodeEqual (linearSystem c126_A c126_O) c126_result x y ↔ ObsEq (linearSystem c126_A c126_O) x y :=
  replaySource_all_words c126_A c126_O c126_evidence c126_result c126_checked_data x y
theorem c126_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c126_R) c126_R) :
    taggedRealize (linearSystem c126_A c126_O) (guardedCodeFormula c126_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c126_A c126_O) :=
  replaySource_standard_formula c126_A c126_O c126_evidence c126_result c126_checked_data e
abbrev c127_R := ZMod 3
def c127_A : Fin 2 → Mat c127_R 2 2 := ![![![1, 2], ![0, 1]], ![![1, 1], ![2, 1]]]
def c127_O : Mat c127_R 1 2 := ![![2, 2]]
def c127_evidence : List (Evidence c127_R 2) := [
  .separation (![1, 0]),
  .separation (![2, 1]),
  .combination [2, 1],
  .combination [2, 2],
  .combination [1, 0]]
def c127_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c127_checked_data : replaySource c127_A c127_O c127_evidence = some c127_result := by decide +kernel
theorem c127_reference_result :
    finitePrimeDiscover 3 1 2 (fun a => rowRight (c127_A a)) c127_O = some c127_result :=
  replaySource_reference 3 1 2 (by decide +kernel) c127_A c127_O c127_evidence c127_result c127_checked_data
theorem c127_all_words (x y : Fin 2 → c127_R) :
    CodeEqual (linearSystem c127_A c127_O) c127_result x y ↔ ObsEq (linearSystem c127_A c127_O) x y :=
  replaySource_all_words c127_A c127_O c127_evidence c127_result c127_checked_data x y
theorem c127_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c127_R) c127_R) :
    taggedRealize (linearSystem c127_A c127_O) (guardedCodeFormula c127_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c127_A c127_O) :=
  replaySource_standard_formula c127_A c127_O c127_evidence c127_result c127_checked_data e
abbrev c128_R := ZMod 5
def c128_A : Fin 3 → Mat c128_R 2 2 := ![![![0, 1], ![2, 0]], ![![3, 2], ![2, 2]], ![![3, 3], ![3, 0]]]
def c128_O : Mat c128_R 2 2 := ![![0, 4], ![4, 4]]
def c128_evidence : List (Evidence c128_R 2) := [
  .separation (![0, 1]),
  .separation (![1, 0]),
  .combination [3, 2],
  .combination [0, 2],
  .combination [2, 3],
  .combination [4, 2],
  .combination [4, 0],
  .combination [2, 1]]
def c128_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c128_checked_data : replaySource c128_A c128_O c128_evidence = some c128_result := by decide +kernel
theorem c128_reference_result :
    finitePrimeDiscover 5 1 2 (fun a => rowRight (c128_A a)) c128_O = some c128_result :=
  replaySource_reference 5 1 2 (by decide +kernel) c128_A c128_O c128_evidence c128_result c128_checked_data
theorem c128_all_words (x y : Fin 2 → c128_R) :
    CodeEqual (linearSystem c128_A c128_O) c128_result x y ↔ ObsEq (linearSystem c128_A c128_O) x y :=
  replaySource_all_words c128_A c128_O c128_evidence c128_result c128_checked_data x y
theorem c128_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c128_R) c128_R) :
    taggedRealize (linearSystem c128_A c128_O) (guardedCodeFormula c128_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c128_A c128_O) :=
  replaySource_standard_formula c128_A c128_O c128_evidence c128_result c128_checked_data e
abbrev c129_R := ZMod 4
def c129_A : Fin 1 → Mat c129_R 2 2 := ![![![0, 2], ![1, 3]]]
def c129_O : Mat c129_R 1 2 := ![![3, 1]]
def c129_evidence : List (Evidence c129_R 2) := [
  .separation (![1, 0]),
  .separation (![1, 1]),
  .combination [0, 1]]
def c129_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c129_checked_data : replaySource c129_A c129_O c129_evidence = some c129_result := by decide +kernel
theorem c129_reference_result :
    finitePrimeDiscover 2 2 2 (fun a => rowRight (c129_A a)) c129_O = some c129_result :=
  replaySource_reference 2 2 2 (by decide +kernel) c129_A c129_O c129_evidence c129_result c129_checked_data
theorem c129_all_words (x y : Fin 2 → c129_R) :
    CodeEqual (linearSystem c129_A c129_O) c129_result x y ↔ ObsEq (linearSystem c129_A c129_O) x y :=
  replaySource_all_words c129_A c129_O c129_evidence c129_result c129_checked_data x y
theorem c129_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c129_R) c129_R) :
    taggedRealize (linearSystem c129_A c129_O) (guardedCodeFormula c129_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c129_A c129_O) :=
  replaySource_standard_formula c129_A c129_O c129_evidence c129_result c129_checked_data e
abbrev c130_R := ZMod 9
def c130_A : Fin 2 → Mat c130_R 2 2 := ![![![8, 7], ![3, 7]], ![![2, 0], ![8, 3]]]
def c130_O : Mat c130_R 2 2 := ![![1, 0], ![6, 6]]
def c130_evidence : List (Evidence c130_R 2) := [
  .separation (![1, 0]),
  .separation (![0, 1]),
  .separation (![0, 3]),
  .combination [2, 0, 0],
  .combination [6, 0, 3],
  .combination [6, 0, 0],
  .combination [1, 0, 6],
  .combination [3, 0, 3]]
def c130_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c130_checked_data : replaySource c130_A c130_O c130_evidence = some c130_result := by decide +kernel
theorem c130_reference_result :
    finitePrimeDiscover 3 2 2 (fun a => rowRight (c130_A a)) c130_O = some c130_result :=
  replaySource_reference 3 2 2 (by decide +kernel) c130_A c130_O c130_evidence c130_result c130_checked_data
theorem c130_all_words (x y : Fin 2 → c130_R) :
    CodeEqual (linearSystem c130_A c130_O) c130_result x y ↔ ObsEq (linearSystem c130_A c130_O) x y :=
  replaySource_all_words c130_A c130_O c130_evidence c130_result c130_checked_data x y
theorem c130_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c130_R) c130_R) :
    taggedRealize (linearSystem c130_A c130_O) (guardedCodeFormula c130_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c130_A c130_O) :=
  replaySource_standard_formula c130_A c130_O c130_evidence c130_result c130_checked_data e
abbrev c131_R := ZMod 25
def c131_A : Fin 3 → Mat c131_R 2 2 := ![![![6, 12], ![12, 5]], ![![13, 3], ![10, 22]], ![![2, 2], ![21, 19]]]
def c131_O : Mat c131_R 1 2 := ![![3, 17]]
def c131_evidence : List (Evidence c131_R 2) := [
  .separation (![1, 0]),
  .separation (![11, 1]),
  .combination [17, 14],
  .combination [15, 19],
  .combination [14, 11],
  .combination [0, 18],
  .combination [1, 6]]
def c131_result : List (Test 3 1) := [([], 0), ([0], 0)]
theorem c131_checked_data : replaySource c131_A c131_O c131_evidence = some c131_result := by decide +kernel
theorem c131_reference_result :
    finitePrimeDiscover 5 2 2 (fun a => rowRight (c131_A a)) c131_O = some c131_result :=
  replaySource_reference 5 2 2 (by decide +kernel) c131_A c131_O c131_evidence c131_result c131_checked_data
theorem c131_all_words (x y : Fin 2 → c131_R) :
    CodeEqual (linearSystem c131_A c131_O) c131_result x y ↔ ObsEq (linearSystem c131_A c131_O) x y :=
  replaySource_all_words c131_A c131_O c131_evidence c131_result c131_checked_data x y
theorem c131_standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → c131_R) c131_R) :
    taggedRealize (linearSystem c131_A c131_O) (guardedCodeFormula c131_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c131_A c131_O) :=
  replaySource_standard_formula c131_A c131_O c131_evidence c131_result c131_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch10
