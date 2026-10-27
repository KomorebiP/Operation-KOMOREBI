module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case058
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 3 3 := ![![![23, 16, 24], ![20, 19, 17], ![11, 21, 2]], ![![26, 6, 21], ![13, 25, 16], ![3, 10, 14]]]
def O : Mat R 2 3 := ![![20, 25, 26], ![2, 15, 14]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 3 3 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case058
