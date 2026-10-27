module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case165
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 4 4 := ![![![3, 15, 3, 12], ![7, 1, 15, 6], ![15, 15, 4, 10], ![4, 11, 14, 11]]]
def O : Mat R 1 4 := ![![4, 12, 13, 5]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 4 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case165
