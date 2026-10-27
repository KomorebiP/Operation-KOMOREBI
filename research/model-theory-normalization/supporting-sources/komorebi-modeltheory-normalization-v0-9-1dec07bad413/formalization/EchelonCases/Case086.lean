module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case086
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 5 5 := ![![![5, 8, 19, 5, 3], ![22, 0, 0, 17, 0], ![15, 1, 16, 11, 14], ![13, 7, 4, 19, 1], ![0, 3, 8, 13, 2]], ![![12, 3, 11, 4, 10], ![8, 19, 3, 22, 14], ![4, 8, 3, 8, 21], ![2, 14, 19, 9, 1], ![24, 18, 7, 19, 0]], ![![23, 21, 23, 0, 5], ![21, 23, 17, 13, 18], ![13, 23, 9, 9, 11], ![10, 1, 15, 8, 18], ![9, 17, 15, 24, 15]]]
def O : Mat R 2 5 := ![![0, 0, 0, 0, 0], ![0, 0, 0, 0, 0]]
def result : List (Test 3 2) := []
theorem computed : fastPrimeDiscover 5 2 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case086
