module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case156
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^1)
def A : Fin 1 → Mat R 4 4 := ![![![0, 1, 1, 0], ![1, 0, 1, 1], ![0, 1, 1, 1], ![1, 0, 1, 0]]]
def O : Mat R 2 4 := ![![1, 1, 1, 1], ![0, 1, 0, 1]]
def result : List (Test 1 2) := [([], 0), ([], 1), ([0], 1)]
theorem computed : fastPrimeDiscover 2 1 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case156
