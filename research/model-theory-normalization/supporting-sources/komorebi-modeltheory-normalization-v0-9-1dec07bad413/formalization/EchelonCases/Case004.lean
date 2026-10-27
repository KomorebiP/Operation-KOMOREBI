module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case004
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 2 → Mat R 6 6 := ![![![1, 3, 5, 6, 1, 6], ![4, 4, 1, 2, 3, 5], ![6, 4, 6, 0, 0, 5], ![0, 3, 7, 0, 5, 3], ![0, 0, 0, 6, 3, 1], ![4, 7, 4, 2, 7, 7]], ![![3, 3, 0, 3, 0, 2], ![6, 3, 6, 5, 0, 2], ![5, 5, 6, 2, 0, 1], ![7, 1, 7, 1, 1, 4], ![2, 1, 6, 0, 7, 2], ![7, 2, 6, 5, 6, 1]]]
def O : Mat R 1 6 := ![![4, 1, 3, 4, 6, 1]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 2 3 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case004
