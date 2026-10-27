module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case095
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 5 5 := ![![![2277, 1422, 1294, 646, 2433], ![2328, 158, 2137, 1258, 220], ![2566, 35, 2691, 704, 653], ![1372, 1235, 1365, 1613, 1122], ![3069, 2726, 2491, 985, 238]], ![![1049, 2380, 2211, 396, 1852], ![2244, 1796, 2669, 191, 2187], ![2182, 868, 2844, 2850, 1365], ![2060, 246, 2826, 889, 2211], ![2322, 2013, 405, 2041, 3073]], ![![1533, 460, 2443, 2423, 485], ![3028, 2990, 2875, 2341, 629], ![835, 1611, 561, 347, 1391], ![1471, 3055, 1398, 554, 663], ![600, 1904, 517, 206, 847]]]
def O : Mat R 1 5 := ![![1842, 2605, 1237, 1803, 619]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 5 5 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case095
