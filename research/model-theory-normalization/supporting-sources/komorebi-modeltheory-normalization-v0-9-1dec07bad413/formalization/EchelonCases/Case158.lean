module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case158
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^1)
def A : Fin 3 → Mat R 4 4 := ![![![1, 2, 3, 3], ![3, 0, 4, 4], ![0, 0, 2, 3], ![0, 4, 0, 1]], ![![0, 0, 3, 0], ![3, 4, 1, 3], ![4, 3, 4, 4], ![3, 1, 3, 0]], ![![1, 0, 3, 0], ![4, 2, 1, 2], ![3, 1, 0, 2], ![1, 3, 1, 4]]]
def O : Mat R 2 4 := ![![1, 2, 0, 3], ![0, 0, 0, 0]]
def result : List (Test 3 2) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 5 1 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case158
