module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case085
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 5 5 := ![![![1, 5, 0, 8, 8], ![8, 0, 6, 3, 1], ![6, 6, 4, 4, 3], ![4, 5, 3, 8, 7], ![2, 3, 8, 6, 6]], ![![5, 6, 5, 0, 6], ![4, 3, 2, 2, 3], ![2, 7, 2, 5, 5], ![1, 4, 4, 7, 2], ![8, 7, 7, 8, 2]]]
def O : Mat R 1 5 := ![![1, 0, 2, 2, 5]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem computed : fastPrimeDiscover 3 2 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case085
