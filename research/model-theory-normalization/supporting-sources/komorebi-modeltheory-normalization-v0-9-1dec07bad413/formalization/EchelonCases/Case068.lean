module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case068
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^1)
def A : Fin 3 → Mat R 4 4 := ![![![0, 2, 0, 0], ![3, 0, 2, 0], ![3, 3, 1, 4], ![0, 3, 3, 0]], ![![1, 0, 3, 0], ![3, 1, 4, 1], ![0, 1, 0, 1], ![1, 1, 0, 2]], ![![2, 0, 4, 0], ![0, 2, 3, 1], ![3, 4, 3, 2], ![0, 2, 3, 3]]]
def O : Mat R 2 4 := ![![3, 3, 3, 3], ![4, 4, 2, 3]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 1 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case068
