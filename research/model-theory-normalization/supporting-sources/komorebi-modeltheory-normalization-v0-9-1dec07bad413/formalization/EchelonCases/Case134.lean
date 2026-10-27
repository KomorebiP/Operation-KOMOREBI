module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case134
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 2 2 := ![![![117, 9], ![41, 14]], ![![20, 38], ![115, 7]], ![![68, 12], ![18, 83]]]
def O : Mat R 2 2 := ![![77, 74], ![33, 2]]
def result : List (Test 3 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 5 3 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case134
