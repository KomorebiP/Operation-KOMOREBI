module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case070
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 4 4 := ![![![4, 2, 3, 1], ![0, 2, 3, 5], ![0, 4, 1, 5], ![3, 2, 2, 3]], ![![6, 7, 4, 4], ![3, 4, 5, 3], ![6, 8, 3, 4], ![5, 4, 3, 6]]]
def O : Mat R 2 4 := ![![3, 6, 3, 3], ![3, 0, 3, 3]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 3 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case070
