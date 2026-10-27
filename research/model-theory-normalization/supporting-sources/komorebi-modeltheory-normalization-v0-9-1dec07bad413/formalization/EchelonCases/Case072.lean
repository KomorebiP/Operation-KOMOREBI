module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case072
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 4 4 := ![![![1, 7, 6, 4], ![7, 6, 3, 3], ![3, 4, 1, 7], ![7, 1, 1, 4]]]
def O : Mat R 2 4 := ![![6, 3, 3, 5], ![4, 3, 3, 1]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0)]
theorem computed : fastPrimeDiscover 2 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case072
