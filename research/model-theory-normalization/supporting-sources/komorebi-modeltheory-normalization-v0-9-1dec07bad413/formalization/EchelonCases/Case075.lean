module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case075
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 4 4 := ![![![15, 1, 15, 6], ![8, 4, 6, 15], ![4, 14, 7, 12], ![4, 10, 11, 3]]]
def O : Mat R 1 4 := ![![3, 14, 6, 12]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 4 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case075
