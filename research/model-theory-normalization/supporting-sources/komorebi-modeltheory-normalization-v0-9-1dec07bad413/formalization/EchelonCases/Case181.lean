module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case181
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 5 5 := ![![![67, 35, 20, 56, 25], ![1, 1, 58, 54, 33], ![42, 48, 80, 17, 7], ![19, 54, 20, 20, 60], ![39, 2, 29, 55, 65]], ![![11, 57, 23, 51, 3], ![23, 77, 48, 66, 33], ![11, 4, 13, 43, 50], ![8, 0, 66, 28, 26], ![21, 42, 48, 55, 21]]]
def O : Mat R 1 5 := ![![30, 60, 25, 52, 17]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0)]
theorem computed : fastPrimeDiscover 3 4 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case181
