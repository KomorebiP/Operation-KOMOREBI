module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case017
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 2 → Mat R 4 4 := ![![![1754, 2237, 1761, 2455], ![784, 2076, 1344, 294], ![2125, 336, 2000, 576], ![1445, 2441, 209, 2587]], ![![1650, 544, 2801, 2817], ![2137, 492, 1519, 1975], ![3022, 1702, 2591, 1281], ![1226, 2769, 1402, 472]]]
def O : Mat R 1 4 := ![![1034, 2592, 2787, 1425]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case017
