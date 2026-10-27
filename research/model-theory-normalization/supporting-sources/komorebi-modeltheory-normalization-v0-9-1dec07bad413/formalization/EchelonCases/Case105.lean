module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case105
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 6 6 := ![![![9, 9, 11, 2, 0, 9], ![9, 14, 0, 15, 7, 12], ![12, 11, 9, 0, 12, 12], ![8, 10, 3, 6, 15, 9], ![6, 12, 4, 5, 3, 9], ![4, 2, 1, 8, 0, 2]]]
def O : Mat R 1 6 := ![![8, 8, 8, 8, 8, 8]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 4 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case105
