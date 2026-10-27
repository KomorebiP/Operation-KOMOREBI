module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case100
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 6 6 := ![![![7, 6, 7, 5, 4, 4], ![2, 4, 4, 7, 8, 1], ![2, 4, 1, 3, 2, 4], ![5, 5, 4, 4, 2, 6], ![2, 7, 2, 2, 6, 1], ![1, 0, 4, 7, 7, 3]], ![![0, 6, 2, 0, 0, 2], ![0, 3, 7, 8, 1, 3], ![5, 0, 3, 8, 0, 5], ![7, 7, 3, 1, 5, 7], ![4, 6, 7, 4, 1, 4], ![7, 7, 3, 5, 2, 0]]]
def O : Mat R 2 6 := ![![2, 6, 4, 0, 3, 4], ![6, 6, 3, 3, 5, 2]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([0,0], 0)]
theorem computed : fastPrimeDiscover 3 2 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case100
