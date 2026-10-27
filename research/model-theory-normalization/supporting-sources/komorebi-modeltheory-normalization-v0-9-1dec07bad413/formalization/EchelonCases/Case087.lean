module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case087
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^3)
def A : Fin 1 → Mat R 5 5 := ![![![6, 0, 4, 6, 1], ![7, 3, 7, 1, 7], ![5, 4, 1, 0, 4], ![1, 0, 1, 7, 7], ![1, 1, 2, 5, 0]]]
def O : Mat R 1 5 := ![![4, 1, 6, 7, 2]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 3 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case087
