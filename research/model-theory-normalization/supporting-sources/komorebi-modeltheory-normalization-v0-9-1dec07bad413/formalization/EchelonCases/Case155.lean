module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case155
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 3 3 := ![![![2481, 458, 154], ![1844, 1174, 1557], ![498, 1764, 589]], ![![1001, 1571, 2305], ![1475, 48, 1870], ![1439, 2881, 1601]], ![![2436, 873, 1668], ![405, 1803, 791], ![2667, 589, 1326]]]
def O : Mat R 1 3 := ![![2013, 514, 992]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 5 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case155
