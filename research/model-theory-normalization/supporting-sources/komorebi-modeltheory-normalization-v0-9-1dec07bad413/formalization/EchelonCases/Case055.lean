module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case055
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 3 3 := ![![![5, 4, 5], ![0, 1, 5], ![7, 0, 3]], ![![3, 2, 5], ![5, 3, 3], ![4, 4, 8]]]
def O : Mat R 1 3 := ![![2, 1, 6]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 3 2 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case055
