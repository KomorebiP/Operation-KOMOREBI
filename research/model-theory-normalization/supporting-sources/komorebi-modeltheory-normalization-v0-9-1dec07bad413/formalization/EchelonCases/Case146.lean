module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case146
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 3 3 := ![![![9, 0, 3], ![10, 13, 19], ![8, 19, 2]], ![![0, 24, 18], ![3, 17, 7], ![10, 10, 22]], ![![24, 22, 21], ![8, 14, 20], ![5, 8, 0]]]
def O : Mat R 2 3 := ![![2, 6, 5], ![9, 1, 7]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 5 2 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case146
