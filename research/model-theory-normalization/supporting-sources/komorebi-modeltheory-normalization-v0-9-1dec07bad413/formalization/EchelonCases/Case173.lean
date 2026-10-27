module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case173
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^1)
def A : Fin 3 → Mat R 5 5 := ![![![0, 2, 0, 3, 2], ![0, 2, 3, 1, 1], ![2, 3, 1, 2, 4], ![3, 0, 3, 1, 3], ![1, 2, 2, 4, 2]], ![![1, 1, 3, 0, 1], ![2, 2, 0, 3, 2], ![3, 4, 1, 4, 1], ![2, 3, 4, 1, 3], ![0, 4, 3, 1, 2]], ![![3, 2, 4, 2, 1], ![3, 0, 2, 4, 2], ![4, 1, 4, 1, 1], ![0, 3, 4, 2, 3], ![4, 2, 0, 2, 2]]]
def O : Mat R 1 5 := ![![1, 4, 0, 0, 4]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem computed : fastPrimeDiscover 5 1 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case173
