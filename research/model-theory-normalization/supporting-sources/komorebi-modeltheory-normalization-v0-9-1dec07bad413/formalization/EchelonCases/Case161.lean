module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case161
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 4 4 := ![![![2, 17, 14, 23], ![24, 22, 13, 7], ![21, 1, 9, 10], ![10, 13, 19, 21]], ![![8, 8, 0, 21], ![17, 7, 10, 12], ![21, 19, 8, 22], ![19, 10, 4, 24]], ![![11, 20, 8, 1], ![2, 11, 19, 0], ![10, 13, 21, 22], ![2, 3, 6, 23]]]
def O : Mat R 1 4 := ![![20, 0, 5, 5]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem computed : fastPrimeDiscover 5 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case161
