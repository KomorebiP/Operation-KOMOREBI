module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case044
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 2 2 := ![![![27, 1], ![74, 15]], ![![67, 57], ![34, 72]], ![![25, 49], ![41, 54]]]
def O : Mat R 2 2 := ![![114, 44], ![56, 15]]
def result : List (Test 3 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 5 3 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case044
