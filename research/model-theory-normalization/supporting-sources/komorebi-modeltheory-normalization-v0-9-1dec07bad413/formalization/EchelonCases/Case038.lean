module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case038
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^1)
def A : Fin 3 → Mat R 2 2 := ![![![4, 2], ![0, 3]], ![![1, 2], ![2, 3]], ![![0, 0], ![3, 0]]]
def O : Mat R 2 2 := ![![2, 2], ![2, 4]]
def result : List (Test 3 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 5 1 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case038
