module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case143
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^1)
def A : Fin 3 → Mat R 3 3 := ![![![3, 0, 3], ![0, 1, 4], ![3, 3, 4]], ![![0, 0, 4], ![4, 4, 2], ![0, 4, 4]], ![![2, 1, 4], ![0, 1, 1], ![0, 3, 0]]]
def O : Mat R 1 3 := ![![2, 4, 1]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 1 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case143
