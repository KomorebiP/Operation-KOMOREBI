module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case043
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 2 2 := ![![![6, 1], ![8, 26]], ![![1, 11], ![8, 0]]]
def O : Mat R 1 2 := ![![14, 8]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 3 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case043
