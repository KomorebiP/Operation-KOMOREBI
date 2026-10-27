module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case169
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 4 4 := ![![![32, 180, 15, 20], ![59, 86, 189, 61], ![134, 9, 112, 209], ![81, 1, 99, 94]], ![![177, 114, 54, 45], ![92, 125, 240, 197], ![150, 83, 136, 114], ![5, 176, 145, 7]]]
def O : Mat R 1 4 := ![![73, 8, 194, 48]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 3 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case169
