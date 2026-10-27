module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case040
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 2 2 := ![![![8, 0], ![6, 2]], ![![7, 3], ![5, 5]]]
def O : Mat R 2 2 := ![![6, 1], ![5, 5]]
def result : List (Test 2 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 3 2 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case040
