module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case018
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 2 → Mat R 6 6 := ![![![2782, 2556, 2688, 2508, 140, 2737], ![1694, 794, 2974, 1322, 2897, 1181], ![1768, 1733, 862, 603, 1549, 373], ![1794, 2608, 1809, 253, 1036, 1130], ![2129, 2543, 2842, 1023, 814, 104], ![1453, 1043, 2716, 43, 2408, 313]], ![![2022, 2885, 504, 683, 135, 177], ![1542, 1644, 963, 2260, 966, 741], ![142, 1551, 2273, 1017, 819, 1891], ![2644, 10, 1040, 2822, 2981, 476], ![2226, 725, 2070, 2845, 702, 2323], ![3077, 2131, 1181, 111, 2953, 64]]]
def O : Mat R 1 6 := ![![784, 269, 276, 794, 137, 1916]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case018
