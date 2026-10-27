module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedDelay
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev R := ZMod 16
def A : Fin 1 → Mat R 8 8 := ![![![0, 1, 0, 0, 0, 0, 0, 0], ![0, 0, 1, 0, 0, 0, 0, 0], ![0, 0, 0, 1, 0, 0, 0, 0], ![0, 0, 0, 0, 1, 0, 0, 0], ![0, 0, 0, 0, 0, 1, 0, 0], ![0, 0, 0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 0, 0, 0, 1], ![0, 0, 0, 0, 0, 0, 0, 0]]]
def O : Mat R 1 8 := ![![1, 0, 0, 0, 0, 0, 0, 0]]
def evidence : List (Evidence R 8) := [
  .separation (![1, 0, 0, 0, 0, 0, 0, 0]),
  .separation (![0, 1, 0, 0, 0, 0, 0, 0]),
  .separation (![0, 0, 1, 0, 0, 0, 0, 0]),
  .separation (![0, 0, 0, 1, 0, 0, 0, 0]),
  .separation (![0, 0, 0, 0, 1, 0, 0, 0]),
  .separation (![0, 0, 0, 0, 0, 1, 0, 0]),
  .separation (![0, 0, 0, 0, 0, 0, 1, 0]),
  .separation (![0, 0, 0, 0, 0, 0, 0, 1]),
  .combination [0, 0, 0, 0, 0, 0, 0, 0]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0), ([0,0,0,0,0,0], 0), ([0,0,0,0,0,0,0], 0)]
theorem checked_data : replaySource A O evidence = some result := by decide +kernel
theorem reference_result :
    finitePrimeDiscover 2 4 8 (fun a => rowRight (A a)) O = some result :=
  replaySource_reference 2 4 8 (by decide +kernel) A O evidence result checked_data
theorem all_words (x y : Fin 8 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  replaySource_all_words A O evidence result checked_data x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 8 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  replaySource_standard_formula A O evidence result checked_data e
end Komorebi.Discovery.CheckedData.CheckedDelay
