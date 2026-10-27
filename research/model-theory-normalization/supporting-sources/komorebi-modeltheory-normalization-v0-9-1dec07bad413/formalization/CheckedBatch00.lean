module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedBatch00
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev c000_R := ZMod 16
def c000_A : Fin 1 → Mat c000_R 8 8 := ![![![0, 1, 0, 0, 0, 0, 0, 0], ![0, 0, 1, 0, 0, 0, 0, 0], ![0, 0, 0, 1, 0, 0, 0, 0], ![0, 0, 0, 0, 1, 0, 0, 0], ![0, 0, 0, 0, 0, 1, 0, 0], ![0, 0, 0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 0, 0, 0, 1], ![0, 0, 0, 0, 0, 0, 0, 0]]]
def c000_O : Mat c000_R 1 8 := ![![1, 0, 0, 0, 0, 0, 0, 0]]
def c000_evidence : List (Evidence c000_R 8) := [
  .separation (![1, 0, 0, 0, 0, 0, 0, 0]),
  .separation (![0, 1, 0, 0, 0, 0, 0, 0]),
  .separation (![0, 0, 1, 0, 0, 0, 0, 0]),
  .separation (![0, 0, 0, 1, 0, 0, 0, 0]),
  .separation (![0, 0, 0, 0, 1, 0, 0, 0]),
  .separation (![0, 0, 0, 0, 0, 1, 0, 0]),
  .separation (![0, 0, 0, 0, 0, 0, 1, 0]),
  .separation (![0, 0, 0, 0, 0, 0, 0, 1]),
  .combination [0, 0, 0, 0, 0, 0, 0, 0]]
def c000_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0), ([0,0,0,0,0,0], 0), ([0,0,0,0,0,0,0], 0)]
theorem c000_checked_data : replaySource c000_A c000_O c000_evidence = some c000_result := by decide +kernel
theorem c000_reference_result :
    finitePrimeDiscover 2 4 8 (fun a => rowRight (c000_A a)) c000_O = some c000_result :=
  replaySource_reference 2 4 8 (by decide +kernel) c000_A c000_O c000_evidence c000_result c000_checked_data
theorem c000_all_words (x y : Fin 8 → c000_R) :
    CodeEqual (linearSystem c000_A c000_O) c000_result x y ↔ ObsEq (linearSystem c000_A c000_O) x y :=
  replaySource_all_words c000_A c000_O c000_evidence c000_result c000_checked_data x y
theorem c000_standard_definition (e : Fin 2 → TaggedCarrier (Fin 8 → c000_R) c000_R) :
    taggedRealize (linearSystem c000_A c000_O) (guardedCodeFormula c000_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c000_A c000_O) :=
  replaySource_standard_formula c000_A c000_O c000_evidence c000_result c000_checked_data e
abbrev c001_R := ZMod 4
def c001_A : Fin 2 → Mat c001_R 4 4 := ![![![3, 2, 0, 2], ![1, 2, 3, 1], ![1, 2, 1, 3], ![3, 3, 3, 0]], ![![2, 0, 0, 0], ![1, 0, 2, 1], ![2, 0, 0, 2], ![2, 3, 2, 2]]]
def c001_O : Mat c001_R 1 4 := ![![3, 0, 0, 0]]
def c001_evidence : List (Evidence c001_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 1, 0, 0]),
  .combination [2, 0],
  .combination [1, 0],
  .combination [1, 1]]
def c001_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c001_checked_data : replaySource c001_A c001_O c001_evidence = some c001_result := by decide +kernel
theorem c001_reference_result :
    finitePrimeDiscover 2 2 4 (fun a => rowRight (c001_A a)) c001_O = some c001_result :=
  replaySource_reference 2 2 4 (by decide +kernel) c001_A c001_O c001_evidence c001_result c001_checked_data
theorem c001_all_words (x y : Fin 4 → c001_R) :
    CodeEqual (linearSystem c001_A c001_O) c001_result x y ↔ ObsEq (linearSystem c001_A c001_O) x y :=
  replaySource_all_words c001_A c001_O c001_evidence c001_result c001_checked_data x y
theorem c001_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c001_R) c001_R) :
    taggedRealize (linearSystem c001_A c001_O) (guardedCodeFormula c001_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c001_A c001_O) :=
  replaySource_standard_formula c001_A c001_O c001_evidence c001_result c001_checked_data e
abbrev c002_R := ZMod 4
def c002_A : Fin 2 → Mat c002_R 6 6 := ![![![1, 2, 3, 0, 0, 1], ![3, 0, 2, 1, 1, 1], ![0, 2, 2, 1, 1, 1], ![0, 1, 2, 2, 3, 1], ![1, 2, 0, 2, 1, 0], ![0, 0, 2, 0, 0, 3]], ![![1, 0, 1, 2, 0, 1], ![2, 3, 2, 3, 1, 1], ![2, 0, 0, 3, 1, 1], ![3, 1, 3, 1, 2, 0], ![1, 3, 3, 3, 2, 0], ![0, 0, 0, 0, 2, 2]]]
def c002_O : Mat c002_R 1 6 := ![![2, 2, 0, 0, 2, 1]]
def c002_evidence : List (Evidence c002_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![0, 1, 0, 0, 0, 2]),
  .combination [2, 0],
  .combination [1, 0],
  .combination [1, 1]]
def c002_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c002_checked_data : replaySource c002_A c002_O c002_evidence = some c002_result := by decide +kernel
theorem c002_reference_result :
    finitePrimeDiscover 2 2 6 (fun a => rowRight (c002_A a)) c002_O = some c002_result :=
  replaySource_reference 2 2 6 (by decide +kernel) c002_A c002_O c002_evidence c002_result c002_checked_data
theorem c002_all_words (x y : Fin 6 → c002_R) :
    CodeEqual (linearSystem c002_A c002_O) c002_result x y ↔ ObsEq (linearSystem c002_A c002_O) x y :=
  replaySource_all_words c002_A c002_O c002_evidence c002_result c002_checked_data x y
theorem c002_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c002_R) c002_R) :
    taggedRealize (linearSystem c002_A c002_O) (guardedCodeFormula c002_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c002_A c002_O) :=
  replaySource_standard_formula c002_A c002_O c002_evidence c002_result c002_checked_data e
abbrev c003_R := ZMod 8
def c003_A : Fin 2 → Mat c003_R 4 4 := ![![![4, 1, 2, 5], ![7, 6, 1, 2], ![3, 5, 4, 0], ![4, 2, 4, 3]], ![![5, 7, 1, 2], ![1, 6, 7, 0], ![7, 5, 4, 2], ![0, 4, 2, 2]]]
def c003_O : Mat c003_R 1 4 := ![![2, 0, 6, 5]]
def c003_evidence : List (Evidence c003_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 1, 0, 0]),
  .combination [2, 0],
  .combination [7, 2],
  .combination [1, 1]]
def c003_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c003_checked_data : replaySource c003_A c003_O c003_evidence = some c003_result := by decide +kernel
theorem c003_reference_result :
    finitePrimeDiscover 2 3 4 (fun a => rowRight (c003_A a)) c003_O = some c003_result :=
  replaySource_reference 2 3 4 (by decide +kernel) c003_A c003_O c003_evidence c003_result c003_checked_data
theorem c003_all_words (x y : Fin 4 → c003_R) :
    CodeEqual (linearSystem c003_A c003_O) c003_result x y ↔ ObsEq (linearSystem c003_A c003_O) x y :=
  replaySource_all_words c003_A c003_O c003_evidence c003_result c003_checked_data x y
theorem c003_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c003_R) c003_R) :
    taggedRealize (linearSystem c003_A c003_O) (guardedCodeFormula c003_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c003_A c003_O) :=
  replaySource_standard_formula c003_A c003_O c003_evidence c003_result c003_checked_data e
abbrev c004_R := ZMod 8
def c004_A : Fin 2 → Mat c004_R 6 6 := ![![![1, 3, 5, 6, 1, 6], ![4, 4, 1, 2, 3, 5], ![6, 4, 6, 0, 0, 5], ![0, 3, 7, 0, 5, 3], ![0, 0, 0, 6, 3, 1], ![4, 7, 4, 2, 7, 7]], ![![3, 3, 0, 3, 0, 2], ![6, 3, 6, 5, 0, 2], ![5, 5, 6, 2, 0, 1], ![7, 1, 7, 1, 1, 4], ![2, 1, 6, 0, 7, 2], ![7, 2, 6, 5, 6, 1]]]
def c004_O : Mat c004_R 1 6 := ![![4, 1, 3, 4, 6, 1]]
def c004_evidence : List (Evidence c004_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 4, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [7, 2],
  .combination [1, 1]]
def c004_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c004_checked_data : replaySource c004_A c004_O c004_evidence = some c004_result := by decide +kernel
theorem c004_reference_result :
    finitePrimeDiscover 2 3 6 (fun a => rowRight (c004_A a)) c004_O = some c004_result :=
  replaySource_reference 2 3 6 (by decide +kernel) c004_A c004_O c004_evidence c004_result c004_checked_data
theorem c004_all_words (x y : Fin 6 → c004_R) :
    CodeEqual (linearSystem c004_A c004_O) c004_result x y ↔ ObsEq (linearSystem c004_A c004_O) x y :=
  replaySource_all_words c004_A c004_O c004_evidence c004_result c004_checked_data x y
theorem c004_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c004_R) c004_R) :
    taggedRealize (linearSystem c004_A c004_O) (guardedCodeFormula c004_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c004_A c004_O) :=
  replaySource_standard_formula c004_A c004_O c004_evidence c004_result c004_checked_data e
abbrev c005_R := ZMod 32
def c005_A : Fin 2 → Mat c005_R 4 4 := ![![![30, 8, 13, 31], ![6, 21, 0, 1], ![22, 24, 31, 8], ![3, 28, 31, 9]], ![![27, 14, 23, 9], ![24, 18, 17, 27], ![18, 4, 15, 30], ![25, 6, 11, 12]]]
def c005_O : Mat c005_R 1 4 := ![![27, 7, 11, 7]]
def c005_evidence : List (Evidence c005_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![27, 1, 0, 0]),
  .combination [2, 0],
  .combination [31, 2],
  .combination [1, 1]]
def c005_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c005_checked_data : replaySource c005_A c005_O c005_evidence = some c005_result := by decide +kernel
theorem c005_reference_result :
    finitePrimeDiscover 2 5 4 (fun a => rowRight (c005_A a)) c005_O = some c005_result :=
  replaySource_reference 2 5 4 (by decide +kernel) c005_A c005_O c005_evidence c005_result c005_checked_data
theorem c005_all_words (x y : Fin 4 → c005_R) :
    CodeEqual (linearSystem c005_A c005_O) c005_result x y ↔ ObsEq (linearSystem c005_A c005_O) x y :=
  replaySource_all_words c005_A c005_O c005_evidence c005_result c005_checked_data x y
theorem c005_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c005_R) c005_R) :
    taggedRealize (linearSystem c005_A c005_O) (guardedCodeFormula c005_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c005_A c005_O) :=
  replaySource_standard_formula c005_A c005_O c005_evidence c005_result c005_checked_data e
abbrev c006_R := ZMod 32
def c006_A : Fin 2 → Mat c006_R 6 6 := ![![![7, 1, 3, 30, 26, 12], ![14, 0, 21, 17, 5, 24], ![26, 11, 24, 15, 20, 19], ![16, 3, 19, 14, 28, 19], ![12, 26, 25, 26, 13, 7], ![8, 19, 15, 14, 0, 7]], ![![9, 5, 8, 10, 20, 20], ![23, 15, 31, 8, 29, 7], ![21, 5, 31, 15, 0, 17], ![24, 17, 30, 0, 18, 22], ![28, 9, 12, 2, 4, 8], ![25, 15, 26, 14, 14, 8]]]
def c006_O : Mat c006_R 1 6 := ![![13, 18, 20, 28, 0, 27]]
def c006_evidence : List (Evidence c006_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![6, 1, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [31, 2],
  .combination [1, 1]]
def c006_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c006_checked_data : replaySource c006_A c006_O c006_evidence = some c006_result := by decide +kernel
theorem c006_reference_result :
    finitePrimeDiscover 2 5 6 (fun a => rowRight (c006_A a)) c006_O = some c006_result :=
  replaySource_reference 2 5 6 (by decide +kernel) c006_A c006_O c006_evidence c006_result c006_checked_data
theorem c006_all_words (x y : Fin 6 → c006_R) :
    CodeEqual (linearSystem c006_A c006_O) c006_result x y ↔ ObsEq (linearSystem c006_A c006_O) x y :=
  replaySource_all_words c006_A c006_O c006_evidence c006_result c006_checked_data x y
theorem c006_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c006_R) c006_R) :
    taggedRealize (linearSystem c006_A c006_O) (guardedCodeFormula c006_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c006_A c006_O) :=
  replaySource_standard_formula c006_A c006_O c006_evidence c006_result c006_checked_data e
abbrev c007_R := ZMod 9
def c007_A : Fin 2 → Mat c007_R 4 4 := ![![![0, 0, 7, 6], ![8, 4, 5, 8], ![8, 3, 6, 5], ![7, 6, 1, 2]], ![![5, 0, 8, 0], ![3, 5, 4, 1], ![3, 6, 8, 6], ![6, 6, 5, 7]]]
def c007_O : Mat c007_R 1 4 := ![![6, 2, 0, 5]]
def c007_evidence : List (Evidence c007_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 0, 1, 0]),
  .combination [2, 0],
  .combination [8, 2],
  .combination [1, 1]]
def c007_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c007_checked_data : replaySource c007_A c007_O c007_evidence = some c007_result := by decide +kernel
theorem c007_reference_result :
    finitePrimeDiscover 3 2 4 (fun a => rowRight (c007_A a)) c007_O = some c007_result :=
  replaySource_reference 3 2 4 (by decide +kernel) c007_A c007_O c007_evidence c007_result c007_checked_data
theorem c007_all_words (x y : Fin 4 → c007_R) :
    CodeEqual (linearSystem c007_A c007_O) c007_result x y ↔ ObsEq (linearSystem c007_A c007_O) x y :=
  replaySource_all_words c007_A c007_O c007_evidence c007_result c007_checked_data x y
theorem c007_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c007_R) c007_R) :
    taggedRealize (linearSystem c007_A c007_O) (guardedCodeFormula c007_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c007_A c007_O) :=
  replaySource_standard_formula c007_A c007_O c007_evidence c007_result c007_checked_data e
abbrev c008_R := ZMod 9
def c008_A : Fin 2 → Mat c008_R 6 6 := ![![![6, 1, 1, 2, 4, 0], ![7, 7, 3, 2, 2, 3], ![4, 0, 4, 5, 8, 6], ![7, 8, 3, 8, 2, 4], ![2, 8, 4, 3, 6, 1], ![3, 5, 1, 5, 6, 0]], ![![3, 6, 2, 3, 2, 3], ![7, 2, 2, 3, 5, 3], ![6, 8, 0, 1, 2, 4], ![0, 2, 7, 4, 5, 0], ![0, 8, 7, 2, 2, 1], ![0, 4, 5, 7, 1, 8]]]
def c008_O : Mat c008_R 1 6 := ![![5, 7, 0, 4, 3, 7]]
def c008_evidence : List (Evidence c008_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![4, 1, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [5, 5],
  .combination [1, 1]]
def c008_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c008_checked_data : replaySource c008_A c008_O c008_evidence = some c008_result := by decide +kernel
theorem c008_reference_result :
    finitePrimeDiscover 3 2 6 (fun a => rowRight (c008_A a)) c008_O = some c008_result :=
  replaySource_reference 3 2 6 (by decide +kernel) c008_A c008_O c008_evidence c008_result c008_checked_data
theorem c008_all_words (x y : Fin 6 → c008_R) :
    CodeEqual (linearSystem c008_A c008_O) c008_result x y ↔ ObsEq (linearSystem c008_A c008_O) x y :=
  replaySource_all_words c008_A c008_O c008_evidence c008_result c008_checked_data x y
theorem c008_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c008_R) c008_R) :
    taggedRealize (linearSystem c008_A c008_O) (guardedCodeFormula c008_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c008_A c008_O) :=
  replaySource_standard_formula c008_A c008_O c008_evidence c008_result c008_checked_data e
abbrev c009_R := ZMod 27
def c009_A : Fin 2 → Mat c009_R 4 4 := ![![![6, 5, 10, 1], ![22, 10, 26, 13], ![0, 15, 1, 15], ![20, 12, 4, 24]], ![![12, 0, 10, 12], ![7, 16, 7, 17], ![0, 12, 11, 21], ![26, 12, 23, 8]]]
def c009_O : Mat c009_R 1 4 := ![![18, 12, 1, 21]]
def c009_evidence : List (Evidence c009_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![0, 1, 15, 0]),
  .combination [2, 0],
  .combination [26, 2],
  .combination [1, 1]]
def c009_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c009_checked_data : replaySource c009_A c009_O c009_evidence = some c009_result := by decide +kernel
theorem c009_reference_result :
    finitePrimeDiscover 3 3 4 (fun a => rowRight (c009_A a)) c009_O = some c009_result :=
  replaySource_reference 3 3 4 (by decide +kernel) c009_A c009_O c009_evidence c009_result c009_checked_data
theorem c009_all_words (x y : Fin 4 → c009_R) :
    CodeEqual (linearSystem c009_A c009_O) c009_result x y ↔ ObsEq (linearSystem c009_A c009_O) x y :=
  replaySource_all_words c009_A c009_O c009_evidence c009_result c009_checked_data x y
theorem c009_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c009_R) c009_R) :
    taggedRealize (linearSystem c009_A c009_O) (guardedCodeFormula c009_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c009_A c009_O) :=
  replaySource_standard_formula c009_A c009_O c009_evidence c009_result c009_checked_data e
abbrev c010_R := ZMod 27
def c010_A : Fin 2 → Mat c010_R 6 6 := ![![![0, 8, 10, 19, 2, 8], ![23, 24, 3, 15, 20, 1], ![1, 2, 13, 13, 24, 25], ![13, 26, 0, 17, 24, 9], ![5, 20, 20, 2, 9, 25], ![12, 0, 23, 14, 0, 14]], ![![19, 17, 1, 22, 13, 1], ![25, 22, 23, 10, 26, 11], ![26, 7, 18, 16, 26, 20], ![8, 17, 25, 25, 24, 1], ![14, 3, 22, 20, 0, 16], ![10, 12, 14, 24, 1, 17]]]
def c010_O : Mat c010_R 1 6 := ![![24, 17, 7, 14, 13, 23]]
def c010_evidence : List (Evidence c010_R 6) := [
  .separation (![1, 0, 0, 0, 0, 0]),
  .separation (![1, 24, 0, 0, 0, 0]),
  .combination [2, 0],
  .combination [17, 11],
  .combination [1, 1]]
def c010_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c010_checked_data : replaySource c010_A c010_O c010_evidence = some c010_result := by decide +kernel
theorem c010_reference_result :
    finitePrimeDiscover 3 3 6 (fun a => rowRight (c010_A a)) c010_O = some c010_result :=
  replaySource_reference 3 3 6 (by decide +kernel) c010_A c010_O c010_evidence c010_result c010_checked_data
theorem c010_all_words (x y : Fin 6 → c010_R) :
    CodeEqual (linearSystem c010_A c010_O) c010_result x y ↔ ObsEq (linearSystem c010_A c010_O) x y :=
  replaySource_all_words c010_A c010_O c010_evidence c010_result c010_checked_data x y
theorem c010_standard_definition (e : Fin 2 → TaggedCarrier (Fin 6 → c010_R) c010_R) :
    taggedRealize (linearSystem c010_A c010_O) (guardedCodeFormula c010_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c010_A c010_O) :=
  replaySource_standard_formula c010_A c010_O c010_evidence c010_result c010_checked_data e
abbrev c011_R := ZMod 243
def c011_A : Fin 2 → Mat c011_R 4 4 := ![![![199, 37, 95, 215], ![58, 147, 109, 227], ![74, 21, 172, 53], ![154, 128, 52, 81]], ![![51, 210, 126, 119], ![71, 171, 220, 167], ![148, 158, 173, 93], ![210, 19, 62, 104]]]
def c011_O : Mat c011_R 1 4 := ![![202, 236, 238, 71]]
def c011_evidence : List (Evidence c011_R 4) := [
  .separation (![1, 0, 0, 0]),
  .separation (![148, 1, 0, 0]),
  .combination [2, 0],
  .combination [161, 83],
  .combination [1, 1]]
def c011_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c011_checked_data : replaySource c011_A c011_O c011_evidence = some c011_result := by decide +kernel
theorem c011_reference_result :
    finitePrimeDiscover 3 5 4 (fun a => rowRight (c011_A a)) c011_O = some c011_result :=
  replaySource_reference 3 5 4 (by decide +kernel) c011_A c011_O c011_evidence c011_result c011_checked_data
theorem c011_all_words (x y : Fin 4 → c011_R) :
    CodeEqual (linearSystem c011_A c011_O) c011_result x y ↔ ObsEq (linearSystem c011_A c011_O) x y :=
  replaySource_all_words c011_A c011_O c011_evidence c011_result c011_checked_data x y
theorem c011_standard_definition (e : Fin 2 → TaggedCarrier (Fin 4 → c011_R) c011_R) :
    taggedRealize (linearSystem c011_A c011_O) (guardedCodeFormula c011_result) e ↔
      e ∈ taggedBehaviorSet (linearSystem c011_A c011_O) :=
  replaySource_standard_formula c011_A c011_O c011_evidence c011_result c011_checked_data e
end Komorebi.Discovery.CheckedData.CheckedBatch00
