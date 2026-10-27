module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case088
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 5 5 := ![![![1, 18, 5, 18, 4], ![16, 24, 12, 10, 0], ![19, 8, 7, 20, 23], ![4, 9, 5, 1, 12], ![22, 23, 1, 16, 6]], ![![21, 13, 22, 10, 7], ![20, 22, 8, 19, 4], ![14, 9, 20, 8, 23], ![2, 18, 7, 1, 5], ![19, 12, 4, 11, 12]]]
def O : Mat R 2 5 := ![![6, 13, 22, 8, 3], ![12, 5, 9, 16, 22]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 3 3 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case088
