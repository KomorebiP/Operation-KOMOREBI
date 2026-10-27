module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case109
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 6 6 := ![![![224, 222, 200, 133, 150, 117], ![211, 27, 21, 16, 33, 38], ![49, 200, 26, 194, 114, 187], ![70, 139, 218, 132, 171, 192], ![238, 0, 168, 230, 229, 236], ![23, 70, 137, 144, 48, 203]], ![![90, 175, 5, 73, 67, 160], ![74, 133, 78, 68, 78, 162], ![63, 229, 178, 221, 54, 180], ![195, 221, 39, 206, 141, 168], ![64, 86, 71, 3, 86, 88], ![87, 215, 112, 35, 116, 178]]]
def O : Mat R 1 6 := ![![179, 134, 33, 180, 172, 25]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0), ([1,1], 0), ([1,0,1], 0)]
theorem computed : fastPrimeDiscover 3 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case109
