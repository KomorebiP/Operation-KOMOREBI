module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case170
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 4 4 := ![![![422, 1382, 2161, 2712], ![1903, 1948, 1425, 397], ![1316, 489, 2493, 1136], ![2740, 1710, 724, 569]], ![![2544, 761, 2548, 1006], ![700, 2335, 243, 1972], ![2007, 2783, 2393, 2029], ![1475, 435, 1958, 547]], ![![1602, 2746, 2378, 2127], ![1559, 1191, 150, 2970], ![3057, 2550, 2597, 662], ![1123, 1514, 409, 2522]]]
def O : Mat R 2 4 := ![![1426, 1137, 565, 2015], ![3043, 3060, 2509, 1388]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case170
