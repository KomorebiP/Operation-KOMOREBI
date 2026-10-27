module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case063
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 3 3 := ![![![13, 29, 18], ![0, 8, 25], ![5, 2, 10]]]
def O : Mat R 1 3 := ![![16, 16, 0]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 2 5 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case063
