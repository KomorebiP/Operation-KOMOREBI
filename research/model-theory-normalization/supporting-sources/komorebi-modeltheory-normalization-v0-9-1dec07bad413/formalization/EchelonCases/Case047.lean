module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case047
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 2 2 := ![![![200, 67], ![241, 486]], ![![100, 72], ![366, 595]], ![![613, 261], ![168, 390]]]
def O : Mat R 1 2 := ![![0, 0]]
def result : List (Test 3 1) := []
theorem computed : fastPrimeDiscover 5 4 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case047
