module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case168
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^5)
def A : Fin 1 → Mat R 4 4 := ![![![27, 28, 4, 29], ![14, 19, 14, 27], ![16, 8, 25, 27], ![3, 3, 28, 12]]]
def O : Mat R 2 4 := ![![16, 16, 16, 0], ![16, 0, 16, 0]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 2 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case168
