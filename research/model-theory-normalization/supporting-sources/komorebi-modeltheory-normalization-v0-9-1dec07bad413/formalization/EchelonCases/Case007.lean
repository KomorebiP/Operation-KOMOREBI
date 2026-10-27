module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case007
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 4 4 := ![![![0, 0, 7, 6], ![8, 4, 5, 8], ![8, 3, 6, 5], ![7, 6, 1, 2]], ![![5, 0, 8, 0], ![3, 5, 4, 1], ![3, 6, 8, 6], ![6, 6, 5, 7]]]
def O : Mat R 1 4 := ![![6, 2, 0, 5]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case007
