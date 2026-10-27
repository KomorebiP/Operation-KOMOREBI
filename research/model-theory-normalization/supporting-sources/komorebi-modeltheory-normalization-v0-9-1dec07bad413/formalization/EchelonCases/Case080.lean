module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case080
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 4 4 := ![![![2781, 4, 2809, 2360], ![2840, 1576, 1793, 2417], ![2471, 666, 20, 859], ![1063, 1901, 1256, 2242]], ![![401, 2351, 497, 2498], ![246, 1266, 2326, 221], ![1341, 125, 2490, 2472], ![1753, 2328, 2560, 2227]], ![![906, 3001, 682, 563], ![11, 1251, 1314, 1325], ![1536, 2787, 1181, 2031], ![1688, 1888, 1751, 619]]]
def O : Mat R 2 4 := ![![34, 872, 752, 1288], ![2123, 3020, 2824, 1286]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case080
