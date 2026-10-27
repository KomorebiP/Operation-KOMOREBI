module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case160
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 4 4 := ![![![4, 3, 3, 8], ![5, 2, 0, 6], ![4, 8, 3, 3], ![3, 0, 1, 0]], ![![0, 5, 4, 6], ![3, 3, 7, 5], ![0, 8, 7, 4], ![5, 0, 7, 6]]]
def O : Mat R 2 4 := ![![5, 5, 3, 2], ![3, 8, 2, 6]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1)]
theorem computed : fastPrimeDiscover 3 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case160
