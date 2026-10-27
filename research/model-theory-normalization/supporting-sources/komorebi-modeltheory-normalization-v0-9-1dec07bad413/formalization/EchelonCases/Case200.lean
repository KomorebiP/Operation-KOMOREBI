module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case200
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 6 6 := ![![![359, 2215, 2375, 2102, 1953, 1435], ![309, 1145, 1384, 530, 1804, 2344], ![2729, 173, 2574, 1085, 1277, 771], ![66, 1152, 2718, 2419, 244, 1813], ![320, 2980, 2464, 472, 2510, 2751], ![2846, 1564, 1215, 1239, 630, 579]], ![![1627, 1438, 1488, 2392, 2593, 692], ![2659, 410, 1711, 1555, 3021, 2288], ![1281, 656, 1767, 807, 242, 664], ![2354, 166, 2721, 499, 1561, 239], ![2792, 1104, 1433, 1048, 3060, 253], ![2670, 2348, 1762, 2224, 2157, 2234]], ![![1317, 697, 2576, 644, 2240, 1708], ![2485, 2313, 2357, 1837, 1253, 462], ![1454, 1472, 3058, 1872, 1942, 2856], ![2517, 1084, 1644, 222, 183, 3085], ![1615, 562, 3105, 1042, 993, 1400], ![174, 2072, 2132, 2904, 1655, 1600]]]
def O : Mat R 2 6 := ![![2358, 1712, 158, 579, 2077, 2544], ![2315, 331, 2650, 2342, 2649, 1444]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([1], 1)]
theorem computed : fastPrimeDiscover 5 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case200
