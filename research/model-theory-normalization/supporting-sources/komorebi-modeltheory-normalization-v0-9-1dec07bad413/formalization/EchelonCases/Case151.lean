module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case151
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 3 3 := ![![![16, 31, 53], ![25, 49, 2], ![47, 75, 50]], ![![9, 31, 44], ![80, 80, 67], ![11, 26, 6]]]
def O : Mat R 1 3 := ![![0, 0, 0]]
def result : List (Test 2 1) := []
theorem computed : fastPrimeDiscover 3 4 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case151
