module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case149
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 3 3 := ![![![77, 101, 14], ![27, 120, 50], ![49, 1, 54]], ![![78, 67, 118], ![48, 117, 101], ![84, 92, 110]], ![![27, 38, 37], ![68, 75, 63], ![77, 49, 18]]]
def O : Mat R 1 3 := ![![96, 51, 95]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 3 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case149
