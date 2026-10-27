module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CheckedData.CheckedLarge
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 12000000
abbrev R := ZMod 65536
def A : Fin 2 → Mat R 8 8 := ![![![17698, 7962, 49699, 37320, 23412, 6538, 39824, 34395], ![23464, 37603, 20556, 32118, 60325, 50701, 6345, 63146], ![7061, 60025, 48800, 57289, 7901, 57423, 17450, 21611], ![57954, 1463, 43061, 61981, 12327, 24535, 55220, 20222], ![9538, 34330, 18991, 25859, 64489, 51532, 7482, 17514], ![8262, 4689, 20524, 11331, 58729, 9597, 8879, 16991], ![38245, 65480, 12079, 48575, 41217, 13059, 11905, 14025], ![40555, 32470, 51819, 35275, 34452, 61245, 54300, 32399]], ![![45667, 60993, 42044, 24680, 13027, 39737, 34859, 3988], ![10393, 29683, 38554, 51204, 39690, 4755, 35121, 61378], ![63427, 47581, 32082, 32486, 44031, 34935, 29965, 8363], ![27479, 23039, 1777, 57316, 32532, 42871, 30241, 7992], ![35244, 37369, 1342, 167, 21177, 50423, 62217, 51013], ![29874, 59333, 42924, 46108, 58455, 35340, 60778, 27268], ![52594, 11868, 27092, 9501, 44582, 25499, 5486, 41184], ![1304, 20195, 44643, 12867, 63107, 13759, 28318, 26332]]]
def O : Mat R 1 8 := ![![7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995]]
def evidence : List (Evidence R 8) := [
  .separation (![1, 0, 0, 0, 0, 0, 0, 0]),
  .separation (![1, 62136, 0, 0, 0, 0, 0, 0]),
  .combination [3, 0],
  .combination [49151, 16386],
  .combination [32766, 32773]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem checked_data : replaySource A O evidence = some result := by decide +kernel
theorem reference_result :
    finitePrimeDiscover 2 16 8 (fun a => rowRight (A a)) O = some result :=
  replaySource_reference 2 16 8 (by decide +kernel) A O evidence result checked_data
theorem all_words (x y : Fin 8 → R) :
    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=
  replaySource_all_words A O evidence result checked_data x y
theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin 8 → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  replaySource_standard_formula A O evidence result checked_data e
end Komorebi.Discovery.CheckedData.CheckedLarge
