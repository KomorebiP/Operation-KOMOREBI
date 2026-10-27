module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case016
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 2 → Mat R 6 6 := ![![![52, 61, 40, 58, 2, 13], ![35, 79, 5, 53, 52, 31], ![41, 37, 72, 7, 66, 36], ![98, 108, 112, 116, 107, 124], ![117, 41, 102, 91, 18, 27], ![51, 31, 33, 57, 18, 50]], ![![119, 19, 12, 50, 121, 34], ![38, 48, 16, 13, 39, 30], ![101, 6, 114, 106, 49, 58], ![106, 44, 83, 111, 5, 102], ![93, 74, 92, 28, 29, 1], ![120, 61, 7, 104, 58, 80]]]
def O : Mat R 1 6 := ![![68, 57, 19, 124, 65, 71]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case016
