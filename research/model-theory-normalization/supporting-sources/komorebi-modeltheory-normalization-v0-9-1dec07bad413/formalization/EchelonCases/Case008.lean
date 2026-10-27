module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case008
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 6 6 := ![![![6, 1, 1, 2, 4, 0], ![7, 7, 3, 2, 2, 3], ![4, 0, 4, 5, 8, 6], ![7, 8, 3, 8, 2, 4], ![2, 8, 4, 3, 6, 1], ![3, 5, 1, 5, 6, 0]], ![![3, 6, 2, 3, 2, 3], ![7, 2, 2, 3, 5, 3], ![6, 8, 0, 1, 2, 4], ![0, 2, 7, 4, 5, 0], ![0, 8, 7, 2, 2, 1], ![0, 4, 5, 7, 1, 8]]]
def O : Mat R 1 6 := ![![5, 7, 0, 4, 3, 7]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 2 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case008
