module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case003
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 2 → Mat R 4 4 := ![![![4, 1, 2, 5], ![7, 6, 1, 2], ![3, 5, 4, 0], ![4, 2, 4, 3]], ![![5, 7, 1, 2], ![1, 6, 7, 0], ![7, 5, 4, 2], ![0, 4, 2, 2]]]
def O : Mat R 1 4 := ![![2, 0, 6, 5]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 2 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case003
