module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case073
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 4 4 := ![![![22, 22, 13, 24], ![22, 0, 21, 6], ![19, 23, 2, 0], ![14, 5, 13, 14]], ![![26, 14, 3, 3], ![12, 8, 16, 16], ![9, 15, 18, 6], ![19, 20, 8, 4]]]
def O : Mat R 1 4 := ![![0, 0, 0, 0]]
def result : List (Test 2 1) := []
theorem computed : fastPrimeDiscover 3 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case073
