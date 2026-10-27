module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch02
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c024_R := ZMod 4
def c024_A : Fin 1 → Mat c024_R 1 1 := ![![![0]]]
def c024_O : Mat c024_R 2 1 := ![![1], ![1]]
def c024_evidence : List (Evidence c024_R 1) := [
  .separation (![1]),
  .combination [1],
  .combination [0]]
def c024_result : List (Test 1 2) := [([], 0)]
theorem c024_checked_data : replaySource c024_A c024_O c024_evidence = some c024_result := by decide +kernel
theorem c024_reference_result :
    finitePrimeDiscover 2 2 1 (fun a => rowRight (c024_A a)) c024_O = some c024_result :=
  replaySource_reference 2 2 1 (by decide +kernel) c024_A c024_O c024_evidence c024_result c024_checked_data
theorem c024_all_words (x y : Fin 1 → c024_R) :
    CodeEqual (linearSystem c024_A c024_O) c024_result x y ↔ ObsEq (linearSystem c024_A c024_O) x y :=
  replaySource_all_words c024_A c024_O c024_evidence c024_result c024_checked_data x y
theorem c024_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c024_R) c024_R) :
    taggedRealize (linearSystem c024_A c024_O) (guardedCodeFormula c024_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c024_A c024_O) :=
  replaySource_standard_formula c024_A c024_O c024_evidence c024_result c024_checked_data e
abbrev c025_R := ZMod 9
def c025_A : Fin 2 → Mat c025_R 1 1 := ![![![6]], ![![0]]]
def c025_O : Mat c025_R 1 1 := ![![4]]
def c025_evidence : List (Evidence c025_R 1) := [
  .separation (![1]),
  .combination [6],
  .combination [0]]
def c025_result : List (Test 2 1) := [([], 0)]
theorem c025_checked_data : replaySource c025_A c025_O c025_evidence = some c025_result := by decide +kernel
theorem c025_reference_result :
    finitePrimeDiscover 3 2 1 (fun a => rowRight (c025_A a)) c025_O = some c025_result :=
  replaySource_reference 3 2 1 (by decide +kernel) c025_A c025_O c025_evidence c025_result c025_checked_data
theorem c025_all_words (x y : Fin 1 → c025_R) :
    CodeEqual (linearSystem c025_A c025_O) c025_result x y ↔ ObsEq (linearSystem c025_A c025_O) x y :=
  replaySource_all_words c025_A c025_O c025_evidence c025_result c025_checked_data x y
theorem c025_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c025_R) c025_R) :
    taggedRealize (linearSystem c025_A c025_O) (guardedCodeFormula c025_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c025_A c025_O) :=
  replaySource_standard_formula c025_A c025_O c025_evidence c025_result c025_checked_data e
abbrev c026_R := ZMod 25
def c026_A : Fin 3 → Mat c026_R 1 1 := ![![![2]], ![![9]], ![![11]]]
def c026_O : Mat c026_R 2 1 := ![![21], ![17]]
def c026_evidence : List (Evidence c026_R 1) := [
  .separation (![1]),
  .combination [2],
  .combination [2],
  .combination [9],
  .combination [11]]
def c026_result : List (Test 3 2) := [([], 0)]
theorem c026_checked_data : replaySource c026_A c026_O c026_evidence = some c026_result := by decide +kernel
theorem c026_reference_result :
    finitePrimeDiscover 5 2 1 (fun a => rowRight (c026_A a)) c026_O = some c026_result :=
  replaySource_reference 5 2 1 (by decide +kernel) c026_A c026_O c026_evidence c026_result c026_checked_data
theorem c026_all_words (x y : Fin 1 → c026_R) :
    CodeEqual (linearSystem c026_A c026_O) c026_result x y ↔ ObsEq (linearSystem c026_A c026_O) x y :=
  replaySource_all_words c026_A c026_O c026_evidence c026_result c026_checked_data x y
theorem c026_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c026_R) c026_R) :
    taggedRealize (linearSystem c026_A c026_O) (guardedCodeFormula c026_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c026_A c026_O) :=
  replaySource_standard_formula c026_A c026_O c026_evidence c026_result c026_checked_data e
abbrev c027_R := ZMod 8
def c027_A : Fin 1 → Mat c027_R 1 1 := ![![![5]]]
def c027_O : Mat c027_R 1 1 := ![![1]]
def c027_evidence : List (Evidence c027_R 1) := [
  .separation (![1]),
  .combination [5]]
def c027_result : List (Test 1 1) := [([], 0)]
theorem c027_checked_data : replaySource c027_A c027_O c027_evidence = some c027_result := by decide +kernel
theorem c027_reference_result :
    finitePrimeDiscover 2 3 1 (fun a => rowRight (c027_A a)) c027_O = some c027_result :=
  replaySource_reference 2 3 1 (by decide +kernel) c027_A c027_O c027_evidence c027_result c027_checked_data
theorem c027_all_words (x y : Fin 1 → c027_R) :
    CodeEqual (linearSystem c027_A c027_O) c027_result x y ↔ ObsEq (linearSystem c027_A c027_O) x y :=
  replaySource_all_words c027_A c027_O c027_evidence c027_result c027_checked_data x y
theorem c027_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c027_R) c027_R) :
    taggedRealize (linearSystem c027_A c027_O) (guardedCodeFormula c027_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c027_A c027_O) :=
  replaySource_standard_formula c027_A c027_O c027_evidence c027_result c027_checked_data e
abbrev c028_R := ZMod 27
def c028_A : Fin 2 → Mat c028_R 1 1 := ![![![7]], ![![4]]]
def c028_O : Mat c028_R 2 1 := ![![18], ![9]]
def c028_evidence : List (Evidence c028_R 1) := [
  .separation (![1]),
  .combination [14],
  .combination [1],
  .combination [1]]
def c028_result : List (Test 2 2) := [([], 0)]
theorem c028_checked_data : replaySource c028_A c028_O c028_evidence = some c028_result := by decide +kernel
theorem c028_reference_result :
    finitePrimeDiscover 3 3 1 (fun a => rowRight (c028_A a)) c028_O = some c028_result :=
  replaySource_reference 3 3 1 (by decide +kernel) c028_A c028_O c028_evidence c028_result c028_checked_data
theorem c028_all_words (x y : Fin 1 → c028_R) :
    CodeEqual (linearSystem c028_A c028_O) c028_result x y ↔ ObsEq (linearSystem c028_A c028_O) x y :=
  replaySource_all_words c028_A c028_O c028_evidence c028_result c028_checked_data x y
theorem c028_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c028_R) c028_R) :
    taggedRealize (linearSystem c028_A c028_O) (guardedCodeFormula c028_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c028_A c028_O) :=
  replaySource_standard_formula c028_A c028_O c028_evidence c028_result c028_checked_data e
abbrev c029_R := ZMod 125
def c029_A : Fin 3 → Mat c029_R 1 1 := ![![![121]], ![![45]], ![![80]]]
def c029_O : Mat c029_R 1 1 := ![![29]]
def c029_evidence : List (Evidence c029_R 1) := [
  .separation (![1]),
  .combination [121],
  .combination [45],
  .combination [80]]
def c029_result : List (Test 3 1) := [([], 0)]
theorem c029_checked_data : replaySource c029_A c029_O c029_evidence = some c029_result := by decide +kernel
theorem c029_reference_result :
    finitePrimeDiscover 5 3 1 (fun a => rowRight (c029_A a)) c029_O = some c029_result :=
  replaySource_reference 5 3 1 (by decide +kernel) c029_A c029_O c029_evidence c029_result c029_checked_data
theorem c029_all_words (x y : Fin 1 → c029_R) :
    CodeEqual (linearSystem c029_A c029_O) c029_result x y ↔ ObsEq (linearSystem c029_A c029_O) x y :=
  replaySource_all_words c029_A c029_O c029_evidence c029_result c029_checked_data x y
theorem c029_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c029_R) c029_R) :
    taggedRealize (linearSystem c029_A c029_O) (guardedCodeFormula c029_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c029_A c029_O) :=
  replaySource_standard_formula c029_A c029_O c029_evidence c029_result c029_checked_data e
abbrev c030_R := ZMod 16
def c030_A : Fin 1 → Mat c030_R 1 1 := ![![![8]]]
def c030_O : Mat c030_R 2 1 := ![![3], ![4]]
def c030_evidence : List (Evidence c030_R 1) := [
  .separation (![1]),
  .combination [12],
  .combination [8]]
def c030_result : List (Test 1 2) := [([], 0)]
theorem c030_checked_data : replaySource c030_A c030_O c030_evidence = some c030_result := by decide +kernel
theorem c030_reference_result :
    finitePrimeDiscover 2 4 1 (fun a => rowRight (c030_A a)) c030_O = some c030_result :=
  replaySource_reference 2 4 1 (by decide +kernel) c030_A c030_O c030_evidence c030_result c030_checked_data
theorem c030_all_words (x y : Fin 1 → c030_R) :
    CodeEqual (linearSystem c030_A c030_O) c030_result x y ↔ ObsEq (linearSystem c030_A c030_O) x y :=
  replaySource_all_words c030_A c030_O c030_evidence c030_result c030_checked_data x y
theorem c030_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c030_R) c030_R) :
    taggedRealize (linearSystem c030_A c030_O) (guardedCodeFormula c030_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c030_A c030_O) :=
  replaySource_standard_formula c030_A c030_O c030_evidence c030_result c030_checked_data e
abbrev c031_R := ZMod 81
def c031_A : Fin 2 → Mat c031_R 1 1 := ![![![11]], ![![54]]]
def c031_O : Mat c031_R 1 1 := ![![7]]
def c031_evidence : List (Evidence c031_R 1) := [
  .separation (![1]),
  .combination [11],
  .combination [54]]
def c031_result : List (Test 2 1) := [([], 0)]
theorem c031_checked_data : replaySource c031_A c031_O c031_evidence = some c031_result := by decide +kernel
theorem c031_reference_result :
    finitePrimeDiscover 3 4 1 (fun a => rowRight (c031_A a)) c031_O = some c031_result :=
  replaySource_reference 3 4 1 (by decide +kernel) c031_A c031_O c031_evidence c031_result c031_checked_data
theorem c031_all_words (x y : Fin 1 → c031_R) :
    CodeEqual (linearSystem c031_A c031_O) c031_result x y ↔ ObsEq (linearSystem c031_A c031_O) x y :=
  replaySource_all_words c031_A c031_O c031_evidence c031_result c031_checked_data x y
theorem c031_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c031_R) c031_R) :
    taggedRealize (linearSystem c031_A c031_O) (guardedCodeFormula c031_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c031_A c031_O) :=
  replaySource_standard_formula c031_A c031_O c031_evidence c031_result c031_checked_data e
abbrev c032_R := ZMod 625
def c032_A : Fin 3 → Mat c032_R 1 1 := ![![![502]], ![![153]], ![![537]]]
def c032_O : Mat c032_R 2 1 := ![![327], ![292]]
def c032_evidence : List (Evidence c032_R 1) := [
  .separation (![1]),
  .combination [171],
  .combination [502],
  .combination [153],
  .combination [537]]
def c032_result : List (Test 3 2) := [([], 0)]
theorem c032_checked_data : replaySource c032_A c032_O c032_evidence = some c032_result := by decide +kernel
theorem c032_reference_result :
    finitePrimeDiscover 5 4 1 (fun a => rowRight (c032_A a)) c032_O = some c032_result :=
  replaySource_reference 5 4 1 (by decide +kernel) c032_A c032_O c032_evidence c032_result c032_checked_data
theorem c032_all_words (x y : Fin 1 → c032_R) :
    CodeEqual (linearSystem c032_A c032_O) c032_result x y ↔ ObsEq (linearSystem c032_A c032_O) x y :=
  replaySource_all_words c032_A c032_O c032_evidence c032_result c032_checked_data x y
theorem c032_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c032_R) c032_R) :
    taggedRealize (linearSystem c032_A c032_O) (guardedCodeFormula c032_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c032_A c032_O) :=
  replaySource_standard_formula c032_A c032_O c032_evidence c032_result c032_checked_data e
abbrev c033_R := ZMod 32
def c033_A : Fin 1 → Mat c033_R 1 1 := ![![![3]]]
def c033_O : Mat c033_R 1 1 := ![![7]]
def c033_evidence : List (Evidence c033_R 1) := [
  .separation (![1]),
  .combination [3]]
def c033_result : List (Test 1 1) := [([], 0)]
theorem c033_checked_data : replaySource c033_A c033_O c033_evidence = some c033_result := by decide +kernel
theorem c033_reference_result :
    finitePrimeDiscover 2 5 1 (fun a => rowRight (c033_A a)) c033_O = some c033_result :=
  replaySource_reference 2 5 1 (by decide +kernel) c033_A c033_O c033_evidence c033_result c033_checked_data
theorem c033_all_words (x y : Fin 1 → c033_R) :
    CodeEqual (linearSystem c033_A c033_O) c033_result x y ↔ ObsEq (linearSystem c033_A c033_O) x y :=
  replaySource_all_words c033_A c033_O c033_evidence c033_result c033_checked_data x y
theorem c033_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c033_R) c033_R) :
    taggedRealize (linearSystem c033_A c033_O) (guardedCodeFormula c033_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c033_A c033_O) :=
  replaySource_standard_formula c033_A c033_O c033_evidence c033_result c033_checked_data e
abbrev c034_R := ZMod 243
def c034_A : Fin 2 → Mat c034_R 1 1 := ![![![104]], ![![102]]]
def c034_O : Mat c034_R 2 1 := ![![0], ![0]]
def c034_evidence : List (Evidence c034_R 1) := [
  .combination [],
  .combination []]
def c034_result : List (Test 2 2) := []
theorem c034_checked_data : replaySource c034_A c034_O c034_evidence = some c034_result := by decide +kernel
theorem c034_reference_result :
    finitePrimeDiscover 3 5 1 (fun a => rowRight (c034_A a)) c034_O = some c034_result :=
  replaySource_reference 3 5 1 (by decide +kernel) c034_A c034_O c034_evidence c034_result c034_checked_data
theorem c034_all_words (x y : Fin 1 → c034_R) :
    CodeEqual (linearSystem c034_A c034_O) c034_result x y ↔ ObsEq (linearSystem c034_A c034_O) x y :=
  replaySource_all_words c034_A c034_O c034_evidence c034_result c034_checked_data x y
theorem c034_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c034_R) c034_R) :
    taggedRealize (linearSystem c034_A c034_O) (guardedCodeFormula c034_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c034_A c034_O) :=
  replaySource_standard_formula c034_A c034_O c034_evidence c034_result c034_checked_data e
abbrev c035_R := ZMod 3125
def c035_A : Fin 3 → Mat c035_R 1 1 := ![![![227]], ![![1859]], ![![2070]]]
def c035_O : Mat c035_R 1 1 := ![![625]]
def c035_evidence : List (Evidence c035_R 1) := [
  .separation (![1]),
  .combination [2],
  .combination [4],
  .combination [0]]
def c035_result : List (Test 3 1) := [([], 0)]
theorem c035_checked_data : replaySource c035_A c035_O c035_evidence = some c035_result := by decide +kernel
theorem c035_reference_result :
    finitePrimeDiscover 5 5 1 (fun a => rowRight (c035_A a)) c035_O = some c035_result :=
  replaySource_reference 5 5 1 (by decide +kernel) c035_A c035_O c035_evidence c035_result c035_checked_data
theorem c035_all_words (x y : Fin 1 → c035_R) :
    CodeEqual (linearSystem c035_A c035_O) c035_result x y ↔ ObsEq (linearSystem c035_A c035_O) x y :=
  replaySource_all_words c035_A c035_O c035_evidence c035_result c035_checked_data x y
theorem c035_standard_definition (e : Fin 2 → TaggedCarrier (Fin 1 → c035_R) c035_R) :
    taggedRealize (linearSystem c035_A c035_O) (guardedCodeFormula c035_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c035_A c035_O) :=
  replaySource_standard_formula c035_A c035_O c035_evidence c035_result c035_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch02
