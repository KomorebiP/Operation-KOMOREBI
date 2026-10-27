module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedRandom
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev R := ZMod 125
def A : Fin 3 → Mat R 2 2 := ![![![27, 1], ![74, 15]], ![![67, 57], ![34, 72]], ![![25, 49], ![41, 54]]]
def O : Mat R 2 2 := ![![114, 44], ![56, 15]]
def evidence : List (Evidence R 2) := [
  .separation (![1, 0]),
  .separation (![4, 1]),
  .combination [21, 115],
  .combination [9, 118],
  .combination [78, 27],
  .combination [39, 21],
  .combination [13, 5],
  .combination [106, 1]]
def result : List (Test 3 2) := [([], 0), ([], 1)]
theorem checked_data : replaySource A O evidence = some result := by decide +kernel
theorem reference_result :
    finitePrimeDiscover 5 3 2 (fun a => rowRight (A a)) O = some result :=
  replaySource_reference 5 3 2 (by decide +kernel) A O evidence result checked_data
theorem all_words (x y : Fin 2 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  replaySource_all_words A O evidence result checked_data x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 2 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  replaySource_standard_formula A O evidence result checked_data e
end Komorebi.Discovery.CheckedData.CheckedRandom
