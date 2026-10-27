module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case065
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 3 3 := ![![![2173, 2544, 1397], ![1021, 486, 1535], ![1572, 361, 2817]], ![![2288, 2418, 2357], ![2124, 1439, 652], ![718, 1107, 2369]], ![![2742, 560, 1777], ![1221, 571, 2366], ![20, 2849, 1531]]]
def O : Mat R 1 3 := ![![2434, 1545, 60]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 5 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case065
