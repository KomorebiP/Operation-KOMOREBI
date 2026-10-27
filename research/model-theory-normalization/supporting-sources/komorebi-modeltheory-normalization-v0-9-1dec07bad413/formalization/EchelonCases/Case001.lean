module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case001
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^2)
def A : Fin 2 → Mat R 4 4 := ![![![3, 2, 0, 2], ![1, 2, 3, 1], ![1, 2, 1, 3], ![3, 3, 3, 0]], ![![2, 0, 0, 0], ![1, 0, 2, 1], ![2, 0, 0, 2], ![2, 3, 2, 2]]]
def O : Mat R 1 4 := ![![3, 0, 0, 0]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 2 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case001
