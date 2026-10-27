module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case183
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 5 5 := ![![![7, 24, 19, 15, 9], ![12, 29, 18, 19, 3], ![29, 5, 29, 29, 27], ![10, 15, 30, 16, 8], ![31, 20, 23, 25, 3]]]
def O : Mat R 1 5 := ![![15, 1, 30, 24, 4]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 5 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case183
