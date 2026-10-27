module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case061
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 3 3 := ![![![9, 78, 10], ![48, 19, 63], ![34, 28, 75]], ![![53, 1, 76], ![6, 14, 48], ![5, 18, 9]]]
def O : Mat R 1 3 := ![![76, 64, 33]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 3 4 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case061
