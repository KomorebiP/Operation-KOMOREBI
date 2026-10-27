module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case099
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^2)
def A : Fin 1 → Mat R 6 6 := ![![![0, 2, 3, 2, 0, 2], ![3, 1, 3, 0, 0, 3], ![0, 2, 3, 0, 3, 1], ![3, 2, 2, 1, 2, 3], ![2, 2, 1, 2, 3, 2], ![2, 3, 0, 0, 2, 0]]]
def O : Mat R 1 6 := ![![0, 0, 0, 0, 0, 0]]
def result : List (Test 1 1) := []
theorem computed : fastPrimeDiscover 2 2 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case099
