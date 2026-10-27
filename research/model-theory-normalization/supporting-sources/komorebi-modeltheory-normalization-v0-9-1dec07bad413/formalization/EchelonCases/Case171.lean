module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case171
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^1)
def A : Fin 1 → Mat R 5 5 := ![![![0, 0, 0, 0, 1], ![0, 0, 0, 0, 1], ![0, 1, 1, 1, 1], ![0, 0, 0, 1, 0], ![1, 1, 0, 0, 0]]]
def O : Mat R 1 5 := ![![1, 1, 1, 1, 1]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 1 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case171
