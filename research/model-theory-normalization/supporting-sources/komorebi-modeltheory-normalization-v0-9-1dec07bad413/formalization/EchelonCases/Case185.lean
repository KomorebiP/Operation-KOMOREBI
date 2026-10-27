module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case185
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 5 5 := ![![![1331, 1876, 1173, 1684, 1937], ![556, 1499, 2714, 2283, 447], ![2803, 664, 2344, 1296, 1713], ![1422, 841, 2661, 2983, 3011], ![340, 110, 1368, 2398, 1549]], ![![697, 1148, 1073, 245, 517], ![26, 521, 2207, 1239, 2122], ![360, 1178, 355, 1939, 2263], ![1484, 2820, 1204, 2834, 2234], ![2608, 78, 445, 267, 2914]], ![![1649, 1259, 339, 2615, 1617], ![2869, 2745, 1957, 2747, 870], ![2567, 2842, 1321, 2954, 1983], ![2180, 2801, 2172, 2718, 1193], ![2544, 1971, 1024, 1694, 839]]]
def O : Mat R 1 5 := ![![1490, 937, 878, 624, 1892]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 5 5 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case185
